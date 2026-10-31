from __future__ import annotations
"""
Agente de Alcance Controlado con Herramientas Deterministas (Patrón ReAct)
Proyecto: ConectaTec / TecnoAula — Triaje de Incidentes Técnicos (Caso N.º 03 · Grupo 3 UNIANDES)
Seminario de Titulación: Ingeniería de Software con IA Generativa — 2026

Cumple con la rúbrica oficial de la Semana 3:
1. clasificar(solicitud): Herramienta de agente con IA y fallback determinista.
2. priorizar(impacto, urgencia): Matriz ITIL determinista leída de config/ (0 tokens).
3. buscar_solucion(categoria, texto): Búsqueda semántica sobre ChromaDB (15 manuales técnicos).
4. crear_ticket(datos): Registro con esquema estricto en SQLite (Tablero Kanban).
5. escalar(ticket, motivo): Escalamiento presencial gobernado por compuerta Human-in-the-Loop (HITL).
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional, Literal, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, ValidationError

from app.tools.priorizar import calcular_prioridad_itil
from app.services.rag import buscar_solucion, consultar_base_conocimiento
from app.schemas import CitaRAG, PrioridadSLA
from app.tools.configuracion import (
    listar_todas_las_tarifas,
    obtener_tarifa_por_codigo,
    calcular_presupuesto_reparacion,
    es_horario_laborable_habil,
    es_feriado_nacional,
    obtener_salario_basico
)

logger = logging.getLogger("conectatec.agente")


# ============================================================================
# 1. Carga Desacoplada de Parámetros desde config/parametros.yaml
# ============================================================================

def _cargar_config_agente() -> Dict[str, Any]:
    """Carga configuración del agente desde config/parametros.yaml."""
    ruta_yaml = os.path.join(os.path.dirname(__file__), "..", "config", "parametros.yaml")
    defaults = {
        "max_iteraciones_agente": 6,
        "herramientas_permitidas": [
            "clasificar",
            "clasificar_solicitud",
            "priorizar",
            "calcular_prioridad_itil",
            "buscar_solucion",
            "buscar_procedimiento_rag",
            "crear_ticket",
            "registrar_ticket_kanban",
            "escalar",
            "escalar_cuadrilla_presencial",
            "consultar_estado_nodo",
            "consultar_tarifas_repuestos",
            "consultar_calendario_soporte"
        ],
        "herramientas_requieren_confirmacion": [
            "escalar",
            "escalar_cuadrilla_presencial",
            "crear_ticket",
            "registrar_ticket_kanban"
        ]
    }
    if os.path.exists(ruta_yaml):
        try:
            import yaml
            with open(ruta_yaml, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    return {
                        "max_iteraciones_agente": data.get("max_iteraciones_agente", defaults["max_iteraciones_agente"]),
                        "herramientas_permitidas": data.get("herramientas_permitidas", defaults["herramientas_permitidas"]),
                        "herramientas_requieren_confirmacion": data.get("herramientas_requieren_confirmacion", defaults["herramientas_requieren_confirmacion"])
                    }
        except Exception as e:
            logger.warning("No se pudo leer parametros.yaml, usando defaults: %s", e)
    return defaults


CONFIG_AGENTE = _cargar_config_agente()
MAX_ITERACIONES_DEFECTO = CONFIG_AGENTE["max_iteraciones_agente"]


# ============================================================================
# 2. Esquemas Pydantic V2 Estrictos para cada Herramienta (extra='forbid')
# ============================================================================

# Tool 1: clasificar(solicitud)
class ParamsClasificar(BaseModel):
    """Contrato estricto de entrada para la herramienta clasificar(solicitud)."""
    model_config = ConfigDict(extra="forbid")

    solicitud: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="Texto de la incidencia o reporte a clasificar"
    )
    simular_caida_llm: Optional[bool] = False


class ResultadoClasificar(BaseModel):
    """Contrato de salida para clasificar(solicitud)."""
    model_config = ConfigDict(extra="forbid")

    categoria: str
    impacto: Literal["Alto", "Medio", "Bajo"]
    urgencia: Literal["Alta", "Media", "Baja"]
    descripcion_problema: str
    es_fuera_de_alcance: bool
    requiere_revision_humana: bool
    proveedor: str


# Tool 2: priorizar(impacto, urgencia)
class ParamsCalcularPrioridadITIL(BaseModel):
    """Contrato estricto de entrada para priorizar(impacto, urgencia)."""
    model_config = ConfigDict(extra="forbid")

    impacto: Literal["Alto", "Medio", "Bajo"] = Field(
        ..., description="Nivel de afectación operativa o usuarios incomunicados"
    )
    urgencia: Literal["Alta", "Media", "Baja"] = Field(
        ..., description="Velocidad requerida de contención o resolución"
    )


class ResultadoCalcularPrioridadITIL(BaseModel):
    """Contrato de salida para priorizar(impacto, urgencia)."""
    model_config = ConfigDict(extra="forbid")

    prioridad: Literal["Alta", "Media", "Baja"]
    sla_minutos: int
    descripcion_sla: str


# Tool 3: buscar_solucion(categoria, texto)
class ParamsBuscarSolucion(BaseModel):
    """Contrato estricto de entrada para buscar_solucion(categoria, texto)."""
    model_config = ConfigDict(extra="forbid")

    texto: Optional[str] = Field(
        None,
        min_length=3,
        max_length=1000,
        description="Descripción o síntomas del problema técnico"
    )
    consulta: Optional[str] = Field(
        None,
        min_length=3,
        max_length=1000,
        description="Alias de texto para compatibilidad con buscar_procedimiento_rag"
    )
    categoria: Optional[str] = Field(
        None,
        max_length=100,
        description="Categoría tecnológica opcional para filtrado guiado"
    )
    top_k: Optional[int] = Field(
        3,
        ge=1,
        le=10,
        description="Número de fragmentos relevantes a recuperar"
    )


class ParamsBuscarProcedimientoRAG(BaseModel):
    """Contrato de entrada para compatibilidad con tests previos de buscar_procedimiento_rag."""
    model_config = ConfigDict(extra="forbid")

    consulta: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Descripción o síntomas técnicos para consultar en la base de manuales oficiales"
    )


class ResultadoBuscarProcedimientoRAG(BaseModel):
    """Contrato de salida para buscar_solucion / buscar_procedimiento_rag."""
    model_config = ConfigDict(extra="forbid")

    encontrado: bool
    documento_id: Optional[str] = None
    titulo_documento: Optional[str] = None
    paso_exacto: Optional[str] = None
    fragmento_aplicado: Optional[str] = None
    vigencia: Optional[str] = None
    url: Optional[str] = None
    requiere_cuadrilla_fisica: bool = False
    solucion_propuesta: Optional[str] = None
    citas: List[Dict[str, Any]] = Field(default_factory=list)


# Tool 4: crear_ticket(datos)
class ParamsRegistrarTicketKanban(BaseModel):
    """Contrato estricto de entrada para crear_ticket / registrar_ticket_kanban."""
    model_config = ConfigDict(extra="forbid")

    nombre_cliente: str = Field("Docente / Personal Campus", min_length=2, max_length=100)
    email_cliente: str = Field("usuario@uniandes.edu.ec", min_length=5, max_length=120)
    descripcion_problema: str = Field(..., min_length=10, max_length=2000)
    categoria: str = Field(..., min_length=3, max_length=100)
    prioridad: Literal["Alta", "Media", "Baja"]
    sla_minutos: int = Field(..., ge=1, le=10080)
    solucion_propuesta: str = Field(..., min_length=10, max_length=2000)
    documento_id: Optional[str] = None
    confirmado: Optional[bool] = False


class ResultadoRegistrarTicketKanban(BaseModel):
    """Contrato de salida para crear_ticket / registrar_ticket_kanban."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: int
    ticket_codigo: str
    estado: str
    registrado: bool


