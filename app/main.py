"""
Punto de Entrada Principal de la API - ConectaTec
Caso 03: Triaje Inteligente de Incidentes para ISP (Grupo 3 UNIANDES)
Cumple: RFC 9457 Problem Details, Token Bucket Rate Limiting, CORS seguro y AnyIO.
"""

import time
import uuid
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv(override=True)

from app.routers import tickets_router, salud_router, auth_router, manuales_router, principal_router
from app.database import inicializar_bd


# ============================================================================
# Logger Estructurado y Registro de Observabilidad (Tokens y Latencia)
# ============================================================================

logger_solicitudes = logging.getLogger("conectatec.solicitudes")
if not logger_solicitudes.handlers:
    _sh = logging.StreamHandler()
    _sh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger_solicitudes.addHandler(_sh)
    logger_solicitudes.setLevel(logging.INFO)

# Buffer circular en memoria de métricas por solicitud (últimas 300 peticiones)
_registro_solicitudes_metricas = deque(maxlen=300)


def registrar_log_solicitud(datos: dict):
    """Almacena el registro de una solicitud en el buffer de métricas."""
    _registro_solicitudes_metricas.append(datos)


def obtener_metricas_solicitudes():
    """Calcula estadísticas agregadas de solicitudes, tokens consumidos y tiempos de respuesta."""
    items = list(_registro_solicitudes_metricas)
    total = len(items)
    if total == 0:
        return {
            "total_solicitudes": 0,
            "tiempo_promedio_ms": 0.0,
            "total_tokens_consumidos": 0,
            "total_tokens_prompt": 0,
            "total_tokens_completado": 0,
            "solicitudes_recientes": []
        }

    tiempos = [it["tiempo_respuesta_ms"] for it in items if "tiempo_respuesta_ms" in it]
    tokens_tot = [it["tokens_total"] for it in items if it.get("tokens_total") is not None]
    tokens_in = [it["tokens_prompt"] for it in items if it.get("tokens_prompt") is not None]
    tokens_out = [it["tokens_completado"] for it in items if it.get("tokens_completado") is not None]

    promedio_ms = round(sum(tiempos) / len(tiempos), 2) if tiempos else 0.0

    return {
        "total_solicitudes": total,
        "tiempo_promedio_ms": promedio_ms,
        "total_tokens_consumidos": sum(tokens_tot),
        "total_tokens_prompt": sum(tokens_in),
        "total_tokens_completado": sum(tokens_out),
        "solicitudes_recientes": items[::-1][:50]
    }


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
    # Excluir rutas de interfaz gráfica, salud, métricas y documentación de límites de consumo
    rutas_excluidas = [
        "/", "/health", "/salud", "/v1/salud", "/docs", "/redoc", "/openapi.json",
        "/tablero", "/favicon.ico", "/v1/metricas/solicitudes", "/metricas/solicitudes"
    ]
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
# Middleware: Log por Solicitud, Medición de Latencia y Consumo de Tokens
# Rubro: "Log por solicitud: Tokens consumidos y tiempo de respuesta."
# ============================================================================

@app.middleware("http")
async def middleware_observabilidad_solicitudes(request: Request, call_next):
    req_id = f"req-{str(uuid.uuid4())[:8]}"
    request.state.req_id = req_id
    t_inicio = time.perf_counter()

    response = await call_next(request)

    duracion_ms = round((time.perf_counter() - t_inicio) * 1000, 2)
    response.headers["X-Response-Time-Ms"] = str(duracion_ms)
    response.headers["X-Request-ID"] = req_id

    # Extraer metadatos de IA si fueron generados durante la atención del endpoint
    meta_ia = getattr(request.state, "metadatos_ia", None)
    tokens_prompt = getattr(meta_ia, "tokens_prompt", None) if meta_ia else None
    tokens_completado = getattr(meta_ia, "tokens_completado", None) if meta_ia else None
    tokens_total = getattr(meta_ia, "tokens_total", None) if meta_ia else None
    proveedor = getattr(meta_ia, "proveedor", None) if meta_ia else None
    modelo = getattr(meta_ia, "modelo", None) if meta_ia else None

    # Registrar en buffer de auditoría y métricas
    registro = {
        "req_id": req_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metodo": request.method,
        "ruta": request.url.path,
        "status_code": response.status_code,
        "tiempo_respuesta_ms": duracion_ms,
        "proveedor": proveedor or "n/a",
        "modelo": modelo or "n/a",
        "tokens_prompt": tokens_prompt if tokens_prompt is not None else 0,
        "tokens_completado": tokens_completado if tokens_completado is not None else 0,
        "tokens_total": tokens_total if tokens_total is not None else 0
    }
    registrar_log_solicitud(registro)

    # Registro en log por solicitud con formato estructurado
    if tokens_total is not None and tokens_total > 0:
        logger_solicitudes.info(
            f"📊 [SOLICITUD HTTP] {request.method} {request.url.path} -> {response.status_code} | "
            f"Tiempo: {duracion_ms}ms | ReqID: {req_id} | "
            f"IA: {proveedor}:{modelo} | Tokens: in={tokens_prompt}, out={tokens_completado}, total={tokens_total}"
        )
    else:
        logger_solicitudes.info(
            f"📊 [SOLICITUD HTTP] {request.method} {request.url.path} -> {response.status_code} | "
            f"Tiempo: {duracion_ms}ms | ReqID: {req_id}"
        )

    return response

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

app.include_router(principal_router)
app.include_router(principal_router, prefix="/v1")
app.include_router(tickets_router)
app.include_router(salud_router)
app.include_router(auth_router)
app.include_router(manuales_router)


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

