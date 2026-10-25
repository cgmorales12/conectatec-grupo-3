#!/usr/bin/env python3
"""
Script de Conversión Automática de Manuales: Word / PDF -> Markdown RAG
Caso de Uso: El personal técnico de TIC suelta archivos .docx o .pdf en data/inbox/
y el script los convierte y formatea automáticamente a data/raw/ con nomenclatura DOC-XX.

Uso:
    python scripts/convertir_a_markdown.py
    python scripts/convertir_a_markdown.py mi_manual.docx
"""

import os
import sys
import shutil
import glob

# Asegurar que el directorio raíz del proyecto esté en el path de Python
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app.services.conversor import convertir_documento

CARPETA_INBOX = os.path.join(RAIZ, "data", "inbox")
CARPETA_PROCESADOS = os.path.join(CARPETA_INBOX, "procesados")
CARPETA_RAW = os.path.join(RAIZ, "data", "raw")


def inicializar_carpetas():
    os.makedirs(CARPETA_INBOX, exist_ok=True)
    os.makedirs(CARPETA_PROCESADOS, exist_ok=True)
    os.makedirs(CARPETA_RAW, exist_ok=True)


def procesar_archivo(ruta_origen: str):
    nombre_archivo = os.path.basename(ruta_origen)
    print(f"\n⚙️  Procesando: {nombre_archivo} ...")
    
    with open(ruta_origen, "rb") as f:
        contenido_bytes = f.read()
    
    try:
        resultado = convertir_documento(contenido_bytes, nombre_archivo, guardar_en_raw=True)
        print(f"   ✅ Convertido con éxito:")
        print(f"      • Código Asignado: {resultado['documento_id']}")
        print(f"      • Título Oficial : {resultado['titulo']}")
        print(f"      • Archivo Salida : data/raw/{resultado['nombre_archivo_md']}")
        
        # Mover original a procesados si estaba en inbox
        if os.path.dirname(os.path.abspath(ruta_origen)) == os.path.abspath(CARPETA_INBOX):
            destino_procesado = os.path.join(CARPETA_PROCESADOS, nombre_archivo)
            shutil.move(ruta_origen, destino_procesado)
            print(f"      • Original movido a: data/inbox/procesados/{nombre_archivo}")
            
    except Exception as e:
        print(f"   ❌ Error al convertir {nombre_archivo}: {e}")


def main():
    inicializar_carpetas()
    print("=" * 70)
    print(" 📑 CONVERSOR AUTOMÁTICO DE MANUALES TIC A MARKDOWN RAG (ConectaTec)")
    print("=" * 70)
    
    # 1. Si se pasó un archivo por parámetro de línea de comandos
    if len(sys.argv) > 1:
        ruta_param = sys.argv[1]
        if not os.path.isfile(ruta_param):
            print(f"❌ El archivo '{ruta_param}' no existe.")
            sys.exit(1)
        procesar_archivo(ruta_param)
        print("\n✨ Proceso finalizado.")
        return

    # 2. Escanear el buzón data/inbox/
    patrones = ["*.docx", "*.pdf", "*.DOCX", "*.PDF"]
    archivos_encontrados = []
    for pat in patrones:
        archivos_encontrados.extend(glob.glob(os.path.join(CARPETA_INBOX, pat)))
    
    if not archivos_encontrados:
        print(f"ℹ️  El buzón está vacío:")
        print(f"   📂 Ruta del buzón: {os.path.relpath(CARPETA_INBOX, RAIZ)}")
        print("\n💡 Instrucciones para el personal TIC:")
        print("   1. Copia o suelta tus archivos de Word (.docx) o PDF en 'data/inbox/'")
        print("   2. Vuelve a ejecutar: python scripts/convertir_a_markdown.py")
        print("   3. Tus archivos se convertirán automáticamente a .md estructurado en 'data/raw/'")
        print("=" * 70)
        return

    print(f"🔍 Se encontraron {len(archivos_encontrados)} archivo(s) en el buzón 'data/inbox/':")
    for a in archivos_encontrados:
        procesar_archivo(a)

    print("\n" + "=" * 70)
    print("🎉 Todos los documentos del buzón fueron procesados y guardados en data/raw/.")
    print("=" * 70)


if __name__ == "__main__":
    main()