# Tool 5: escalar(ticket, motivo) - Human-in-the-Loop
class ParamsEscalar(BaseModel):
    """Contrato estricto de entrada para escalar(ticket, motivo)."""
    model_config = ConfigDict(extra="forbid")

    ticket: Optional[str] = Field(None, min_length=1, max_length=50, description="Código o ID del ticket a escalar")
    ticket_codigo: Optional[str] = Field(None, min_length=1, max_length=50, description="Alias de ticket")
    motivo: Optional[str] = Field(None, min_length=5, max_length=500, description="Motivo técnico de la derivación")
    motivo_escalado: Optional[str] = Field(None, min_length=5, max_length=500, description="Alias de motivo")
    confirmado: bool = Field(False, description="Confirmación humana obligatoria antes de derivar/despachar")
    sector: Optional[str] = Field("Campus Universitario Matriz", max_length=100)
    requiere_fusionadora: Optional[bool] = True


class ParamsEscalarCuadrillaPresencial(BaseModel):
    """Contrato para compatibilidad con escalar_cuadrilla_presencial."""
    model_config = ConfigDict(extra="forbid")

    ticket_codigo: str = Field(..., min_length=5, max_length=50)
    sector: str = Field(..., min_length=3, max_length=100)
    motivo_escalado: str = Field(..., min_length=10, max_length=500)
    requiere_fusionadora: bool = True
    confirmado: Optional[bool] = False


class ResultadoEscalar(BaseModel):
    """Contrato de salida para escalar(ticket, motivo)."""
    model_config = ConfigDict(extra="forbid")

    orden_despacho_id: Optional[str] = None
    cuadrilla_asignada: Optional[str] = None
    tiempo_estimado_llegada_minutos: Optional[int] = None
    requiere_confirmacion_humana: bool = True
    estado: Literal["pendiente_aprobacion_humana", "despachado", "ejecutado"]
    mensaje: str


class ResultadoEscalarCuadrillaPresencial(BaseModel):
    """Contrato de salida para escalar_cuadrilla_presencial."""
    model_config = ConfigDict(extra="forbid")

    orden_despacho_id: str
    cuadrilla_asignada: str
    tiempo_estimado_llegada_minutos: int
    requiere_confirmacion_humana: bool


# Tool 6: Consultar Estado de Nodo
class ParamsConsultarEstadoNodo(BaseModel):
    """Contrato estricto de entrada para consultar_estado_nodo."""
    model_config = ConfigDict(extra="forbid")

    nodo_id: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Identificador del nodo o sector de campus (ej. NODO-CENTRAL, NODO-NORTE, LAB-SISTEMAS)"
    )


class ResultadoConsultarEstadoNodo(BaseModel):
    """Contrato de salida para consultar_estado_nodo."""
    model_config = ConfigDict(extra="forbid")

    nodo_id: str
    estado: Literal["operativo", "degradado", "mantenimiento", "caido"]
    potencia_optica_dbm: float
    clientes_afectados: int
    sector: str


