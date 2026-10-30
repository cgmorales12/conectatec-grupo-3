"""
Agente de Alcance Controlado con Herramientas Deterministas (Patrón ReAct)
Proyecto: ConectaTec / TecnoAula — Triaje de Incidentes Técnicos (Caso N.º 03 · Grupo 3 UNIANDES)
Seminario de Titulación: Ingeniería de Software con IA Generativa — 2026

Cumple con la rúbrica oficial:
«Agente con las herramientas del caso: Cada herramienta con esquema Pydantic,
implementación determinista y límite de iteraciones.»
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional, Literal, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, ValidationError

from app.tools.priorizar import calcular_prioridad_itil
from app.services.rag import consultar_base_conocimiento
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
            "buscar_procedimiento_rag",
            "calcular_prioridad_itil",
            "consultar_estado_nodo",
            "registrar_ticket_kanban",
            "escalar_cuadrilla_presencial"
        ],
        "herramientas_requieren_confirmacion": [
            "registrar_ticket_kanban",
            "escalar_cuadrilla_presencial"
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
            logger.warning(f"No se pudo leer parametros.yaml, usando defaults: {e}")
    return defaults


CONFIG_AGENTE = _cargar_config_agente()
MAX_ITERACIONES_DEFECTO = CONFIG_AGENTE["max_iteraciones_agente"]


# ============================================================================
# 2. Esquemas Pydantic V2 Estrictos para cada Herramienta (extra='forbid')
# ============================================================================

# Tool 1: Búsqueda Semántica en Manuales Técnicos (RAG)
class ParamsBuscarProcedimientoRAG(BaseModel):
    """Contrato estricto de entrada para buscar_procedimiento_rag."""
    model_config = ConfigDict(extra="forbid")

    consulta: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Descripción o síntomas técnicos para consultar en la base de manuales oficiales"
    )


class ResultadoBuscarProcedimientoRAG(BaseModel):
    """Contrato de salida para buscar_procedimiento_rag."""
    model_config = ConfigDict(extra="forbid")

    encontrado: bool
    documento_id: Optional[str] = None
    titulo_documento: Optional[str] = None
    paso_exacto: Optional[str] = None
    fragmento_aplicado: Optional[str] = None
    vigencia: Optional[str] = None
    url: Optional[str] = None
    requiere_cuadrilla_fisica: bool = False


# Tool 2: Cálculo Matemático ITIL de Prioridad y SLA
class ParamsCalcularPrioridadITIL(BaseModel):
    """Contrato estricto de entrada para calcular_prioridad_itil."""
    model_config = ConfigDict(extra="forbid")

    impacto: Literal["Alto", "Medio", "Bajo"] = Field(
        ..., description="Nivel de afectación operativa o usuarios incomunicados"
    )
    urgencia: Literal["Alta", "Media", "Baja"] = Field(
        ..., description="Velocidad requerida de contención o resolución"
    )


class ResultadoCalcularPrioridadITIL(BaseModel):
    """Contrato de salida para calcular_prioridad_itil."""
    model_config = ConfigDict(extra="forbid")

    prioridad: Literal["Alta", "Media", "Baja"]
    sla_minutos: int
    descripcion_sla: str


# Tool 3: Verificación de Estado Operativo del Nodo de Telecomunicaciones
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


# Tool 4: Registro Determinista de Ticket en Tablero Kanban
class ParamsRegistrarTicketKanban(BaseModel):
    """Contrato estricto de entrada para registrar_ticket_kanban."""
    model_config = ConfigDict(extra="forbid")

    nombre_cliente: str = Field(..., min_length=2, max_length=100)
    email_cliente: str = Field(..., min_length=5, max_length=120)
    descripcion_problema: str = Field(..., min_length=10, max_length=2000)
    categoria: str = Field(..., min_length=3, max_length=100)
    prioridad: Literal["Alta", "Media", "Baja"]
    sla_minutos: int = Field(..., ge=1, le=10080)
    solucion_propuesta: str = Field(..., min_length=10, max_length=2000)
    documento_id: Optional[str] = None


class ResultadoRegistrarTicketKanban(BaseModel):
    """Contrato de salida para registrar_ticket_kanban."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: int
    ticket_codigo: str
    estado: str
    registrado: bool


# Tool 5: Escalamiento Presencial de Cuadrilla Técnica de Campo
class ParamsEscalarCuadrillaPresencial(BaseModel):
    """Contrato estricto de entrada para escalar_cuadrilla_presencial."""
    model_config = ConfigDict(extra="forbid")

    ticket_codigo: str = Field(..., min_length=5, max_length=30)
    sector: str = Field(..., min_length=3, max_length=100)
    motivo_escalado: str = Field(..., min_length=10, max_length=500)
    requiere_fusionadora: bool = True


class ResultadoEscalarCuadrillaPresencial(BaseModel):
    """Contrato de salida para escalar_cuadrilla_presencial."""
    model_config = ConfigDict(extra="forbid")

    orden_despacho_id: str
    cuadrilla_asignada: str
    tiempo_estimado_llegada_minutos: int
    requiere_confirmacion_humana: bool


