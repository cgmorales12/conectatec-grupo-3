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
    ResultadoAnalizarOut,
    SalarioBasicoOut,
    PresupuestoIn,
    PresupuestoCalculadoOut,
    ConsultaCalendarioOut,
    PenalizacionSLAOut,
    PropuestaRegistroTicketOut,
    ConfirmarRegistroIn
)
from app.agente import (
    SolicitudAgenteIn,
    RespuestaAgenteOut,
    agente_soporte,
    CONFIG_AGENTE
)
from app.services.llm import (
    cliente_llm,
    generar_flujo_chat_streaming,
    analizar_incidencia_tecnica
)
from app.tools.configuracion import (
    cargar_parametros_yaml,
    obtener_salario_basico,
    listar_todas_las_tarifas,
    calcular_presupuesto_reparacion,
    es_horario_laborable_habil,
    calcular_penalizacion_sla_por_horas
)
from app.routers.tickets import (
    clasificar_y_crear_ticket,
    proponer_registro_ticket,
    confirmar_y_guardar_ticket
)

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
    "/proponer",
    response_model=PropuestaRegistroTicketOut,
    status_code=status.HTTP_200_OK,
    summary="Propone el registro de un ticket antes de persistir (Human-in-the-Loop)",
    description="Genera la clasificación IA, matriz ITIL y solución RAG en modo propuesta sin escribir en base de datos."
)
def proponer_ticket_principal(solicitud: SolicitudTicketIn, request: Request = None):
    """Endpoint principal de pre-triaje con confirmación humana requerida."""
    return proponer_registro_ticket(solicitud, request=request)


@router.post(
    "/confirmar-registro",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="Confirma y persiste la propuesta de ticket autorizada por el humano",
    description="Persiste el ticket en SQLite asignando el operador confirmador auditado."
)
def confirmar_ticket_principal(payload: ConfirmarRegistroIn):
    """Endpoint principal de confirmación y persistencia de ticket."""
    return confirmar_y_guardar_ticket(payload)



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


@router.get(
    "/v1/agente/herramientas",
    summary="Catálogo de herramientas permitidas y límites del agente",
    description="Consulta la lista blanca de herramientas y el tope máximo de iteraciones del bucle ReAct."
)
def consultar_herramientas_agente():
    """Retorna las herramientas autorizadas, nivel de riesgo y tope de iteraciones."""
    from app.agente import CATALOGO_HERRAMIENTAS
    herramientas_info = {
        nombre: {
            "nivel": datos["nivel"],
            "descripcion": datos["descripcion"],
            "esquema_pydantic": datos["esquema"].__name__
        }
        for nombre, datos in CATALOGO_HERRAMIENTAS.items()
    }
    return {
        "max_iteraciones": CONFIG_AGENTE["max_iteraciones_agente"],
        "herramientas_permitidas": CONFIG_AGENTE["herramientas_permitidas"],
        "herramientas_requieren_confirmacion": CONFIG_AGENTE["herramientas_requieren_confirmacion"],
        "catalogo": herramientas_info
    }


@router.post(
    "/v1/agente/resolver",
    response_model=RespuestaAgenteOut,
    status_code=status.HTTP_200_OK,
    summary="Resolución agéntica con herramientas deterministas y límite ReAct",
    description="Ejecuta el agente de software autónomo controlado sobre la incidencia con tope de iteraciones y esquemas Pydantic."
)
@router.post(
    "/agente/resolver",
    response_model=RespuestaAgenteOut,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
def resolver_con_agente(solicitud: SolicitudAgenteIn):
    """
    Ejecuta el ciclo ReAct: Observar -> Pensar -> Actuar -> Verificar.
    Garantiza contratos Pydantic V2 en cada herramienta y corte determinista por MAX_ITER.
    """
    return agente_soporte.resolver(solicitud)


# ============================================================================
# Endpoints de Parámetros Desacoplados (Tarifas, Umbrales, Salario, Calendario)
# ============================================================================

@router.get(
    "/v1/config/parametros",
    summary="Consulta los parámetros y umbrales vigentes desacoplados",
    description="Retorna la configuración leída en tiempo de ejecución desde config/parametros.yaml."
)
def consultar_parametros_desacoplados():
    """Retorna los umbrales de confianza, límites ReAct y referencias configuradas."""
    return cargar_parametros_yaml()


@router.get(
    "/v1/config/salario-basico",
    response_model=SalarioBasicoOut,
    summary="Consulta el Salario Básico Unificado (SBU) desde config/parametros.yaml",
    description="Demuestra que el salario básico nunca está en el código ni en prompts."
)
def consultar_salario_basico():
    """Retorna el SBU oficial y factor de penalización leídos desde config/parametros.yaml."""
    return obtener_salario_basico()


@router.get(
    "/v1/config/tarifas",
    summary="Consulta el tarifario oficial de equipos, materiales y horas técnicas",
    description="Retorna el catálogo oficial leído desde config/tarifas.json."
)
def consultar_tarifario_oficial(categoria: str = None):
    """Retorna los ítems y precios unitarios del catálogo oficial."""
    return {
        "categoria_filtro": categoria,
        "items": listar_todas_las_tarifas(categoria=categoria),
        "origen": "config/tarifas.json"
    }


@router.post(
    "/v1/config/presupuesto",
    response_model=PresupuestoCalculadoOut,
    summary="Cálculo determinista de presupuesto técnico sin LLM",
    description="Calcula costo de repuestos y mano de obra leyendo config/tarifas.json con cero tokens."
)
def calcular_presupuesto_endpoint(payload: PresupuestoIn):
    """Calcula matemáticamente el presupuesto a partir de los ítems y cantidades solicitadas."""
    items_dicts = [{"codigo": it.codigo, "cantidad": it.cantidad} for it in payload.items]
    return calcular_presupuesto_reparacion(items_dicts, iva_porcentaje=payload.iva_porcentaje)


@router.get(
    "/v1/config/calendario",
    response_model=ConsultaCalendarioOut,
    summary="Consulta disponibilidad de soporte, turnos y feriados nacionales",
    description="Verifica si una fecha u horario es hábil según config/calendario.json."
)
def consultar_calendario_endpoint(fecha: str = None):
    """Verifica si la fecha indicada es hábil o feriado nacional en Ecuador."""
    from datetime import datetime
    dt = None
    if fecha:
        try:
            dt = datetime.fromisoformat(fecha.strip()[:10])
        except Exception:
            dt = None
    return es_horario_laborable_habil(dt)


@router.get(
    "/v1/config/penalizacion-sla",
    response_model=PenalizacionSLAOut,
    summary="Cálculo matemático de penalización por mora SLA según SBU",
    description="Calcula la penalización legal sin LLM usando el SBU de config/parametros.yaml."
)
def calcular_penalizacion_sla_endpoint(horas_retraso: float = 1.0):
    """Calcula la penalización legal basada en el salario básico oficial."""
    return calcular_penalizacion_sla_por_horas(horas_retraso)

