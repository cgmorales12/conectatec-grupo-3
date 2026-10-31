"""
Suite de Pruebas Unitarias Deterministas con Pytest: Herramientas del Agente ReAct
Proyecto: TecnoAula / ConectaTec — Triaje Inteligente de Incidentes ISP (Caso N.º 03 · Grupo 3 UNIANDES)
Seminario de Titulación: Ingeniería de Software con IA Generativa — 2026
Autor: Amalia Geoconda Iguasnia Escobar (QA Lead / Seguridad y Requerimientos — GitHub: Geocoiguasnia76)

Cumple con la rúbrica oficial:
«Pruebas con pytest: De las herramientas del agente y de la construcción del prompt.»
«Cada herramienta con esquema Pydantic, implementación determinista y límite de iteraciones.»
"""

import pytest
from pydantic import ValidationError

from app.agente import (
    AgenteTriajeTecnico,
    CATALOGO_HERRAMIENTAS,
    ParamsClasificar,
    ResultadoClasificar,
    ParamsBuscarSolucion,
    ParamsBuscarProcedimientoRAG,
    ResultadoBuscarProcedimientoRAG,
    ParamsCalcularPrioridadITIL,
    ResultadoCalcularPrioridadITIL,
    ParamsConsultarEstadoNodo,
    ResultadoConsultarEstadoNodo,
    ParamsRegistrarTicketKanban,
    ResultadoRegistrarTicketKanban,
    ParamsEscalar,
    ResultadoEscalar,
    ParamsEscalarCuadrillaPresencial,
    ResultadoEscalarCuadrillaPresencial,
    ParamsConsultarTarifasRepuestos,
    ResultadoConsultarTarifasRepuestos,
    ParamsConsultarCalendarioSoporte,
    ResultadoConsultarCalendarioSoporte,
    SolicitudAgenteIn,
    RespuestaAgenteOut,
    tool_clasificar,
    tool_buscar_solucion,
    tool_buscar_procedimiento_rag,
    tool_priorizar,
    tool_calcular_prioridad_itil,
    tool_crear_ticket,
    tool_registrar_ticket_kanban,
    tool_escalar,
    tool_escalar_cuadrilla_presencial,
    tool_consultar_estado_nodo,
    tool_consultar_tarifas_repuestos,
    tool_consultar_calendario_soporte
)


# ============================================================================
# 1. Verificación del Catálogo Cerrado de Herramientas (Whitelist Oficial)
# ============================================================================

def test_catalogo_herramientas_registro_completo():
    """Valida que las 5 herramientas canónicas del caso y sus aliases estén registradas."""
    herramientas_esperadas = {
        # Herramientas requeridas por la rúbrica oficial (Semana 3 · 70%)
        "clasificar",
        "priorizar",
        "buscar_solucion",
        "crear_ticket",
        "escalar",
        # Aliases y herramientas complementarias
        "buscar_procedimiento_rag",
        "calcular_prioridad_itil",
        "consultar_estado_nodo",
        "registrar_ticket_kanban",
        "escalar_cuadrilla_presencial",
        "consultar_tarifas_repuestos",
        "consultar_calendario_soporte"
    }
    herramientas_actuales = set(CATALOGO_HERRAMIENTAS.keys())
    assert herramientas_esperadas.issubset(herramientas_actuales), (
        f"Faltan herramientas en el catálogo: {herramientas_esperadas - herramientas_actuales}"
    )

    for nombre, defn in CATALOGO_HERRAMIENTAS.items():
        assert "esquema" in defn, f"Tool '{nombre}' carece de esquema Pydantic."
        assert "funcion" in defn, f"Tool '{nombre}' carece de función determinista."
        assert "nivel" in defn, f"Tool '{nombre}' carece de nivel de seguridad/HITL."
        assert "descripcion" in defn, f"Tool '{nombre}' carece de descripción funcional."
        assert callable(defn["funcion"]), f"La función de '{nombre}' debe ser invocable."


# ============================================================================
# 1.1 Pruebas Unitarias de las 5 Herramientas Principales del Caso (70%)
# ============================================================================

def test_tool_clasificar_solicitud_caso():
    """Valida la herramienta clasificar(solicitud) con esquema Pydantic estricto."""
    params = ParamsClasificar(solicitud="Tengo cortes intermitentes en la red Wi-Fi del aula 204")
    resultado = tool_clasificar(params)

    assert isinstance(resultado, ResultadoClasificar)
    assert resultado.categoria != ""
    assert resultado.impacto in ["Alto", "Medio", "Bajo"]
    assert resultado.urgencia in ["Alta", "Media", "Baja"]
    assert resultado.es_fuera_de_alcance is False

    # Verificación extra='forbid'
    with pytest.raises(ValidationError):
        ParamsClasificar(solicitud="problema wifi", inyeccion_no_permitida="malware")