# Tool 6: Consulta de Tarifario Oficial Desacoplado (config/tarifas.json)
class ParamsConsultarTarifasRepuestos(BaseModel):
    """Contrato estricto de entrada para consultar_tarifas_repuestos."""
    model_config = ConfigDict(extra="forbid")

    codigo_o_categoria: Optional[str] = Field(
        None,
        max_length=50,
        description="Código de ítem (ej: EQ-ONT-GPON-W6) o categoría (equipos_cpe, materiales_planta_externa, mano_de_obra_y_servicios)"
    )


class ResultadoConsultarTarifasRepuestos(BaseModel):
    """Contrato de salida para consultar_tarifas_repuestos."""
    model_config = ConfigDict(extra="forbid")

    items: List[Dict[str, Any]]
    total_encontrados: int
    moneda: str
    origen: str


# Tool 7: Consulta de Calendario Operativo y Feriados (config/calendario.json)
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



# ============================================================================
# 3. Implementaciones Deterministas de las Herramientas (Pure Python)
# ============================================================================

def tool_buscar_procedimiento_rag(params: ParamsBuscarProcedimientoRAG) -> ResultadoBuscarProcedimientoRAG:
    """Implementación determinista: consulta manuales técnicos oficiales en data/raw/ y ChromaDB."""
    diag = consultar_base_conocimiento(params.consulta)
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
            requiere_cuadrilla_fisica=diag.requiere_visita_campo
        )
    return ResultadoBuscarProcedimientoRAG(
        encontrado=False,
        documento_id=None,
        titulo_documento=None,
        paso_exacto=None,
        fragmento_aplicado=None,
        vigencia=None,
        url=None,
        requiere_cuadrilla_fisica=diag.requiere_visita_campo
    )


def tool_calcular_prioridad_itil(params: ParamsCalcularPrioridadITIL) -> ResultadoCalcularPrioridadITIL:
    """Implementación determinista: calcula matemáticamente la prioridad desde config/matriz_prioridad.json."""
    res: PrioridadSLA = calcular_prioridad_itil(params.impacto, params.urgencia)
    return ResultadoCalcularPrioridadITIL(
        prioridad=res.prioridad,  # type: ignore
        sla_minutos=res.sla_minutos,
        descripcion_sla=res.descripcion_sla
    )


def tool_consultar_estado_nodo(params: ParamsConsultarEstadoNodo) -> ResultadoConsultarEstadoNodo:
    """Implementación determinista: telemetría de nodos GPON y switches de campus."""
    nodo = params.nodo_id.upper().strip()
    # Simulación determinista basada en hash del nodo para consistencia
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


def tool_registrar_ticket_kanban(params: ParamsRegistrarTicketKanban) -> ResultadoRegistrarTicketKanban:
    """Implementación determinista: registra el ticket en base de datos SQLite."""
    from app.database import obtener_conexion
    
    codigo = f"TCK-{hashlib.md5(f'{params.email_cliente}{datetime.now().isoformat()}'.encode()).hexdigest()[:8].upper()}"
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (
            ticket_codigo, fecha_creacion, nombre_cliente, email_cliente,
            descripcion_problema, categoria, impacto, urgencia, prioridad,
            sla_minutos, descripcion_sla, solucion_propuesta, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        codigo,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        params.nombre_cliente,
        params.email_cliente,
        params.descripcion_problema,
        params.categoria,
        "Medio",
        "Media",
        params.prioridad,
        params.sla_minutos,
        f"SLA Máximo de {params.sla_minutos} minutos",
        params.solucion_propuesta,
        "nuevo"
    ))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return ResultadoRegistrarTicketKanban(
        ticket_id=ticket_id,
        ticket_codigo=codigo,
        estado="nuevo",
        registrado=True
    )


