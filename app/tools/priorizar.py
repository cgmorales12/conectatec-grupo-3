"""
Lógica de Negocio Determinista: Matriz ITIL de Priorización
Principio: «El modelo propone (Impacto x Urgencia), el código dispone (Prioridad y SLA)».
El LLM jamás calcula la prioridad matemática directamente.
"""

import os
import json
from app.schemas import PrioridadSLA

CONFIG_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "matriz_prioridad.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "prioridades.json"),
]

def _cargar_matriz_config():
    """Carga la matriz ITIL desde el archivo de configuración JSON."""
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    
    # Matriz por defecto si no se encuentra el archivo
    return {
        "matriz": {
            "Alto": {
                "Alta": {"prioridad": "Alta", "sla_minutos": 120, "descripcion_sla": "Atención crítica en menos de 2 horas (cuadrilla inmediata)"},
                "Media": {"prioridad": "Alta", "sla_minutos": 360, "descripcion_sla": "Atención prioritaria en menos de 6 horas"},
                "Baja": {"prioridad": "Media", "sla_minutos": 1440, "descripcion_sla": "Atención técnica en 24 horas laborables"}
            },
            "Medio": {
                "Alta": {"prioridad": "Alta", "sla_minutos": 240, "descripcion_sla": "Atención domiciliaria en menos de 4 horas"},
                "Media": {"prioridad": "Media", "sla_minutos": 480, "descripcion_sla": "Soporte remoto en menos de 8 horas"},
                "Baja": {"prioridad": "Baja", "sla_minutos": 1440, "descripcion_sla": "Atención regular en 24 horas"}
            },
            "Bajo": {
                "Alta": {"prioridad": "Media", "sla_minutos": 480, "descripcion_sla": "Soporte en jornada laboral (8 horas)"},
                "Media": {"prioridad": "Baja", "sla_minutos": 1440, "descripcion_sla": "Atención regular en 24 horas"},
                "Baja": {"prioridad": "Baja", "sla_minutos": 2880, "descripcion_sla": "Consulta informativa / Autoatención (48 horas)"}
            }
        }
    }

def calcular_prioridad_itil(impacto: str, urgencia: str) -> PrioridadSLA:
    """
    Calcula matemáticamente la prioridad ITIL y el SLA a partir del cruce de Impacto y Urgencia.
    Función determinista, reproducible y con costo CERO de tokens.
    """
    config = _cargar_matriz_config()
    matriz = config.get("matriz", {})
    
    impacto_norm = impacto.capitalize()
    urgencia_norm = urgencia.capitalize()
    
    # Validar valores según estándar ITIL
    if impacto_norm not in matriz:
        impacto_norm = "Medio"
    if urgencia_norm not in matriz[impacto_norm]:
        urgencia_norm = "Media"
        
    resultado = matriz[impacto_norm][urgencia_norm]
    
    return PrioridadSLA(
        prioridad=resultado["prioridad"],
        sla_minutos=resultado["sla_minutos"],
        descripcion_sla=resultado["descripcion_sla"]
    )
