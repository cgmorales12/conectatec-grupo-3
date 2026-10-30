#!/usr/bin/env python3
"""
Punto de Entrada Retrocompatible: eval/evaluar.py
Ejecuta la suite oficial completa de evaluación invocando run_eval.py.
"""

import os
import sys

ruta_run_eval = os.path.join(os.path.dirname(__file__), "run_eval.py")
if os.path.exists(ruta_run_eval):
    with open(ruta_run_eval, "rb") as f:
        codigo = compile(f.read(), ruta_run_eval, "exec")
        exec(codigo, {"__name__": "__main__", "__file__": ruta_run_eval})
else:
    print(f"Error: No se encontró {ruta_run_eval}")
    sys.exit(1)