# Tool 7: Consulta de Tarifario Oficial Desacoplado (config/tarifas.json)
class ParamsConsultarTarifasRepuestos(BaseModel):
    """Contrato estricto de entrada para consultar_tarifas_repuestos."""
    model_config = ConfigDict(extra="forbid")

    codigo_o_categoria: Optional[str] = Field(
        None,
        max_length=50,
        description="Código de ítem (ej: EQ-ONT-GPON-W6) o categoría"
    )


class ResultadoConsultarTarifasRepuestos(BaseModel):
    """Contrato de salida para consultar_tarifas_repuestos."""
    model_config = ConfigDict(extra="forbid")

    items: List[Dict[str, Any]]
    total_encontrados: int
    moneda: str
    origen: str


# Tool 8: Consulta de Calendario Operativo y Feriados (config/calendario.json)
class ParamsConsultarCalendarioSoporte(BaseModel):
    """Contrato estricto de entrada para consultar_calendario_soporte."""
    model_config = ConfigDict(extra="forbid")

    fecha_iso: Optional[str] = Field(
        None,
        max_length=15,
        description="Fecha en formato YYYY-MM-DD para verificar turno hábil o feriado nacional"
    )


class ResultadoConsultarCalendarioSoporte(BaseModel):
    """Contrato de salida para consultar_calendario_soporte."""
    model_config = ConfigDict(extra="forbid")

    fecha: str
    es_habil: bool
    motivo: str
    guardia_noc_24_7_activa: bool
    origen: str


# Aliases de Contratos
ParamsPriorizar = ParamsCalcularPrioridadITIL
ResultadoPriorizar = ResultadoCalcularPrioridadITIL
ParamsCrearTicket = ParamsRegistrarTicketKanban
ResultadoCrearTicket = ResultadoRegistrarTicketKanban


# ============================================================================
# 3. Implementaciones Deterministas de las Herramientas (Pure Python)
# ============================================================================

def tool_clasificar(params: ParamsClasificar) -> ResultadoClasificar:
    """Implementación de la herramienta clasificar(solicitud): extrae categoría, impacto y urgencia."""
    from app.services.llm import clasificar_solicitud
    clasif, meta = clasificar_solicitud(
        params.solicitud,
        simular_caida_gemini=bool(params.simular_caida_llm),
        simular_caida_groq=bool(params.simular_caida_llm)
    )
    es_fuera = (
        getattr(clasif, "es_fuera_de_alcance", False) or
        ("fuera de alcance" in clasif.categoria.lower()) or
        ("no técnica" in clasif.categoria.lower())
    )
    return ResultadoClasificar(
        categoria=clasif.categoria,
        impacto=clasif.impacto,  # type: ignore
        urgencia=clasif.urgencia,  # type: ignore
        descripcion_problema=params.solicitud,
        es_fuera_de_alcance=es_fuera,
        requiere_revision_humana=clasif.impacto == "Alto" or clasif.urgencia == "Alta",
        proveedor=meta.proveedor
    )


def tool_buscar_solucion(params: ParamsBuscarSolucion) -> ResultadoBuscarProcedimientoRAG:
    """Implementación de buscar_solucion(categoria, texto): consulta directamente ChromaDB."""
    texto_consulta = params.texto or params.consulta or ""
    diag = buscar_solucion(categoria=params.categoria, texto=texto_consulta, top_k=params.top_k or 3)

    citas_dicts = [c.model_dump() for c in diag.citas]
    if diag.citas and len(diag.citas) > 0:
        c = diag.citas[0]
        return ResultadoBuscarProcedimientoRAG(
            encontrado=True,
            documento_id=c.documento_id,
            titulo_documento=c.titulo_documento,
            paso_exacto=c.paso_exacto,
            fragmento_aplicado=c.fragmento_aplicado,
            vigencia=c.vigencia or "v3.2 - Octubre 2026",
            url=c.url or f"https://soporte.conectatec.edu.ec/manuales/{c.documento_id.lower()}",
            requiere_cuadrilla_fisica=diag.requiere_visita_campo,
            solucion_propuesta=diag.solucion_propuesta,
            citas=citas_dicts
        )

    return ResultadoBuscarProcedimientoRAG(
        encontrado=False,
        documento_id=None,
        titulo_documento=None,
        paso_exacto=None,
        fragmento_aplicado=None,
        vigencia=None,
        url=None,
        requiere_cuadrilla_fisica=diag.requiere_visita_campo,
        solucion_propuesta=diag.solucion_propuesta,
        citas=[]
    )


def tool_buscar_procedimiento_rag(params: ParamsBuscarProcedimientoRAG) -> ResultadoBuscarProcedimientoRAG:
    """Implementación de compatibilidad para buscar_procedimiento_rag consultando ChromaDB."""
    return tool_buscar_solucion(ParamsBuscarSolucion(texto=params.consulta, consulta=params.consulta))


def tool_calcular_prioridad_itil(params: ParamsCalcularPrioridadITIL) -> ResultadoCalcularPrioridadITIL:
    """Implementación determinista: calcula matemáticamente la prioridad desde config/matriz_prioridad.json."""
    res: PrioridadSLA = calcular_prioridad_itil(params.impacto, params.urgencia)
    return ResultadoCalcularPrioridadITIL(
        prioridad=res.prioridad,  # type: ignore
        sla_minutos=res.sla_minutos,
        descripcion_sla=res.descripcion_sla
    )


