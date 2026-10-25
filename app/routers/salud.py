"""
Enrutador de Salud y Diagnóstico Operativo - ConectaTec
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import os

router = APIRouter(tags=["Salud y Monitoreo"])

@router.get("/v1/salud", summary="Chequeo de salud del sistema")
@router.get("/health", summary="Endpoint alternativo de salud")
def health_check():
    """
    Informa el estado de operatividad del backend, base de datos y proveedor de IA.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "conectatec.db")
    db_activa = os.path.exists(db_path)
    
    return {
        "status": "ok",
        "servicio": "conectatec-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "base_datos": {
            "motor": "sqlite",
            "conectada": db_activa
        },
        "arquitectura": {
            "modelo_primario": "gemini-1.5-flash",
            "modelo_respaldo": "llama-3.3-70b-versatile (Groq)",
            "rag": "ChromaDB / 15 Manuales ISP",
            "matriz_itil": "determinista (config/matriz_prioridad.json)"
        }
    }