def test_tool_buscar_solucion_chromadb_caso():
    """Valida la herramienta buscar_solucion(categoria, texto) consultando ChromaDB."""
    params = ParamsBuscarSolucion(
        texto="La luz LOS de la ONT Huawei EchoLife parpadea en rojo",
        categoria="Conectividad y Fibra Óptica"
    )
    resultado = tool_buscar_solucion(params)

    assert isinstance(resultado, ResultadoBuscarProcedimientoRAG)
    assert resultado.encontrado is True
    assert resultado.documento_id in ["DOC-01", "DOC-03"]
    assert "Paso" in resultado.paso_exacto
    assert resultado.fragmento_aplicado is not None


def test_tool_priorizar_itil_caso():
    """Valida la herramienta priorizar(impacto, urgencia) leyendo matriz determinista."""
    params = ParamsCalcularPrioridadITIL(impacto="Alto", urgencia="Alta")
    resultado = tool_priorizar(params)

    assert isinstance(resultado, ResultadoCalcularPrioridadITIL)
    assert resultado.prioridad == "Alta"
    assert resultado.sla_minutos <= 120


def test_tool_crear_ticket_caso():
    """Valida la herramienta crear_ticket(datos) con esquema estricto y persistencia SQLite."""
    params = ParamsRegistrarTicketKanban(
        nombre_cliente="Dra. Ana Valencia",
        email_cliente="avalencia@uniandes.edu.ec",
        descripcion_problema="El cable Ethernet de la mesa del laboratorio tiene el conector RJ-45 roto.",
        categoria="Red Cableada",
        prioridad="Media",
        sla_minutos=240,
        solucion_propuesta="Sustitución de conector RJ45 según DOC-08.",
        documento_id="DOC-08"
    )
    resultado = tool_crear_ticket(params)

    assert isinstance(resultado, ResultadoRegistrarTicketKanban)
    assert resultado.registrado is True
    assert resultado.ticket_id > 0
    assert resultado.ticket_codigo.startswith("TCK-")


def test_tool_escalar_hitl_bloqueo_sin_confirmacion():
    """Valida que escalar(ticket, motivo) se bloquee y exija confirmación cuando confirmado=False."""
    params = ParamsEscalar(
        ticket="TCK-LAB-01",
        motivo="Alarma óptica crítica LOS roja en acometida de fibra",
        confirmado=False  # Sin autorización humana
    )
    resultado = tool_escalar(params)

    assert isinstance(resultado, ResultadoEscalar)
    assert resultado.requiere_confirmacion_humana is True
    assert resultado.estado == "pendiente_aprobacion_humana"
    assert resultado.orden_despacho_id is None
    assert "HUMAN-IN-THE-LOOP" in resultado.mensaje


def test_tool_escalar_hitl_ejecucion_con_confirmacion():
    """Valida que escalar(ticket, motivo) emita la orden de despacho cuando confirmado=True."""
    params = ParamsEscalar(
        ticket="TCK-LAB-01",
        motivo="Alarma óptica crítica confirmada por jefe de laboratorio",
        confirmado=True  # Con autorización humana explícita
    )
    resultado = tool_escalar(params)

    assert isinstance(resultado, ResultadoEscalar)
    assert resultado.requiere_confirmacion_humana is False
    assert resultado.estado == "despachado"
    assert resultado.orden_despacho_id is not None
    assert resultado.orden_despacho_id.startswith("ODT-FIBRA-")
    assert "Cuadrilla" in resultado.cuadrilla_asignada


# ============================================================================
# 2. Pruebas Unitarias de cada Herramienta y sus Esquemas Pydantic V2 (extra="forbid")
# ============================================================================

# Tool 1: Búsqueda Semántica RAG en Manuales Oficiales
def test_tool_buscar_procedimiento_rag_exito_y_esquema():
    """Valida la ejecución determinista de buscar_procedimiento_rag para una avería de enlace óptico."""
    params = ParamsBuscarProcedimientoRAG(consulta="alarma óptica luz LOS roja parpadeando en ONT Huawei")
    resultado = tool_buscar_procedimiento_rag(params)

    assert isinstance(resultado, ResultadoBuscarProcedimientoRAG)
    assert resultado.encontrado is True
    assert resultado.documento_id in ["DOC-01", "DOC-03"]
    assert "Paso" in resultado.paso_exacto
    assert resultado.fragmento_aplicado is not None
    assert len(resultado.fragmento_aplicado) > 20
    assert resultado.requiere_cuadrilla_fisica is True