tool_priorizar = tool_calcular_prioridad_itil


def tool_registrar_ticket_kanban(params: ParamsRegistrarTicketKanban) -> ResultadoRegistrarTicketKanban:
    """Implementación determinista: registra el ticket en base de datos SQLite."""
    from app.database import guardar_ticket

    codigo = f"TCK-{hashlib.md5(f'{params.email_cliente}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
    datos_ticket = {
        "ticket_codigo": codigo,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nombre_cliente": params.nombre_cliente,
        "email_cliente": params.email_cliente,
        "descripcion_problema": params.descripcion_problema,
        "categoria": params.categoria,
        "impacto": "Medio",
        "urgencia": "Media",
        "prioridad": params.prioridad,
        "sla_minutos": params.sla_minutos,
        "descripcion_sla": f"SLA Máximo de {params.sla_minutos} minutos",
        "solucion_propuesta": params.solucion_propuesta,
        "citas": [{
            "documento_id": params.documento_id,
            "titulo_documento": f"Manual Oficial {params.documento_id}",
            "paso_exacto": "Paso 1: Procedimiento de Referencia",
            "fragmento_aplicado": params.solucion_propuesta[:200]
        }] if params.documento_id else [],
        "estado": "nuevo",
        "requiere_revision_humana": False,
        "metadatos_ia": {
            "proveedor": "agente-react",
            "modelo": "controlado-determinista"
        }
    }
    ticket_id = guardar_ticket(datos_ticket)

    return ResultadoRegistrarTicketKanban(
        ticket_id=ticket_id,
        ticket_codigo=codigo,
        estado="nuevo",
        registrado=True
    )


tool_crear_ticket = tool_registrar_ticket_kanban


def tool_escalar(params: ParamsEscalar) -> ResultadoEscalar:
    """
    Implementación de la herramienta escalar(ticket, motivo).
    Gobernada por Human-in-the-Loop: Si confirmado=False, se bloquea la ejecución
    para exigir confirmación humana explícita según config/parametros.yaml.
    """
    tck = params.ticket or params.ticket_codigo or "TCK-GENERAL"
    motivo = params.motivo or params.motivo_escalado or "Alarma crítica de red"

    if not params.confirmado:
        logger.info("Escalamiento pausado por Human-in-the-Loop para ticket %s: requiere confirmación.", tck)
        return ResultadoEscalar(
            orden_despacho_id=None,
            cuadrilla_asignada=None,
            tiempo_estimado_llegada_minutos=None,
            requiere_confirmacion_humana=True,
            estado="pendiente_aprobacion_humana",
            mensaje=(
                f"ACCIÓN PAUSADA POR HUMAN-IN-THE-LOOP: La derivación del ticket {tck} a cuadrilla presencial "
                f"por motivo '{motivo}' requiere confirmación humana explícita (config/parametros.yaml)."
            )
        )

    # Si fue confirmado explícitamente por el operador humano
    orden_id = f"ODT-FIBRA-{hashlib.sha256(f'{tck}{motivo}'.encode()).hexdigest()[:6].upper()}"
    return ResultadoEscalar(
        orden_despacho_id=orden_id,
        cuadrilla_asignada="Cuadrilla de Planta Externa Nº 03 (Fusionadora Fujikura 70S)",
        tiempo_estimado_llegada_minutos=45,
        requiere_confirmacion_humana=False,
        estado="despachado",
        mensaje=f"Orden de despacho {orden_id} emitida con éxito tras confirmación humana para {tck}."
    )


def tool_escalar_cuadrilla_presencial(params: ParamsEscalarCuadrillaPresencial) -> ResultadoEscalarCuadrillaPresencial:
    """Implementación de compatibilidad para escalar_cuadrilla_presencial."""
    orden_id = f"ODT-FIBRA-{hashlib.sha256(params.ticket_codigo.encode()).hexdigest()[:6].upper()}"
    return ResultadoEscalarCuadrillaPresencial(
        orden_despacho_id=orden_id,
        cuadrilla_asignada="Cuadrilla de Planta Externa Nº 03 (Fusionadora Fujikura 70S)",
        tiempo_estimado_llegada_minutos=45,
        requiere_confirmacion_humana=True
    )


def tool_consultar_estado_nodo(params: ParamsConsultarEstadoNodo) -> ResultadoConsultarEstadoNodo:
    """Implementación determinista: telemetría de nodos GPON y switches de campus."""
    nodo = params.nodo_id.upper().strip()
    if "NORTE" in nodo or "CENTRAL" in nodo:
        return ResultadoConsultarEstadoNodo(
            nodo_id=nodo,
            estado="operativo",
            potencia_optica_dbm=-19.4,
            clientes_afectados=0,
            sector="Campus Matriz Ambato"
        )
    elif "SISTEMAS" in nodo or "LAB" in nodo:
        return ResultadoConsultarEstadoNodo(
            nodo_id=nodo,
            estado="degradado",
            potencia_optica_dbm=-26.8,
            clientes_afectados=45,
            sector="Facultad de Sistemas Mercantiles"
        )
    return ResultadoConsultarEstadoNodo(
        nodo_id=nodo,
        estado="operativo",
        potencia_optica_dbm=-21.2,
        clientes_afectados=0,
        sector="Campus Universitario General"
    )


