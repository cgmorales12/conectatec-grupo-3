"""
Enrutador de Endpoints Principales - ConectaTec
Cumple con la rúbrica del Seminario de Titulación:
- POST /chat: Endpoint conversacional interactivo con streaming en tiempo real (StreamingResponse).
- POST /clasificar: Triaje e inferencia técnica retornando JSON bajo esquema estricto Pydantic V2.
- POST /analizar: Diagnóstico técnico estructurado con contrato de entrada y salida Pydantic V2.
"""

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.schemas import (
    SolicitudChatIn,
    SolicitudTicketIn,
    TicketOut,
    SolicitudAnalizarIn,
    ResultadoAnalizarOut
)
from app.services.llm import (
    cliente_llm,
    generar_flujo_chat_streaming,
    analizar_incidencia_tecnica
)
from app.routers.tickets import clasificar_y_crear_ticket

router = APIRouter(tags=["Endpoints Principales"])


@router.get(
    "/v1/llm/proveedor",
    summary="Consulta el proveedor LLM activo encapsulado",
    description="Demuestra que el cliente está encapsulado: cambiar de proveedor no toca los endpoints."
)
def consultar_proveedor_activo():
    """Retorna el proveedor configurado en el cliente encapsulado ClienteLLM."""
    return {
        "proveedor_activo": cliente_llm.obtener_proveedor_activo(),
        "encapsulado": True,
        "mensaje": "El cliente del modelo está encapsulado: cambiar de proveedor no toca los endpoints."
    }



@router.post(
    "/chat",
    summary="Endpoint conversacional con Streaming en tiempo real",
    description="Recibe una consulta técnica o del usuario y retorna la respuesta en streaming continuo (token a token / chunk a chunk).",
    response_class=StreamingResponse
)
def chat_conversacional_stream(solicitud: SolicitudChatIn):
    """
    Endpoint conversacional con StreamingResponse.
    Valida el payload con Pydantic (extra='forbid') y transmite la respuesta en streaming.
    """
    historial_dict = [m.model_dump() for m in (solicitud.historial or [])]
    generador = generar_flujo_chat_streaming(
        mensaje=solicitud.mensaje,
        historial=historial_dict,
        simular_caida_gemini=solicitud.simular_caida_gemini,
        simular_caida_groq=solicitud.simular_caida_groq
    )
    return StreamingResponse(
        generador,
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/clasificar",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="Clasificación y triaje determinista con esquema Pydantic",
    description="Recibe un reporte de incidencia, extrae impacto/urgencia con IA y retorna JSON estrictamente validado por Pydantic."
)
def clasificar_directo(solicitud: SolicitudTicketIn):
    """
    Endpoint no conversacional de clasificación.
    Garantiza entrada y salida estrictas bajo contratos Pydantic V2.
    """
    return clasificar_y_crear_ticket(solicitud)


@router.post(
    "/analizar",
    response_model=ResultadoAnalizarOut,
    status_code=status.HTTP_200_OK,
    summary="Análisis técnico estructurado de fallas con esquema Pydantic",
    description="Analiza los síntomas y avería reportada retornando diagnóstico, causa y severidad en formato JSON estructurado."
)
def analizar_problema_tecnico(solicitud: SolicitudAnalizarIn):
    """
    Endpoint no conversacional de análisis técnico.
    Retorna JSON con esquema estricto Pydantic V2 (ResultadoAnalizarOut).
    """
    return analizar_incidencia_tecnica(solicitud)