def test_tool_buscar_procedimiento_rag_rechazo_extra_forbid():
    """Valida que ParamsBuscarProcedimientoRAG rechace campos no declarados (OWASP extra='forbid')."""
    with pytest.raises(ValidationError) as exc_info:
        ParamsBuscarProcedimientoRAG(
            consulta="consulta técnica válida",
            parametro_malicioso_inyectado="bypass_test"  # Inyección indebida
        )
    assert "extra_forbidden" in str(exc_info.value)


def test_tool_buscar_procedimiento_rag_longitud_minima():
    """Valida que consultas con menos de 3 caracteres sean rechazadas por Pydantic."""
    with pytest.raises(ValidationError) as exc_info:
        ParamsBuscarProcedimientoRAG(consulta="a")
    assert "string_too_short" in str(exc_info.value)


# Tool 2: Cálculo Matemático ITIL de Prioridad y SLA (0 tokens)
def test_tool_calcular_prioridad_itil_determinista():
    """Valida que calcular_prioridad_itil sea determinista y concuerde con la matriz ITIL."""
    # Caso 1: Alto / Alta -> Alta (15 min en matriz ITIL de campus)
    res_alta = tool_calcular_prioridad_itil(ParamsCalcularPrioridadITIL(impacto="Alto", urgencia="Alta"))
    assert res_alta.prioridad == "Alta"
    assert res_alta.sla_minutos == 15

    # Caso 2: Medio / Media -> Media (240 min / 4h en matriz ITIL)
    res_media = tool_calcular_prioridad_itil(ParamsCalcularPrioridadITIL(impacto="Medio", urgencia="Media"))
    assert res_media.prioridad == "Media"
    assert res_media.sla_minutos == 240

    # Caso 3: Bajo / Baja -> Baja (1440 min / 24h en matriz ITIL)
    res_baja = tool_calcular_prioridad_itil(ParamsCalcularPrioridadITIL(impacto="Bajo", urgencia="Baja"))
    assert res_baja.prioridad == "Baja"
    assert res_baja.sla_minutos == 1440


def test_tool_calcular_prioridad_itil_rechazo_valores_invalidos():
    """Valida que no se acepten valores de impacto o urgencia fuera de los literales permitidos."""
    with pytest.raises(ValidationError):
        ParamsCalcularPrioridadITIL(impacto="Critico", urgencia="Alta")  # 'Critico' no es Literal

    with pytest.raises(ValidationError):
        ParamsCalcularPrioridadITIL(impacto="Alto", urgencia="Inmediata")  # 'Inmediata' no es Literal


# Tool 3: Telemetría y Consulta de Estado de Nodo GPON
def test_tool_consultar_estado_nodo_telemetria():
    """Valida que la consulta de estado de nodo retorne potencias y sectores válidos."""
    res_nodo = tool_consultar_estado_nodo(ParamsConsultarEstadoNodo(nodo_id="NODO-CENTRAL"))
    assert isinstance(res_nodo, ResultadoConsultarEstadoNodo)
    assert res_nodo.nodo_id == "NODO-CENTRAL"
    assert res_nodo.estado == "operativo"
    assert res_nodo.potencia_optica_dbm == -19.4
    assert res_nodo.sector == "Campus Matriz Ambato"

    # Verificación extra='forbid'
    with pytest.raises(ValidationError):
        ParamsConsultarEstadoNodo(nodo_id="NODO-CENTRAL", hack="drop database")


