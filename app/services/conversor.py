"""
Servicio de Conversión Inteligente de Documentos (Word / PDF -> Markdown RAG)
Cumple: Conversión estructurada con identificación de pasos y metadatos para el motor RAG.
Autor: Luis Fernando Ribera & Amalia Geoconda Iguasnia
"""

import os
import re
import io
import glob
from typing import Tuple, Dict, Any, Optional

DIRECTORIO_RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")


def obtener_siguiente_codigo_doc() -> str:
    """Calcula el siguiente identificador correlativo DOC-XX analizando data/raw/."""
    os.makedirs(DIRECTORIO_RAW, exist_ok=True)
    archivos = glob.glob(os.path.join(DIRECTORIO_RAW, "DOC-*.md"))
    numeros = []
    for a in archivos:
        nombre = os.path.basename(a)
        m = re.match(r"DOC-(\d+)", nombre, re.IGNORECASE)
        if m:
            numeros.append(int(m.group(1)))
    
    siguiente = max(numeros) + 1 if numeros else 1
    return f"DOC-{siguiente:02d}"


def extraer_texto_docx(stream_o_ruta) -> str:
    """Extrae texto y tablas desde un archivo Word (.docx) preservando estructura."""
    import docx
    doc = docx.Document(stream_o_ruta)
    lineas = []
    
    for elemento in doc.element.body:
        # Párrafos
        if elemento.tag.endswith('p'):
            p = docx.text.paragraph.Paragraph(elemento, doc)
            texto = p.text.strip()
            if not texto:
                continue
            estilo = p.style.name.lower() if p.style else ""
            if "heading 1" in estilo:
                lineas.append(f"# {texto}")
            elif "heading 2" in estilo:
                lineas.append(f"## {texto}")
            elif "heading 3" in estilo:
                lineas.append(f"### {texto}")
            else:
                lineas.append(texto)
        # Tablas
        elif elemento.tag.endswith('tbl'):
            t = docx.table.Table(elemento, doc)
            if t.rows:
                filas = []
                for row in t.rows:
                    celdas = [c.text.strip().replace("\n", " ") for c in row.cells]
                    filas.append("| " + " | ".join(celdas) + " |")
                if filas:
                    lineas.append("")
                    lineas.append(filas[0])
                    num_cols = len(t.rows[0].cells)
                    lineas.append("| " + " | ".join(["---"] * num_cols) + " |")
                    for fila in filas[1:]:
                        lineas.append(fila)
                    lineas.append("")
    
    return "\n\n".join(lineas)


def extraer_texto_pdf(stream_o_ruta) -> str:
    """Extrae texto estructurado desde un archivo PDF usando pypdf."""
    from pypdf import PdfReader
    lector = PdfReader(stream_o_ruta)
    texto_completo = []
    for pagina in lector.pages:
        t = pagina.extract_text()
        if t:
            texto_completo.append(t)
    return "\n\n".join(texto_completo)


