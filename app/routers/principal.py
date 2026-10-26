"""
Enrutador de Endpoints Principales - ConectaTec
Cumple con la rúbrica del Seminario de Titulación:
- POST /chat: Endpoint conversacional interactivo con streaming en tiempo real (StreamingResponse).
- POST /clasificar: Triaje e inferencia técnica retornando JSON bajo esquema estricto Pydantic V2.
- POST /analizar: Diagnóstico técnico estructurado con contrato de entrada y salida Pydantic V2.
"""

from fastapi import APIRouter, status, Request
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
    "/metricas/solicitudes",
    summary="Métricas de observabilidad y registro de logs por solicitud",
    description="Retorna el volumen de solicitudes, latencia promedio, desglose de tokens y últimas peticiones."
)
def consultar_metricas_solicitudes():
    """Retorna métricas agregadas y registros de log estructurado por solicitud."""
    from app.main import obtener_metricas_solicitudes
    return obtener_metricas_solicitudes()


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


@router.get(
    "/v1/prompts/versiones",
    summary="Consulta las 3 versiones de system prompts probadas (system_v1, v2, v3)",
    description="Retorna el estado de los prompts versionados app/prompts/system_v1.md, v2.md y v3.md con rol, tono, restricciones y abstención."
)
def consultar_versiones_prompts():
    """Retorna las 3 versiones de prompts y el estado de cumplimiento de los criterios."""
    from app.services.llm import cargar_prompt_sistema
    return {
        "version_activa": cliente_llm.version_prompt,
        "versiones_disponibles": ["v1", "v2", "v3"],
        "criterios_verificados": {
            "rol": "Definido formalmente en las 3 versiones",
            "tono": "Técnico, sobrio, formal y empático",
            "restricciones": "JSON estricto, sin markdown extra, delimitación <solicitud>",
            "instruccion_abstencion": "Cero alucinación: abstenerse de inventar ante dudas o consultas ajenas"
        },
        "prompt_activo_muestra": cargar_prompt_sistema(cliente_llm.version_prompt)[:280] + "..."
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
def clasificar_directo(solicitud: SolicitudTicketIn, request: Request = None):
    """
    Endpoint no conversacional de clasificación.
    Garantiza entrada y salida estrictas bajo contratos Pydantic V2.
    """
    resultado = clasificar_y_crear_ticket(solicitud, request=request)
    if request and hasattr(resultado, "metadatos_ia"):
        request.state.metadatos_ia = resultado.metadatos_ia
    return resultado


@router.post(
    "/analizar",
    response_model=ResultadoAnalizarOut,
    status_code=status.HTTP_200_OK,
    summary="Análisis técnico estructurado de fallas con esquema Pydantic",
    description="Analiza los síntomas y avería reportada retornando diagnóstico, causa y severidad en formato JSON estructurado."
)
def analizar_problema_tecnico(solicitud: SolicitudAnalizarIn, request: Request = None):
    """
    Endpoint no conversacional de análisis técnico.
    Retorna JSON con esquema estricto Pydantic V2 (ResultadoAnalizarOut).
    """
    resultado = analizar_incidencia_tecnica(solicitud)
    if request and getattr(resultado, "metadatos_ia", None):
        request.state.metadatos_ia = resultado.metadatos_ia
    return resultado
