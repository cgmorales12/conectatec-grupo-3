"""
Enrutador de Gestión Documental y CRUD de Manuales RAG - Personal TIC
Permite listar, visualizar, crear, editar y eliminar manuales técnicos .md en data/raw/
Cumple: Control de Acceso RBAC, Mitigación de Path Traversal (OWASP) y Conversor de Documentos.
Autor: Luis Fernando Ribera & Amalia Geoconda Iguasnia
"""

import os
import re
import glob
import base64
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas import (
    ManualItemOut,
    ListaManualesOut,
    ManualDetalleOut,
    GuardarManualIn,
    ConvertirDocIn,
    ResultadoConversionOut
)
from app.services.auth import obtener_usuario_autenticado
from app.services.conversor import convertir_documento

router = APIRouter(prefix="/v1/admin", tags=["Gestión Base de Conocimiento (TIC)"])

DIRECTORIO_RAW = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw"))


def _validar_y_sanitizar_archivo(nombre_archivo: str) -> str:
    """Previene vulnerabilidades de salto de directorio (Path Traversal CWE-22)."""
    archivo_limpio = os.path.basename(nombre_archivo.strip())
    if not archivo_limpio.endswith(".md"):
        archivo_limpio += ".md"
    # Solo caracteres seguros
    if not re.match(r"^[a-zA-Z0-9_\-\.]+\.md$", archivo_limpio):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de archivo contiene caracteres no permitidos. Use solo letras, números, guiones y punto."
        )
    return archivo_limpio


def _parsear_metadatos_manual(ruta_completa: str) -> dict:
    """Extrae metadatos esenciales de la cabecera de un archivo Markdown."""
    nombre_archivo = os.path.basename(ruta_completa)
    tamano = os.path.getsize(ruta_completa)
    mtime = os.path.getmtime(ruta_completa)
    fecha_mod = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    doc_id = "DOC-XX"
    titulo = nombre_archivo
    categoria = "General / Procedimientos"
    vigencia = "2026"
    
    match_id = re.match(r"(DOC-\d+)", nombre_archivo, re.IGNORECASE)
    if match_id:
        doc_id = match_id.group(1).upper()
        
    try:
        with open(ruta_completa, "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(15):
                linea = f.readline()
                if not linea:
                    break
                linea = linea.strip()
                if linea.startswith("# "):
                    titulo = re.sub(r"^#\s*(?:DOC-\d+[:\s-]*)?", "", linea).strip()
                elif "categor" in linea.lower() and ":" in linea:
                    categoria = linea.split(":", 1)[1].strip("*_ ")
                elif ("vigencia" in linea.lower() or "versión" in linea.lower()) and ":" in linea:
                    vigencia = linea.split(":", 1)[1].strip("*_ ")
    except Exception:
        pass
        
    return {
        "archivo": nombre_archivo,
        "documento_id": doc_id,
        "titulo": titulo,
        "categoria": categoria,
        "vigencia": vigencia,
        "tamano_bytes": tamano,
        "fecha_modificacion": fecha_mod
    }


@router.get(
    "/manuales",
    response_model=ListaManualesOut,
    status_code=status.HTTP_200_OK,
    summary="Lista todos los manuales Markdown de la base de conocimiento (Solo TIC)"
)
def listar_manuales_rag(usuario_tic: dict = Depends(obtener_usuario_autenticado)):
    """Retorna el inventario de los manuales técnicos oficiales almacenados en data/raw/."""
    os.makedirs(DIRECTORIO_RAW, exist_ok=True)
    patron = os.path.join(DIRECTORIO_RAW, "*.md")
    archivos = sorted(glob.glob(patron))
    
    items: List[ManualItemOut] = []
    for a in archivos:
        # Excluir README si no es un manual de diagnóstico
        if os.path.basename(a).lower() == "readme.md":
            continue
        meta = _parsear_metadatos_manual(a)
        items.append(ManualItemOut(**meta))
        
    return ListaManualesOut(total=len(items), manuales=items)


@router.get(
    "/manuales/{nombre_archivo}",
    response_model=ManualDetalleOut,
    status_code=status.HTTP_200_OK,
    summary="Obtiene el contenido completo de un manual Markdown (Solo TIC)"
)
def obtener_detalle_manual(
    nombre_archivo: str,
    usuario_tic: dict = Depends(obtener_usuario_autenticado)
):
    """Retorna el contenido en texto plano Markdown de un manual para visualización o edición."""
    archivo_seguro = _validar_y_sanitizar_archivo(nombre_archivo)
    ruta_completa = os.path.join(DIRECTORIO_RAW, archivo_seguro)
    
    if not os.path.isfile(ruta_completa):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El manual '{archivo_seguro}' no existe en data/raw/."
        )
        
    meta = _parsear_metadatos_manual(ruta_completa)
    with open(ruta_completa, "r", encoding="utf-8") as f:
        contenido = f.read()
        
    return ManualDetalleOut(
        archivo=archivo_seguro,
        documento_id=meta["documento_id"],
        titulo=meta["titulo"],
        contenido_markdown=contenido
    )