# Tool 4: Registro Determinista de Ticket en Kanban
def test_tool_registrar_ticket_kanban_exito_y_validaciones():
    """Valida que registrar_ticket_kanban persista el ticket y valide campos requeridos."""
    params = ParamsRegistrarTicketKanban(
        nombre_cliente="Ing. Carlos Pérez",
        email_cliente="cperez@uniandes.edu.ec",
        descripcion_problema="Luz LOS roja parpadeando en la ONT del Laboratorio de Telecomunicaciones.",
        categoria="Conectividad y Fibra Óptica",
        prioridad="Alta",
        sla_minutos=120,
        solucion_propuesta="Inspección de acometida y medición de potencia óptica.",
        documento_id="DOC-01"
    )
    res_ticket = tool_registrar_ticket_kanban(params)
    assert isinstance(res_ticket, ResultadoRegistrarTicketKanban)
    assert res_ticket.registrado is True
    assert res_ticket.ticket_codigo.startswith("TCK-")
    assert res_ticket.estado == "nuevo"

    # Rechazo por descripción demasiado corta (< 10 caracteres)
    with pytest.raises(ValidationError):
        ParamsRegistrarTicketKanban(
            nombre_cliente="A",
            email_cliente="email@test.com",
            descripcion_problema="Corta",
            categoria="Redes",
            prioridad="Baja",
            sla_minutos=60,
            solucion_propuesta="Solución válida para prueba"
        )


# Tool 5: Escalamiento Presencial de Cuadrilla Técnica de Campo
def test_tool_escalar_cuadrilla_presencial_y_hitl():
    """Valida que escalar_cuadrilla_presencial genere orden técnica y requiera confirmación humana."""
    params = ParamsEscalarCuadrillaPresencial(
        ticket_codigo="TCK-990011",
        sector="Edificio de Posgrados - Ambato",
        motivo_escalado="Corte físico de cable drop exterior tras caída de rama.",
        requiere_fusionadora=True
    )
    res_cuadrilla = tool_escalar_cuadrilla_presencial(params)
    assert isinstance(res_cuadrilla, ResultadoEscalarCuadrillaPresencial)
    assert res_cuadrilla.orden_despacho_id.startswith("ODT-")
    assert "Cuadrilla" in res_cuadrilla.cuadrilla_asignada
    assert res_cuadrilla.tiempo_estimado_llegada_minutos in [45, 90]
    assert res_cuadrilla.requiere_confirmacion_humana is True


# Tool 6: Consulta de Tarifas Desacopladas (config/tarifas.json)
def test_tool_consultar_tarifas_repuestos_desacoplada():
    """Valida que consultar_tarifas_repuestos obtenga precios sin hardcoding en Python."""
    # Listar todas
    res_todas = tool_consultar_tarifas_repuestos(ParamsConsultarTarifasRepuestos())
    assert isinstance(res_todas, ResultadoConsultarTarifasRepuestos)
    assert res_todas.total_encontrados >= 9
    assert res_todas.moneda == "USD"
    assert res_todas.origen == "config/tarifas.json"

    # Filtrar por código específico
    res_ont = tool_consultar_tarifas_repuestos(ParamsConsultarTarifasRepuestos(codigo_o_categoria="EQ-ONT-GPON-W6"))
    assert res_ont.total_encontrados == 1
    assert res_ont.items[0]["tarifa_usd"] == 45.00

    # Rechazo extra_forbid
    with pytest.raises(ValidationError):
        ParamsConsultarTarifasRepuestos(codigo_o_categoria="EQ-ONT-GPON-W6", descuento_secreto=0.50)


# Tool 7: Consulta de Calendario Operativo y Feriados (config/calendario.json)
def test_tool_consultar_calendario_soporte_feriados():
    """Valida la verificación determinista de días hábiles y feriados nacionales de Ecuador."""
    # Feriado Nacional: 1 de Enero de 2026 (Año Nuevo)
    res_feriado = tool_consultar_calendario_soporte(ParamsConsultarCalendarioSoporte(fecha_iso="2026-01-01"))
    assert res_feriado.es_habil is False
    assert "Ano Nuevo" in res_feriado.motivo or "Nuevo" in res_feriado.motivo
    assert res_feriado.guardia_noc_24_7_activa is True
    assert res_feriado.origen == "config/calendario.json"

    # Día hábil ordinario: Miércoles 14 de Enero de 2026 (a las 10:00)
    res_habil = tool_consultar_calendario_soporte(ParamsConsultarCalendarioSoporte(fecha_iso="2026-01-14"))
    assert res_habil.es_habil is True
    assert "Dentro de jornada laboral" in res_habil.motivo or "jornada" in res_habil.motivo.lower()


# ============================================================================
# 3. Pruebas de Seguridad del Agente: Whitelist Inviolable
# ============================================================================