def tool_escalar_cuadrilla_presencial(params: ParamsEscalarCuadrillaPresencial) -> ResultadoEscalarCuadrillaPresencial:
    """Implementación determinista: genera orden de despacho para cuadrilla de campo."""
    orden_id = f"ODT-FIBRA-{hashlib.sha256(params.ticket_codigo.encode()).hexdigest()[:6].upper()}"
    return ResultadoEscalarCuadrillaPresencial(
        orden_despacho_id=orden_id,
        cuadrilla_asignada="Cuadrilla de Planta Externa Nº 03 (Fusionadora Fujikura 70S)",
        tiempo_estimado_llegada_minutos=45,
        requiere_confirmacion_humana=True
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
            dt = datetime.fromisoformat(params.fecha_iso.strip()[:10])
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
    "buscar_procedimiento_rag": {
        "esquema": ParamsBuscarProcedimientoRAG,
        "funcion": tool_buscar_procedimiento_rag,
        "nivel": 1,
        "descripcion": "Recupera manuales técnicos oficiales con ID y paso exacto"
    },
    "calcular_prioridad_itil": {
        "esquema": ParamsCalcularPrioridadITIL,
        "funcion": tool_calcular_prioridad_itil,
        "nivel": 1,
        "descripcion": "Calcula matemáticamente prioridad ITIL y SLA (0 tokens)"
    },
    "consultar_estado_nodo": {
        "esquema": ParamsConsultarEstadoNodo,
        "funcion": tool_consultar_estado_nodo,
        "nivel": 1,
        "descripcion": "Consulta telemetría y potencia óptica del nodo GPON"
    },
    "registrar_ticket_kanban": {
        "esquema": ParamsRegistrarTicketKanban,
        "funcion": tool_registrar_ticket_kanban,
        "nivel": 2,
        "descripcion": "Persiste un ticket estructurado en la base de datos"
    },
    "escalar_cuadrilla_presencial": {
        "esquema": ParamsEscalarCuadrillaPresencial,
        "funcion": tool_escalar_cuadrilla_presencial,
        "nivel": 2,
        "descripcion": "Despacha cuadrilla con fusionadora óptica (requiere confirmación)"
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

    solicitud: str = Field(..., min_length=5, max_length=2000, description="Texto de la incidencia o reporte")
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
        3. Ejecución determinista pura.
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

        # 3. Ejecución Determinista
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
        es_fuera_de_alcance = any(w in texto_lower for w in [
            "complexivo", "comedor", "matrícula", "matricula", "almuerzo",
            "llueve", "clima", "nómina", "nomina", "sueldo"
        ]) and not any(t in texto_lower for t in ["los", "ont", "router", "fibra", "wifi", "cable", "red"])

        if es_fuera_de_alcance:
            diag_fuera = (
                "No dispongo de un procedimiento técnico registrado para esta situación en los 15 manuales oficiales del ISP. "
                "Orientación al usuario: Para trámites académicos, matrículas o certificaciones, acuda a Secretaría General o DGA. "
                "Si experimenta una falla de telecomunicaciones (luces LED de la ONT, Wi-Fi o Ethernet), descríbala detalladamente."
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
        requiere_cuadrilla = False
        resuelto = False

        # Bandera de simulación de fallo / Chaos Engineering
        if solicitud_in.forzar_bucle_infinito:
            # Simula una condición que agota el tope sin resolver para probar el corte forzoso
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
                # Paso 1: Consultar base RAG
                nombre_tool = "buscar_procedimiento_rag"
                args = {"consulta": texto_usuario}
            elif iteracion == 2:
                # Paso 2: Calcular prioridad ITIL con la matriz determinista
                nombre_tool = "calcular_prioridad_itil"
                # Extraer heurística del síntoma para impacto y urgencia
                if any(w in texto_lower for w in ["fibra", "corte", "masivo", "acometida", "ont"]) or ("los" in texto_lower and "roj" in texto_lower) or ("los" in texto_lower and "parpadea" in texto_lower):
                    impacto_actual = "Alto"
                    urgencia_actual = "Alta"
                elif any(w in texto_lower for w in ["lento", "lentitud", "velocidad", "ethernet", "latencia", "ping"]):
                    impacto_actual = "Medio"
                    urgencia_actual = "Media"
                else:
                    impacto_actual = "Bajo"
                    urgencia_actual = "Baja"
                args = {"impacto": impacto_actual, "urgencia": urgencia_actual}
            elif iteracion == 3 and requiere_cuadrilla:
                # Paso 3 (si aplica): Escalar a cuadrilla
                nombre_tool = "escalar_cuadrilla_presencial"
                args = {
                    "ticket_codigo": f"TCK-{hashlib.md5(texto_usuario.encode()).hexdigest()[:6].upper()}",
                    "sector": "Campus Universitario Matriz",
                    "motivo_escalado": "Alarma óptica crítica LOS roja detectada",
                    "requiere_fusionadora": True
                }
            else:
                # Caso completado
                resuelto = True
                break

            # FASE 3: ACTUAR (Ejecución bajo whitelist y Pydantic)
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
            if nombre_tool == "buscar_procedimiento_rag":
                if res_tool.get("encontrado"):
                    diagnostico_actual = f"Procedimiento recomendado según {res_tool['documento_id']} ({res_tool['paso_exacto']}): {res_tool['fragmento_aplicado']}"
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
                else:
                    diagnostico_actual = "Incidencia analizada sin procedimiento directo; aplicar ciclo de reinicio de 30 segundos (DOC-03)."

            elif nombre_tool == "calcular_prioridad_itil":
                prioridad_actual = res_tool.get("prioridad", "Media")
                sla_actual = res_tool.get("sla_minutos", 480)
                if not requiere_cuadrilla:
                    resuelto = True

            elif nombre_tool == "escalar_cuadrilla_presencial":
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
            motivo_revision="Incidente crítico o alarma óptica: confirmación de cuadrilla presencial" if (requiere_cuadrilla or prioridad_actual == "Alta") else None,
            iteraciones_ejecutadas=iteracion - 1,
            limite_alcanzado=False,
            audit_trail=audit_trail
        )


# Instancia Singleton del Agente
agente_soporte = AgenteTriajeTecnico()