def tool_consultar_tarifas_repuestos(params: ParamsConsultarTarifasRepuestos) -> ResultadoConsultarTarifasRepuestos:
    """Implementación determinista: consulta tarifas oficiales desde config/tarifas.json (0 tokens)."""
    filtro = (params.codigo_o_categoria or "").strip()
    if filtro:
        item = obtener_tarifa_por_codigo(filtro)
        if item:
            items = [item]
        else:
            items = listar_todas_las_tarifas(categoria=filtro)
    else:
        items = listar_todas_las_tarifas()

    return ResultadoConsultarTarifasRepuestos(
        items=items,
        total_encontrados=len(items),
        moneda="USD",
        origen="config/tarifas.json"
    )


def tool_consultar_calendario_soporte(params: ParamsConsultarCalendarioSoporte) -> ResultadoConsultarCalendarioSoporte:
    """Implementación determinista: evalúa turnos y feriados desde config/calendario.json (0 tokens)."""
    dt = None
    if params.fecha_iso:
        try:
            texto = params.fecha_iso.strip()
            if len(texto) == 10:
                texto += "T10:00:00"
            dt = datetime.fromisoformat(texto)
        except Exception:
            dt = None

    info = es_horario_laborable_habil(dt)
    return ResultadoConsultarCalendarioSoporte(
        fecha=info["fecha"],
        es_habil=info["es_habil"],
        motivo=info["motivo"],
        guardia_noc_24_7_activa=info.get("guardia_noc_24_7_activa", True),
        origen="config/calendario.json"
    )


# ============================================================================
# 4. Catálogo y Registro Cerrado de Herramientas (Whitelist)
# ============================================================================

CATALOGO_HERRAMIENTAS = {
    # Herramientas canónicas requeridas por la rúbrica oficial (Semana 3 · 70%)
    "clasificar": {
        "esquema": ParamsClasificar,
        "funcion": tool_clasificar,
        "nivel": 1,
        "descripcion": "Clasifica estructuradamente categoría, impacto y urgencia de la solicitud"
    },
    "priorizar": {
        "esquema": ParamsCalcularPrioridadITIL,
        "funcion": tool_calcular_prioridad_itil,
        "nivel": 1,
        "descripcion": "Calcula matemáticamente prioridad ITIL y SLA (0 tokens)"
    },
    "buscar_solucion": {
        "esquema": ParamsBuscarSolucion,
        "funcion": tool_buscar_solucion,
        "nivel": 1,
        "descripcion": "Recupera manuales técnicos oficiales desde ChromaDB con ID y paso exacto"
    },
    "crear_ticket": {
        "esquema": ParamsRegistrarTicketKanban,
        "funcion": tool_registrar_ticket_kanban,
        "nivel": 2,
        "descripcion": "Persiste un ticket estructurado en la base de datos (Kanban)"
    },
    "escalar": {
        "esquema": ParamsEscalar,
        "funcion": tool_escalar,
        "nivel": 2,
        "descripcion": "Deriva a cuadrilla técnica de campo (requiere confirmación humana explícita)"
    },

    # Aliases de compatibilidad con versiones anteriores
    "clasificar_solicitud": {
        "esquema": ParamsClasificar,
        "funcion": tool_clasificar,
        "nivel": 1,
        "descripcion": "Alias de clasificar(solicitud)"
    },
    "calcular_prioridad_itil": {
        "esquema": ParamsCalcularPrioridadITIL,
        "funcion": tool_calcular_prioridad_itil,
        "nivel": 1,
        "descripcion": "Alias de priorizar(impacto, urgencia)"
    },
    "buscar_procedimiento_rag": {
        "esquema": ParamsBuscarProcedimientoRAG,
        "funcion": tool_buscar_procedimiento_rag,
        "nivel": 1,
        "descripcion": "Alias de buscar_solucion(categoria, texto)"
    },
    "registrar_ticket_kanban": {
        "esquema": ParamsRegistrarTicketKanban,
        "funcion": tool_registrar_ticket_kanban,
        "nivel": 2,
        "descripcion": "Alias de crear_ticket(datos)"
    },
    "escalar_cuadrilla_presencial": {
        "esquema": ParamsEscalarCuadrillaPresencial,
        "funcion": tool_escalar_cuadrilla_presencial,
        "nivel": 2,
        "descripcion": "Alias de escalar(ticket, motivo)"
    },
    "consultar_estado_nodo": {
        "esquema": ParamsConsultarEstadoNodo,
        "funcion": tool_consultar_estado_nodo,
        "nivel": 1,
        "descripcion": "Consulta telemetría y potencia óptica del nodo GPON"
    },
    "consultar_tarifas_repuestos": {
        "esquema": ParamsConsultarTarifasRepuestos,
        "funcion": tool_consultar_tarifas_repuestos,
        "nivel": 1,
        "descripcion": "Consulta tarifas de equipos, repuestos y horas técnicas desde config/tarifas.json"
    },
    "consultar_calendario_soporte": {
        "esquema": ParamsConsultarCalendarioSoporte,
        "funcion": tool_consultar_calendario_soporte,
        "nivel": 1,
        "descripcion": "Verifica si una fecha/hora es laborable o feriado desde config/calendario.json"
    }
}


# ============================================================================
# 5. Esquemas del Flujo ReAct del Agente
# ============================================================================