def test_agente_whitelist_rechazo_herramientas_prohibidas():
    """Valida que el agente bloquee tajantemente la invocación de herramientas no permitidas (OWASP ASI02)."""
    agente = AgenteTriajeTecnico()

    herramientas_adversas = [
        "eliminar_ticket_base_datos",
        "ejecutar_comando_bash",
        "borrar_registros_auditoria",
        "enviar_credenciales_remotas",
        "formatear_servidor"
    ]

    for tool_prohibida in herramientas_adversas:
        ok, res, obs = agente.ejecutar_herramienta(tool_prohibida, {"param": "valor"})
        assert ok is False, f"La herramienta prohibida '{tool_prohibida}' debió ser rechazada."
        assert res.get("error") == "herramienta_prohibida"
        assert "RECHAZO DE SEGURIDAD" in obs


def test_agente_whitelist_ejecucion_herramienta_autorizada():
    """Valida que herramientas autorizadas se ejecuten con éxito a través de agente.ejecutar_herramienta."""
    agente = AgenteTriajeTecnico()
    ok, res, obs = agente.ejecutar_herramienta(
        "calcular_prioridad_itil",
        {"impacto": "Alto", "urgencia": "Alta"}
    )
    assert ok is True
    assert res["prioridad"] == "Alta"
    assert res["sla_minutos"] == 15
    assert "éxito" in obs.lower()


# ============================================================================
# 4. Pruebas de Límite de Iteraciones (Corte Forzoso y Control de Bucles)
# ============================================================================

def test_agente_corte_forzoso_limite_iteraciones():
    """Valida que el bucle ReAct no sobrepase el límite máximo de iteraciones configurado."""
    agente = AgenteTriajeTecnico(max_iteraciones=4)

    # Invocación en modo Chaos Engineering con forzar_bucle_infinito=True
    solicitud = SolicitudAgenteIn(
        solicitud="Avería compleja con comportamiento caótico en enlace de campus",
        max_iteraciones=4,
        forzar_bucle_infinito=True
    )
    respuesta = agente.resolver(solicitud)

    assert isinstance(respuesta, RespuestaAgenteOut)
    assert respuesta.exito is False
    assert respuesta.limite_alcanzado is True
    assert respuesta.iteraciones_ejecutadas == 4
    assert respuesta.requiere_revision_humana is True
    assert "CORTE DETERMINISTA DE SEGURIDAD" in respuesta.diagnostico_final
    assert "Límite máximo de iteraciones alcanzado" in respuesta.motivo_revision
    assert len(respuesta.audit_trail) == 4


# ============================================================================
# 5. Pruebas de Flujo Completo ReAct: Observar, Pensar, Actuar, Verificar
# ============================================================================

def test_agente_flujo_camino_feliz_resolucion_tecnica():
    """Valida el ciclo ReAct completo para un reporte técnico crítico con cita RAG y orden presencial."""
    agente = AgenteTriajeTecnico(max_iteraciones=6)

    solicitud = SolicitudAgenteIn(
        solicitud="Tengo la luz LOS roja parpadeando en la ONT del Laboratorio 2 y el cable de fibra exterior está quebrado.",
        nombre_cliente="Docente Sistemas",
        email_cliente="docente@uniandes.edu.ec"
    )
    respuesta = agente.resolver(solicitud)

    assert respuesta.exito is True
    assert respuesta.limite_alcanzado is False
    assert respuesta.prioridad == "Alta"
    assert respuesta.sla_minutos == 15
    assert len(respuesta.citas) >= 1
    assert any(c.documento_id in ["DOC-01", "DOC-03", "DOC-09"] for c in respuesta.citas)
    assert respuesta.requiere_revision_humana is True  # Alarma crítica requiere confirmación
    assert len(respuesta.audit_trail) >= 3

    # Comprobar fases ReAct en el audit_trail
    fases = [paso.fase for paso in respuesta.audit_trail]
    assert "OBSERVAR" in fases
    assert "ACTUAR" in fases


def test_agente_mision_silencio_solicitud_no_tecnica():
    """Valida que solicitudes fuera de alcance se atiendan con abstención inmediata en 1 sola iteración."""
    agente = AgenteTriajeTecnico()

    solicitud = SolicitudAgenteIn(
        solicitud="¿A qué hora abre el comedor universitario para el almuerzo y cuándo son las matrículas?",
        nombre_cliente="Estudiante",
        email_cliente="alumno@uniandes.edu.ec"
    )
    respuesta = agente.resolver(solicitud)

    assert respuesta.exito is True
    assert respuesta.prioridad == "Baja"
    assert len(respuesta.citas) == 0
    assert respuesta.iteraciones_ejecutadas == 1
    assert "No dispongo de un procedimiento técnico" in respuesta.diagnostico_final
    assert "Secretaría General" in respuesta.diagnostico_final
