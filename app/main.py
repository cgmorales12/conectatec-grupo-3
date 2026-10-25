"""
Punto de Entrada Principal de la API - ConectaTec
Caso 03: Triaje Inteligente de Incidentes para ISP (Grupo 3 UNIANDES)
Cumple: RFC 9457 Problem Details, Token Bucket Rate Limiting, CORS seguro y AnyIO.
"""

import time
import uuid
from collections import defaultdict
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from contextlib import asynccontextmanager
from app.routers import tickets_router, salud_router
from app.database import inicializar_bd

# ============================================================================
# Inicialización de la Aplicación FastAPI con Lifespan Moderno
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar tablas de SQLite al arrancar el backend
    inicializar_bd()
    yield

app = FastAPI(
    title="ConectaTec API · Triaje Inteligente ISP",
    description="Sistema de triaje automático, priorización determinista ITIL y resolución con RAG sobre 15 manuales técnicos oficiales.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Middleware: Limitador de Tasa Token Bucket por Sesión / IP (Reto 8 Backend)
# Capacidad: 10 fichas | Recarga: 1 ficha cada 6 segundos
# ============================================================================

CUBETA_CAPACIDAD = 15.0
CUBETA_RECARGA_SEGUNDOS = 3.0

_cubetas_clientes = defaultdict(lambda: {"fichas": CUBETA_CAPACIDAD, "ultimo_tiempo": time.time()})

@app.middleware("http")
async def limitador_tasa_token_bucket(request: Request, call_next):
    # Excluir rutas de interfaz gráfica, salud y documentación de límites de consumo
    rutas_excluidas = ["/", "/health", "/v1/salud", "/docs", "/redoc", "/openapi.json", "/tablero", "/favicon.ico"]
    if request.url.path in rutas_excluidas or request.url.path.startswith("/docs"):
        return await call_next(request)
        
    client_ip = request.client.host if request.client else "127.0.0.1"
    ahora = time.time()
    
    estado = _cubetas_clientes[client_ip]
    dt = ahora - estado["ultimo_tiempo"]
    estado["ultimo_tiempo"] = ahora
    
    # Recargar fichas según el tiempo transcurrido
    estado["fichas"] = min(CUBETA_CAPACIDAD, estado["fichas"] + (dt / CUBETA_RECARGA_SEGUNDOS))
    
    if estado["fichas"] >= 1.0:
        estado["fichas"] -= 1.0
        response = await call_next(request)
        return response
    else:
        # Calcular tiempo de espera requerido
        espera_segundos = int(max(1, (1.0 - estado["fichas"]) * CUBETA_RECARGA_SEGUNDOS))
        req_id = f"req-{str(uuid.uuid4())[:8]}"
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/problem+json",
            headers={"Retry-After": str(espera_segundos)},
            content={
                "type": "/errores/limite-alcanzado",
                "title": "Demasiadas Solicitudes",
                "status": 429,
                "detail": f"Has alcanzado el límite de tasa permitido. Por favor espera {espera_segundos} segundos antes de reintentar.",
                "instance": f"{request.url.path}#{req_id}"
            }
        )

# ============================================================================
# Manejadores de Excepciones Estándar RFC 9457 (Problem Details)
# ============================================================================

@app.exception_handler(RequestValidationError)
async def manejador_error_validacion_422(request: Request, exc: RequestValidationError):
    req_id = f"req-{str(uuid.uuid4())[:8]}"
    primer_error = exc.errors()[0] if exc.errors() else {}
    campo_raw = " -> ".join(str(loc) for loc in primer_error.get("loc", []))
    
    # Nombres en español para los campos del formulario
    nombres_campos = {
        "body -> descripcion_problema": "Descripción del problema",
        "body -> nombre_cliente": "Nombre del abonado",
        "body -> email_cliente": "Correo electrónico",
        "body -> codigo_abonado": "Código de abonado"
    }
    campo = nombres_campos.get(campo_raw, campo_raw)
    
    tipo_error = primer_error.get("type", "")
    if "string_too_short" in tipo_error or "at_least" in primer_error.get("msg", ""):
        min_chars = primer_error.get("ctx", {}).get("min_length", 10)
        detalle = f"El campo '{campo}' debe tener al menos {min_chars} caracteres para que la IA realice el triaje."
    elif "email" in tipo_error or "value_error" in tipo_error:
        detalle = f"El campo '{campo}' debe ser una dirección de correo válida (ej. usuario@dominio.com)."
    else:
        detalle = f"Error en campo '{campo}': {primer_error.get('msg', 'Entrada no válida')}."
    
    return JSONResponse(
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        media_type="application/problem+json",
        content={
            "type": "/errores/entrada-invalida",
            "title": "Entrada Invalida",
            "status": 422,
            "detail": detalle,
            "instance": f"{request.url.path}#{req_id}"
        }
    )

@app.exception_handler(StarletteHTTPException)
async def manejador_errores_http_estandar(request: Request, exc: StarletteHTTPException):
    req_id = f"req-{str(uuid.uuid4())[:8]}"
    titulos = {
        404: "Recurso No Encontrado",
        429: "Demasiadas Solicitudes",
        500: "Error Interno del Servidor",
        503: "Servicio Temporalmente No Disponible"
    }
    titulo = titulos.get(exc.status_code, "Error HTTP")
    
    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/problem+json",
        content={
            "type": f"/errores/http-{exc.status_code}",
            "title": titulo,
            "status": exc.status_code,
            "detail": str(exc.detail),
            "instance": f"{request.url.path}#{req_id}"
        }
    )

# ============================================================================
# Registro de Enrutadores Modulares
# ============================================================================

app.include_router(tickets_router)
app.include_router(salud_router)

@app.get("/", tags=["Raíz"])
def raiz():
    return {
        "sistema": "ConectaTec API",
        "descripcion": "Triaje Inteligente de Incidentes ISP con IA y RAG",
        "version": "1.0.0",
        "tablero_kanban": "/tablero",
        "documentacion": "/docs",
        "salud": "/v1/salud"
    }

@app.get("/tablero", tags=["Frontend Kanban"])
def ver_tablero_kanban():
    """Sirve la interfaz web interactiva del tablero Kanban."""
    import os
    from fastapi.responses import FileResponse
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)

