#!/usr/bin/env python3
"""
Punto de Entrada Raíz: run_eval.py
Permite ejecutar la suite completa de evaluación de calidad directamente desde la raíz:
  python run_eval.py
O desde el subdirectorio eval:
  python eval/run_eval.py
"""

import os
import sys

# Redirigir a eval/run_eval.py
ruta_eval = os.path.join(os.path.dirname(__file__), "eval", "run_eval.py")
if os.path.exists(ruta_eval):
    with open(ruta_eval, "rb") as f:
        codigo = compile(f.read(), ruta_eval, "exec")
        exec(codigo, {"__name__": "__main__", "__file__": ruta_eval})
else:
    print(f"Error: No se encontró el archivo de evaluación en {ruta_eval}")
    sys.exit(1)

