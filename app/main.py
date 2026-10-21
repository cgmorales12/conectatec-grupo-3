"""
Punto de entrada principal de la API - ConectaTec
Caso 03: Triaje Inteligente de Incidentes para ISP
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="ConectaTec API",
    description="Sistema de triaje automático y priorización de incidentes de soporte técnico ISP",
    version="0.1.0"
)

# Configuración de CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "sistema": "ConectaTec API",
        "version": "0.1.0",
        "estado": "activo",
        "documentacion": "/docs"
    }

@app.get("/health")
def health_check():
    """
    Endpoint de chequeo de salud para monitoreo del backend.
    """
    return {
        "status": "ok",
        "service": "conectatec-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "sqlite",
        "llm_provider": "gemini-1.5-flash"
    }