def estructurar_a_markdown_rag(texto_crudo: str, nombre_original: str) -> Tuple[str, str, str]:
    """
    Toma el texto extraído y lo normaliza al formato canónico de la base de conocimiento RAG:
    # DOC-XX: Título
    **Categoría:** ...
    ## Descripción General
    ## Procedimiento Operativo Paso a Paso
    ### Paso 1: ...
    Retorna: (doc_id, titulo, contenido_markdown)
    """
    lineas = [l.strip() for l in texto_crudo.splitlines() if l.strip()]
    
    # 1. Detectar o asignar Document ID
    match_doc = re.search(r"\b(DOC-\d+)\b", texto_crudo, re.IGNORECASE) or re.search(r"\b(DOC-\d+)\b", nombre_original, re.IGNORECASE)
    doc_id = match_doc.group(1).upper() if match_doc else obtener_siguiente_codigo_doc()
    
    # 2. Detectar Título
    titulo_candidato = ""
    for l in lineas[:5]:
        limpia = re.sub(r"^#+\s*", "", l)
        limpia = re.sub(r"^DOC-\d+[:\s-]*", "", limpia, flags=re.IGNORECASE).strip()
        if len(limpia) > 5 and not limpia.lower().startswith("categoría") and not limpia.lower().startswith("versión"):
            titulo_candidato = limpia
            break
    
    if not titulo_candidato:
        base = os.path.splitext(nombre_original)[0]
        titulo_candidato = base.replace("_", " ").replace("-", " ").capitalize()
    
    # 3. Detectar Categoría
    categoria = "Soporte Técnico / Redes"
    match_cat = re.search(r"categor[ií]a[:\s]+([^\n\r]+)", texto_crudo, re.IGNORECASE)
    if match_cat:
        categoria = match_cat.group(1).strip("*_ ")
    elif any(k in texto_crudo.lower() for k in ["ont", "pon", "los", "huawei", "zte"]):
        categoria = "Equipos de Cliente / ONT"
    elif any(k in texto_crudo.lower() for k in ["wifi", "wi-fi", "2.4ghz", "5ghz", "canal"]):
        categoria = "Red Inalámbrica / Wi-Fi"
    elif any(k in texto_crudo.lower() for k in ["fibra", "atenuacion", "potencia", "spliter"]):
        categoria = "Planta Externa / Fibra Óptica"
    
    # 4. Estructurar cuerpo identificando pasos
    bloques_pasos = []
    descripcion_general = []
    resto_contenido = []
    
    en_procedimiento = False
    paso_actual = 0
    
    for l in lineas:
        # Detectar inicio de un paso
        match_paso = re.match(r"^(?:###\s*)?(?:paso|step)\s*(\d+)[:\s.-]*(.*)$", l, re.IGNORECASE)
        match_num = re.match(r"^(\d+)\.\s+(.*)$", l)
        
        if match_paso:
            en_procedimiento = True
            paso_actual += 1
            num_detectado = match_paso.group(1)
            encabezado_paso = match_paso.group(2).strip() or f"Instrucción Operativa {num_detectado}"
            bloques_pasos.append(f"### Paso {paso_actual}: {encabezado_paso}")
        elif match_num and len(match_num.group(2)) > 10 and not l.startswith("|"):
            en_procedimiento = True
            paso_actual += 1
            encabezado_paso = match_num.group(2).strip()
            # Si el texto es largo, usar las primeras palabras como título
            palabras = encabezado_paso.split()
            tit_paso = " ".join(palabras[:5]) if len(palabras) > 5 else encabezado_paso
            bloques_pasos.append(f"### Paso {paso_actual}: {tit_paso}")
            if len(palabras) > 5:
                bloques_pasos.append(encabezado_paso)
        else:
            if en_procedimiento:
                bloques_pasos.append(l)
            elif "descripci" in l.lower():
                pass
            elif not descripcion_general and len(l) > 20 and not l.startswith("#"):
                descripcion_general.append(l)
            else:
                resto_contenido.append(l)
    
    # Ensamblar Markdown limpio
    desc_texto = " ".join(descripcion_general) if descripcion_general else f"Procedimiento técnico oficial para {titulo_candidato.lower()} en infraestructura de clientes ConectaTec ISP."
    
    md_final = [
        f"# {doc_id}: {titulo_candidato}",
        "",
        f"**Categoría:** {categoria}  ",
        "**Fabricante / Origen:** Operaciones ConectaTec ISP / Carrier Support  ",
        "**Versión / Vigencia:** v1.0 - Actualizado 2026  ",
        "",
        "## Descripción General",
        desc_texto,
        "",
        "## Procedimiento Operativo Paso a Paso"
    ]
    
    if bloques_pasos:
        md_final.extend(bloques_pasos)
    else:
        # Si no hubo pasos explícitos detectados, generamos al menos 2 pasos estructurados
        md_final.append("### Paso 1: Verificación de Condiciones Iniciales")
        md_final.append("Inspeccione el estado general del enlace, cableado y alimentación del equipo.")
        md_final.append("")
        md_final.append("### Paso 2: Ejecución del Procedimiento Técnico")
        if resto_contenido:
            md_final.extend(resto_contenido[:10])
        else:
            md_final.append("Aplique las instrucciones técnicas de calibración y reseteo según especificaciones del fabricante.")
        md_final.append("")
        md_final.append("### Paso 3: Confirmación y Cierre")
        md_final.append("Compruebe que el servicio haya restablecido parámetros nominales de navegación.")
    
    md_final.append("")
    md_final.append("---")
    md_final.append("*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*")
    md_final.append("")
    
    contenido_markdown = "\n".join(md_final)
    return doc_id, titulo_candidato, contenido_markdown


def convertir_documento(stream_bytes: bytes, nombre_archivo: str, guardar_en_raw: bool = False) -> Dict[str, Any]:
    """
    Convierte un documento en memoria (.docx o .pdf) a formato Markdown para RAG.
    Opcionalmente lo persiste directamente en data/raw/.
    """
    ext = os.path.splitext(nombre_archivo)[1].lower()
    bio = io.BytesIO(stream_bytes)
    
    if ext == ".docx":
        texto_crudo = extraer_texto_docx(bio)
    elif ext == ".pdf":
        texto_crudo = extraer_texto_pdf(bio)
    else:
        raise ValueError(f"Extensión no soportada: {ext}. Solo se admiten archivos .docx y .pdf.")
    
    doc_id, titulo, md_content = estructurar_a_markdown_rag(texto_crudo, nombre_archivo)
    
    # Nombre de archivo sugerido: DOC-XX_slug_titulo.md
    slug = re.sub(r"[^\w\s-]", "", titulo).strip().lower()
    slug = re.sub(r"[-\s]+", "_", slug)[:40]
    nombre_archivo_md = f"{doc_id}_{slug}.md"
    
    ruta_guardado = None
    if guardar_en_raw:
        os.makedirs(DIRECTORIO_RAW, exist_ok=True)
        ruta_guardado = os.path.join(DIRECTORIO_RAW, nombre_archivo_md)
        with open(ruta_guardado, "w", encoding="utf-8") as f:
            f.write(md_content)
            
    return {
        "nombre_archivo_md": nombre_archivo_md,
        "documento_id": doc_id,
        "titulo": titulo,
        "contenido_markdown": md_content,
        "guardado_en_raw": bool(guardar_en_raw),
        "ruta_guardado": ruta_guardado
    }