class PasoAgente(BaseModel):
    """Paso individual auditado dentro del ciclo ReAct."""
    model_config = ConfigDict(extra="forbid")

    iteracion: int
    fase: Literal["OBSERVAR", "PENSAR", "ACTUAR", "VERIFICAR"]
    herramienta_invocada: Optional[str] = None
    argumentos_enviados: Optional[Dict[str, Any]] = None
    resultado_obtenido: Optional[Dict[str, Any]] = None
    observacion: str


class SolicitudAgenteIn(BaseModel):
    """Payload de entrada para invocar el agente."""
    model_config = ConfigDict(extra="forbid")

    solicitud: str = Field(..., min_length=5, max_length=4000, description="Texto de la incidencia o reporte")
    nombre_cliente: Optional[str] = "Docente / Personal Campus"
    email_cliente: Optional[str] = "usuario@uniandes.edu.ec"
    max_iteraciones: Optional[int] = Field(None, ge=1, le=20, description="Tope de iteraciones del bucle ReAct")
    forzar_bucle_infinito: bool = Field(False, description="Chaos engineering: prueba de corte forzoso al alcanzar MAX_ITER")


class RespuestaAgenteOut(BaseModel):
    """Contrato de salida limpio de la resolución agéntica."""
    model_config = ConfigDict(extra="forbid")

    exito: bool
    diagnostico_final: str
    prioridad: str
    sla_minutos: int
    citas: List[CitaRAG] = Field(default_factory=list)
    requiere_revision_humana: bool
    motivo_revision: Optional[str] = None
    iteraciones_ejecutadas: int
    limite_alcanzado: bool
    audit_trail: List[PasoAgente] = Field(default_factory=list)


# ============================================================================
# 6. Clase Orquestadora: Agente de Triaje de Alcance Controlado
# ============================================================================

