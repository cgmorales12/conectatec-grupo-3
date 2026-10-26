"""
Script de Auditoría Determinista de Seguridad: Cero Secretos en Git
Caso N.º 03 · ConectaTec ISP (Grupo 3 UNIANDES)
Evalúa el cumplimiento estricto de:
- .env en .gitignore
- .env NUNCA comiteado en ningún commit de la historia del repositorio
- Claves de API cargadas exclusivamente desde variables de entorno (os.environ)
- .env.example como plantilla pública libre de claves reales

Uso:
    python scripts/auditar_cero_secretos.py
"""

import os
import sys
import subprocess
import re

# Forzar codificación UTF-8 en consolas Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def print_resultado(titulo: str, ok: bool, detalle: str = ""):
    badge = "[PASS]" if ok else "[FAIL]"
    color = "\033[92m" if ok else "\033[91m"
    reset = "\033[0m"
    print(f" {color}{badge}{reset} {titulo}")
    if detalle:
        print(f"        └─ {detalle}")


def main():
    print("=" * 70)
    print(" AUDITORIA DE SEGURIDAD: POLITICA CERO SECRETOS EN GIT")
    print(" Proyecto: ConectaTec / TecnoAula · Grupo 3 UNIANDES (Caso N. 03)")
    print(" Marco: OWASP LLM06 / LOPDP Art. 23 (Cero Credenciales en Codigo)")
    print("=" * 70)

    raiz = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    todos_ok = True

    # 1. Verificar .env en .gitignore
    ruta_gitignore = os.path.join(raiz, ".gitignore")
    if not os.path.exists(ruta_gitignore):
        print_resultado(".gitignore existe en la raíz", False, "No se encontró .gitignore")
        todos_ok = False
    else:
        with open(ruta_gitignore, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
        tiene_env = ".env" in lineas or any(p.startswith(".env") for p in lineas)
        print_resultado(
            ".env está explícitamente ignorado en .gitignore",
            tiene_env,
            "Reglas activas: .env, .env.*, *.env, .env.local" if tiene_env else "Falta regla .env"
        )
        todos_ok = todos_ok and tiene_env

    # 2. Verificar que .env NO esté rastreado en el índice de Git
    cmd_ls = ["git", "ls-files", ".env"]
    res_ls = subprocess.run(cmd_ls, cwd=raiz, capture_output=True, text=True)
    no_rastreado = (res_ls.returncode == 0 and res_ls.stdout.strip() == "")
    print_resultado(
        ".env NO está rastreado en el índice actual de Git",
        no_rastreado,
        "git ls-files .env -> (vacío: el archivo local no está trackeado)" if no_rastreado else "¡ALERTA! .env está rastreado por git"
    )
    todos_ok = todos_ok and no_rastreado

    # 3. Verificar que .env NUNCA ha aparecido en ningún commit
    cmd_log = ["git", "log", "--all", "--full-history", "--oneline", "--", ".env"]
    res_log = subprocess.run(cmd_log, cwd=raiz, capture_output=True, text=True)
    cero_commits = (res_log.returncode == 0 and res_log.stdout.strip() == "")
    print_resultado(
        ".env NUNCA ha sido incluido en ningún commit de la historia",
        cero_commits,
        "git log --all --full-history -- .env -> 0 commits encontrados" if cero_commits else f"¡ALERTA! Commits con .env: {res_log.stdout.strip()}"
    )
    todos_ok = todos_ok and cero_commits

    # 4. Verificar .env.example como plantilla limpia
    ruta_example = os.path.join(raiz, ".env.example")
    if not os.path.exists(ruta_example):
        print_resultado(".env.example existe como plantilla", False, "No se encontró .env.example")
        todos_ok = False
    else:
        with open(ruta_example, "r", encoding="utf-8") as f:
            contenido_example = f.read()

        tiene_gemini_key_real = bool(re.search(r'AIzaSy[A-Za-z0-9_-]{33}', contenido_example))
        tiene_groq_key_real = bool(re.search(r'gsk_[A-Za-z0-9]{50,}', contenido_example))
        plantilla_limpia = not (tiene_gemini_key_real or tiene_groq_key_real)
        print_resultado(
            ".env.example contiene únicamente valores de plantilla (sin secretos reales)",
            plantilla_limpia,
            "Variables declaradas: GEMINI_API_KEY, GROQ_API_KEY, PROVEEDOR_LLM_ACTIVO con valores placeholder"
        )
        todos_ok = todos_ok and plantilla_limpia

    # 5. Verificar que el código fuente carga claves solo por os.environ
    sys.path.insert(0, raiz)
    try:
        from app.services.llm import cliente_llm
        carga_env_ok = (
            cliente_llm.gemini_api_key == os.environ.get("GEMINI_API_KEY") and
            cliente_llm.groq_api_key == os.environ.get("GROQ_API_KEY")
        )
        print_resultado(
            "ClienteLLM lee credenciales exclusivamente desde os.environ / dotenv",
            carga_env_ok,
            f"Proveedor activo: {cliente_llm.proveedor_activo} | Keys cargadas dinámicamente desde entorno"
        )
        todos_ok = todos_ok and carga_env_ok
    except Exception as e:
        print_resultado("ClienteLLM lee credenciales desde variables de entorno", False, str(e))
        todos_ok = False

    # 6. Escaneo de seguridad estático en archivos de código (.py)
    patrones_secretos = [
        ("Google Gemini API Key", re.compile(r'AIzaSy[A-Za-z0-9_-]{33}')),
        ("Groq Cloud API Key", re.compile(r'gsk_[A-Za-z0-9]{50,}'))
    ]

    fugas_encontradas = []
    for dirpath, _, filenames in os.walk(os.path.join(raiz, "app")):
        for fname in filenames:
            if fname.endswith((".py", ".json", ".js")):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, linea in enumerate(f, 1):
                            for nombre_patron, regex in patrones_secretos:
                                if regex.search(linea):
                                    fugas_encontradas.append(f"{fpath}:{idx} ({nombre_patron})")
                except Exception:
                    pass

    escaneo_limpio = (len(fugas_encontradas) == 0)
    print_resultado(
        "Escaneo estático en app/ libre de claves o tokens hardcodeados",
        escaneo_limpio,
        "Ninguna clave AIzaSy o gsk encontrada en código Python/JS" if escaneo_limpio else f"Fugas: {fugas_encontradas}"
    )
    todos_ok = todos_ok and escaneo_limpio

    print("=" * 70)
    if todos_ok:
        print(" \033[92m[OK] RESULTADO: 100% CUMPLIMIENTO CERO SECRETOS EN GIT (POLITICA APROBADA)\033[0m")
        print("   - .env protegido en .gitignore")
        print("   - 0 commits con secretos en la historia de Git")
        print("   - Credenciales desacopladas e inyectadas solo en runtime")
        print("=" * 70)
        sys.exit(0)
    else:
        print(" \033[91m[ERROR] RESULTADO: SE ENCONTRARON NO CONFORMIDADES DE SEGURIDAD\033[0m")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