@router.post(
    "/manuales",
    response_model=ManualDetalleOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuevo manual técnico en data/raw/ (Solo TIC)"
)
def crear_manual(
    payload: GuardarManualIn,
    usuario_tic: dict = Depends(obtener_usuario_autenticado)
):
    """Crea un nuevo archivo .md en la base de conocimiento oficial."""
    archivo_seguro = _validar_y_sanitizar_archivo(payload.archivo)
    ruta_completa = os.path.join(DIRECTORIO_RAW, archivo_seguro)
    
    if os.path.exists(ruta_completa) and not payload.sobrescribir:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El manual '{archivo_seguro}' ya existe. Active 'sobrescribir' si desea reemplazarlo."
        )
        
    with open(ruta_completa, "w", encoding="utf-8") as f:
        f.write(payload.contenido_markdown)
        
    meta = _parsear_metadatos_manual(ruta_completa)
    return ManualDetalleOut(
        archivo=archivo_seguro,
        documento_id=meta["documento_id"],
        titulo=meta["titulo"],
        contenido_markdown=payload.contenido_markdown
    )


@router.put(
    "/manuales/{nombre_archivo}",
    response_model=ManualDetalleOut,
    status_code=status.HTTP_200_OK,
    summary="Actualiza el contenido de un manual existente (Solo TIC)"
)
def actualizar_manual(
    nombre_archivo: str,
    payload: GuardarManualIn,
    usuario_tic: dict = Depends(obtener_usuario_autenticado)
):
    """Modifica el contenido Markdown de un procedimiento técnico existente."""
    archivo_seguro = _validar_y_sanitizar_archivo(nombre_archivo)
    ruta_completa = os.path.join(DIRECTORIO_RAW, archivo_seguro)
    
    if not os.path.isfile(ruta_completa):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El manual '{archivo_seguro}' no existe en data/raw/."
        )
        
    with open(ruta_completa, "w", encoding="utf-8") as f:
        f.write(payload.contenido_markdown)
        
    meta = _parsear_metadatos_manual(ruta_completa)
    return ManualDetalleOut(
        archivo=archivo_seguro,
        documento_id=meta["documento_id"],
        titulo=meta["titulo"],
        contenido_markdown=payload.contenido_markdown
    )


@router.delete(
    "/manuales/{nombre_archivo}",
    status_code=status.HTTP_200_OK,
    summary="Elimina un manual técnico de data/raw/ (Solo TIC)"
)
def eliminar_manual(
    nombre_archivo: str,
    usuario_tic: dict = Depends(obtener_usuario_autenticado)
):
    """Elimina permanentemente un manual técnico de la base de conocimiento."""
    archivo_seguro = _validar_y_sanitizar_archivo(nombre_archivo)
    ruta_completa = os.path.join(DIRECTORIO_RAW, archivo_seguro)
    
    if not os.path.isfile(ruta_completa):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El manual '{archivo_seguro}' no existe en data/raw/."
        )
        
    os.remove(ruta_completa)
    return {
        "status": "ok",
        "mensaje": f"Manual '{archivo_seguro}' eliminado exitosamente de la base de conocimiento.",
        "eliminado_por": usuario_tic["usuario"]
    }


@router.post(
    "/convertir-documento",
    response_model=ResultadoConversionOut,
    status_code=status.HTTP_200_OK,
    summary="Convierte un archivo Word o PDF a Markdown RAG en caliente (Solo TIC)"
)
def convertir_documento_web(
    payload: ConvertirDocIn,
    usuario_tic: dict = Depends(obtener_usuario_autenticado)
):
    """
    Recibe un documento Word (.docx) o PDF en Base64, extrae su texto estructurado,
    genera las secciones de procedimiento y pasos compatibles con el RAG, y opcionalmente
    lo guarda directamente en data/raw/.
    """
    try:
        contenido_bytes = base64.b64decode(payload.contenido_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El contenido Base64 del documento no es válido: {str(e)}"
        )
        
    ext = os.path.splitext(payload.nombre_archivo)[1].lower()
    if ext not in [".docx", ".pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no admitido '{ext}'. Solo se permite convertir archivos .docx y .pdf."
        )
        
    try:
        resultado = convertir_documento(
            contenido_bytes,
            payload.nombre_archivo,
            guardar_en_raw=payload.guardar_directo
        )
        
        msg = "Documento convertido exitosamente a Markdown."
        if payload.guardar_directo:
            msg += f" Guardado en data/raw/{resultado['nombre_archivo_md']}"
            
        return ResultadoConversionOut(
            nombre_archivo_md=resultado["nombre_archivo_md"],
            documento_id=resultado["documento_id"],
            titulo=resultado["titulo"],
            contenido_markdown=resultado["contenido_markdown"],
            guardado_en_raw=resultado["guardado_en_raw"],
            mensaje=msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el procesamiento del documento: {str(e)}"
        )