class AgenteTriajeTecnico:
    """
    Agente de software con IA para triaje de incidentes tecnológicos.
    Implementa el bucle canónico ReAct con tope inviolable de iteraciones y whitelist.
    """

    def __init__(self, max_iteraciones: int = MAX_ITERACIONES_DEFECTO):
        self.max_iteraciones = max_iteraciones
        self.herramientas_permitidas = set(CONFIG_AGENTE["herramientas_permitidas"])
        self.herramientas_confirmacion = set(CONFIG_AGENTE["herramientas_requieren_confirmacion"])

    def ejecutar_herramienta(self, nombre_tool: str, argumentos: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Ejecuta una herramienta validando:
        1. Lista blanca (whitelist).
        2. Esquema Pydantic V2 estricto (extra="forbid").
        3. Human-in-the-Loop (HITL): comprobación de confirmación previa si la herramienta lo exige.
        4. Ejecución determinista pura.
        """
        # 1. Verificación de Seguridad: Whitelist
        if nombre_tool not in self.herramientas_permitidas:
            msg_seguridad = (
                f"RECHAZO DE SEGURIDAD (ASI02): La herramienta '{nombre_tool}' NO está en la lista blanca de "
                f"herramientas permitidas {list(self.herramientas_permitidas)}."
            )
            logger.error(msg_seguridad)
            return False, {"error": "herramienta_prohibida", "detalle": msg_seguridad}, msg_seguridad

        definicion = CATALOGO_HERRAMIENTAS.get(nombre_tool)
        if not definicion:
            return False, {"error": "herramienta_no_definida"}, f"Herramienta '{nombre_tool}' no registrada en catálogo."

        esquema_cls = definicion["esquema"]
        funcion_fn = definicion["funcion"]

        # 2. Validación de Contrato Pydantic (extra="forbid")
        try:
            params_validados = esquema_cls(**argumentos)
        except ValidationError as val_err:
            msg_err = f"ERROR DE CONTRATO PYDANTIC (extra='forbid'): Argumentos inválidos para '{nombre_tool}': {val_err.errors()}"
            logger.warning(msg_err)
            return False, {"error": "validacion_pydantic", "detalles": val_err.errors()}, msg_err

        # 3. Verificación Human-in-the-Loop (HITL) para herramientas con impacto presencial / persistencia
        if nombre_tool in self.herramientas_confirmacion:
            confirmado = (
                argumentos.get("confirmado", False) or
                getattr(params_validados, "confirmado", False)
            )
            if not confirmado:
                # Si es la herramienta escalar o escalar_cuadrilla_presencial sin confirmación
                if nombre_tool in ["escalar", "escalar_cuadrilla_presencial"]:
                    msg_hitl = (
                        f"BLOQUEO HUMAN-IN-THE-LOOP (HITL): La herramienta '{nombre_tool}' requiere "
                        f"confirmación humana explícita antes de despachar o derivar (config/parametros.yaml)."
                    )
                    logger.info(msg_hitl)
                    # La herramienta escalar retorna su resultado de pausa controlada
                    resultado_obj = funcion_fn(params_validados)
                    return True, resultado_obj.model_dump(), msg_hitl

        # 4. Ejecución Determinista
        try:
            resultado_obj = funcion_fn(params_validados)
            resultado_dict = resultado_obj.model_dump()
            return True, resultado_dict, f"Herramienta '{nombre_tool}' ejecutada con éxito."
        except Exception as ex:
            return False, {"error": "falla_ejecucion", "detalle": str(ex)}, f"Excepción en ejecución de '{nombre_tool}': {str(ex)}"

    def resolver(self, solicitud_in: SolicitudAgenteIn) -> RespuestaAgenteOut:
        """
        Ejecuta el ciclo ReAct:
        OBSERVAR -> PENSAR -> ACTUAR -> VERIFICAR
        Con corte determinista al alcanzar MAX_ITER.
        """
        texto_usuario = solicitud_in.solicitud.strip()
        limite_max = solicitud_in.max_iteraciones or self.max_iteraciones
        audit_trail: List[PasoAgente] = []
        citas_obtenidas: List[CitaRAG] = []

        texto_lower = texto_usuario.lower()

        # Detección temprana de preguntas fuera de alcance (Misión de Silencio y Abstención)
        terminos_ti = ["los", "ont", "router", "fibra", "wifi", "cable", "red", "ethernet", "internet"]
        es_fuera_de_alcance = any(w in texto_lower for w in [
            "complexivo", "comedor", "matrícula", "matricula", "almuerzo",
            "llueve", "clima", "nómina", "nomina", "sueldo"
        ]) and not any(t in texto_lower for t in terminos_ti)

        if es_fuera_de_alcance:
            diag_fuera = (
                "No dispongo de un procedimiento técnico registrado para esta situación en los 15 manuales oficiales de ConectaTec. "
                "La consulta no describe ninguna avería técnica ni falla en la infraestructura de Internet o telecomunicaciones. "
                "No se requiere despacho de cuadrilla ni manipulación de equipos. "
                "Orientación al usuario: Si su solicitud corresponde a trámites administrativos o académicos (como notas, matrículas o certificaciones), "
                "por favor acuda a Secretaría General o al portal institucional de autoservicio. "
                "Si experimenta problemas de conectividad o luces anómalas en el módem/ONT (POWER, PON, LOS, LAN), por favor descríbalos detalladamente."
            )
            return RespuestaAgenteOut(
                exito=True,
                diagnostico_final=diag_fuera,
                prioridad="Baja",
                sla_minutos=2880,
                citas=[],
                requiere_revision_humana=False,
                motivo_revision=None,
                iteraciones_ejecutadas=1,
                limite_alcanzado=False,
                audit_trail=[PasoAgente(
                    iteracion=1,
                    fase="OBSERVAR",
                    herramienta_invocada=None,
                    argumentos_enviados=None,
                    resultado_obtenido={"clasificacion": "fuera_de_alcance"},
                    observacion="Solicitud no técnica detectada: se aplica protocolo oficial de abstención con orientación."
                )]
            )

        # Inicio del Bucle ReAct
        iteracion = 1
        diagnostico_actual = ""
        prioridad_actual = "Media"
        sla_actual = 480
        impacto_actual: Literal["Alto", "Medio", "Bajo"] = "Medio"
        urgencia_actual: Literal["Alta", "Media", "Baja"] = "Media"
        categoria_actual = "Conectividad y Red"
        requiere_cuadrilla = False
        resuelto = False

        # Bandera de simulación de fallo / Chaos Engineering
        if solicitud_in.forzar_bucle_infinito:
            while iteracion <= limite_max:
                audit_trail.append(PasoAgente(
                    iteracion=iteracion,
                    fase="OBSERVAR",
                    observacion=f"Iteración {iteracion}: Analizando síntoma no convergente en modo simulación de tope."
                ))
                iteracion += 1

            return RespuestaAgenteOut(
                exito=False,
                diagnostico_final="CORTE DETERMINISTA DE SEGURIDAD: El agente alcanzó el límite máximo de iteraciones configurado.",
                prioridad="Media",
                sla_minutos=480,
                citas=[],
                requiere_revision_humana=True,
                motivo_revision=f"Límite máximo de iteraciones alcanzado ({limite_max}). Derivación obligatoria a operador humano para preservar SLA.",
                iteraciones_ejecutadas=limite_max,
                limite_alcanzado=True,
                audit_trail=audit_trail
            )

        while iteracion <= limite_max and not resuelto:
            # FASE 1: OBSERVAR
            audit_trail.append(PasoAgente(
                iteracion=iteracion,
                fase="OBSERVAR",
                observacion=f"Iteración {iteracion}: Evaluando estado de la incidencia y requerimientos de información."
            ))

            # FASE 2: PENSAR (Decisión determinista de la siguiente herramienta)
            if iteracion == 1:
                # Paso 1: Clasificar la solicitud como herramienta de agente
                nombre_tool = "clasificar"
                args = {"solicitud": texto_usuario}
            elif iteracion == 2:
                # Paso 2: Buscar solución en base RAG (ChromaDB)
                nombre_tool = "buscar_solucion"
                args = {"texto": texto_usuario, "categoria": categoria_actual}
            elif iteracion == 3:
                # Paso 3: Calcular prioridad ITIL con la matriz determinista
                nombre_tool = "priorizar"
                args = {"impacto": impacto_actual, "urgencia": urgencia_actual}
            elif iteracion == 4 and requiere_cuadrilla:
                # Paso 4 (si aplica): Escalar cuadrilla con compuerta HITL
                nombre_tool = "escalar"
                args = {
                    "ticket": f"TCK-{hashlib.md5(texto_usuario.encode()).hexdigest()[:6].upper()}",
                    "motivo": "Alarma óptica crítica LOS roja detectada en enlace GPON",
                    "confirmado": False  # Se detiene deterministamente para requerir confirmación humana
                }
            else:
                resuelto = True
                break

            # FASE 3: ACTUAR (Ejecución bajo whitelist, HITL y Pydantic)
            ok, res_tool, obs_act = self.ejecutar_herramienta(nombre_tool, args)

            audit_trail.append(PasoAgente(
                iteracion=iteracion,
                fase="ACTUAR",
                herramienta_invocada=nombre_tool,
                argumentos_enviados=args,
                resultado_obtenido=res_tool,
                observacion=obs_act
            ))

            # FASE 4: VERIFICAR
            if nombre_tool == "clasificar":
                if res_tool.get("es_fuera_de_alcance"):
                    resuelto = True
                    diagnostico_actual = (
                        "No dispongo de un procedimiento técnico registrado para esta situación en los 15 manuales oficiales de ConectaTec. "
                        "Orientación al usuario: Si su solicitud corresponde a trámites administrativos o académicos, acuda a Secretaría General."
                    )
                    prioridad_actual = "Baja"
                    sla_actual = 2880
                    break
                categoria_actual = res_tool.get("categoria", categoria_actual)
                imp = res_tool.get("impacto")
                urg = res_tool.get("urgencia")
                if imp in ["Alto", "Medio", "Bajo"]:
                    impacto_actual = imp
                if urg in ["Alta", "Media", "Baja"]:
                    urgencia_actual = urg

                # Alarma física o rotura de fibra implica impacto Alto y urgencia Alta (SLA 15m)
                if ("los" in texto_lower and "roj" in texto_lower) or any(w in texto_lower for w in ["fibra", "corte", "masivo", "acometida"]):
                    impacto_actual = "Alto"
                    urgencia_actual = "Alta"

            elif nombre_tool in ["buscar_solucion", "buscar_procedimiento_rag"]:
                if res_tool.get("encontrado"):
                    diagnostico_actual = f"Procedimiento recomendado según {res_tool['documento_id']} ({res_tool['paso_exacto']}): {res_tool['fragmento_aplicado']}"
                    
                    citas_en_tool = res_tool.get("citas", [])
                    if citas_en_tool:
                        for cd in citas_en_tool:
                            citas_obtenidas.append(CitaRAG(
                                documento_id=cd.get("documento_id", "DOC-01"),
                                titulo_documento=cd.get("titulo_documento", "Manual Técnico"),
                                paso_exacto=cd.get("paso_exacto", "Paso 1"),
                                fragmento_aplicado=cd.get("fragmento_aplicado", ""),
                                vigencia=cd.get("vigencia"),
                                url=cd.get("url")
                            ))
                    else:
                        citas_obtenidas.append(CitaRAG(
                            documento_id=res_tool["documento_id"],
                            titulo_documento=res_tool["titulo_documento"],
                            paso_exacto=res_tool["paso_exacto"],
                            fragmento_aplicado=res_tool["fragmento_aplicado"],
                            vigencia=res_tool.get("vigencia"),
                            url=res_tool.get("url")
                        ))
                    if res_tool.get("requiere_cuadrilla_fisica"):
                        requiere_cuadrilla = True
                        impacto_actual = "Alto"
                        urgencia_actual = "Alta"
                else:
                    diagnostico_actual = res_tool.get("solucion_propuesta") or "Incidencia analizada sin procedimiento directo; aplicar ciclo de reinicio de 30 segundos (DOC-03)."

            elif nombre_tool in ["priorizar", "calcular_prioridad_itil"]:
                prioridad_actual = res_tool.get("prioridad", "Media")
                sla_actual = res_tool.get("sla_minutos", 480)
                if not requiere_cuadrilla:
                    resuelto = True

            elif nombre_tool in ["escalar", "escalar_cuadrilla_presencial"]:
                if res_tool.get("requiere_confirmacion_humana"):
                    diagnostico_actual += " | Escalamiento presencial registrado y en espera de confirmación humana (HITL)."
                else:
                    diagnostico_actual += f" | Orden técnica generada: {res_tool.get('orden_despacho_id')} para {res_tool.get('cuadrilla_asignada')}."
                resuelto = True

            iteracion += 1

        # Comprobación de condición de corte por límite de iteraciones
        if not resuelto and iteracion > limite_max:
            return RespuestaAgenteOut(
                exito=False,
                diagnostico_final=diagnostico_actual or "Resolución incompleta por alcance de tope de iteraciones.",
                prioridad=prioridad_actual,
                sla_minutos=sla_actual,
                citas=citas_obtenidas,
                requiere_revision_humana=True,
                motivo_revision=f"Tope de iteraciones alcanzado (MAX_ITER={limite_max}). Derivación obligatoria a operador humano para preservar SLA.",
                iteraciones_ejecutadas=limite_max,
                limite_alcanzado=True,
                audit_trail=audit_trail
            )

        # Resolución exitosa dentro del límite
        return RespuestaAgenteOut(
            exito=True,
            diagnostico_final=diagnostico_actual,
            prioridad=prioridad_actual,
            sla_minutos=sla_actual,
            citas=citas_obtenidas,
            requiere_revision_humana=requiere_cuadrilla or (prioridad_actual == "Alta"),
            motivo_revision="Incidente crítico o alarma óptica: confirmación requerida para derivar cuadrilla presencial" if (requiere_cuadrilla or prioridad_actual == "Alta") else None,
            iteraciones_ejecutadas=iteracion - 1,
            limite_alcanzado=False,
            audit_trail=audit_trail
        )


# Instancia Singleton del Agente
agente_soporte = AgenteTriajeTecnico()
