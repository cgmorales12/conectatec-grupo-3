"""
Enrutador de Tickets de Soporte Técnico - ConectaTec
Endpoints: Clasificación Inteligente, Consulta de Tickets y Cambio de Estado Kanban.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from datetime import datetime, timezone
import uuid


from app.schemas import (
    SolicitudTicketIn,
    TicketOut,
    ListaTicketsOut,
    ActualizarEstadoIn,
    CitaRAG,
    DiagnosticoRAG,
    MetadatosIA,
    PropuestaRegistroTicketOut,
    ConfirmarRegistroIn,
    PropuestaEnviarNotificacionOut,
    ConfirmarEnvioIn,
    PropuestaDerivarCuadrillaOut,
    ConfirmarDerivacionIn,
    ResultadoConfirmacionHumanaOut
)
from app.services.llm import clasificar_solicitud
from app.tools.priorizar import calcular_prioridad_itil
from app.services.rag import consultar_base_conocimiento
from app.database import (
    guardar_ticket,
    listar_tickets,
    actualizar_estado_ticket,
    eliminar_ticket_logico,
    confirmar_envio_notificacion,
    confirmar_derivacion_cuadrilla,
    obtener_ticket_limpio_por_id,
    obtener_ticket_por_id
)
from app.services.auth import obtener_usuario_autenticado

router = APIRouter(prefix="/v1/tickets", tags=["Tickets de Soporte"])


@router.post(
    "/clasificar",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="Clasifica y genera un ticket de soporte con IA y RAG"
)
def clasificar_y_crear_ticket(solicitud: SolicitudTicketIn, request: Request = None):
    """
    Recibe el reporte de una avería, extrae impacto y urgencia con Gemini/Groq,
    calcula la prioridad matemática con la matriz ITIL y consulta los manuales técnicos RAG.
    """
    # 1. Extracción estructurada con IA y Gateway resiliente (con soporte de Chaos Engineering y Modo Vulnerable)
    clasificacion_ia, metadatos_ia = clasificar_solicitud(
        solicitud.descripcion_problema,
        simular_caida_gemini=solicitud.simular_caida_gemini,
        simular_caida_groq=solicitud.simular_caida_groq,
        simular_error_429=solicitud.simular_error_429,
        simular_timeout=solicitud.simular_timeout,
        simular_respuesta_vacia=solicitud.simular_respuesta_vacia,
        modo_vulnerable=solicitud.modo_vulnerable
    )
    
    if request:
        request.state.metadatos_ia = metadatos_ia
    
    # 2. Priorización determinista por código Python (Matriz ITIL) vs Alucinación en Modo Vulnerable
    if solicitud.modo_vulnerable:
        prioridad_nombre = "Infinita (Alucinada)"
        sla_minutos = 0
        descripcion_sla = "SLA Vulnerado · Demostración de alucinación sin matriz determinista ITIL"
        
        diagnostico_rag = DiagnosticoRAG(
            solucion_propuesta="Auditoría técnica de contraste: Caso adverso ejecutado para demostrar que sin validación determinista, el modelo propone procedimientos ficticios (DOC-99) en lugar de consultar los 15 manuales oficiales.",
            citas=[
                CitaRAG(
                    documento_id="DOC-99 (Inventado)",
                    titulo_documento="Teletransportación Cuántica de Fibra Óptica (Caso de Prueba Adverso)",
                    paso_exacto="Paso de Prueba 1.1: Simulación de inyección de prompt",
                    fragmento_aplicado="«Demostración de auditoría: intento de inyección de prompt para evaluar la contención del perímetro de seguridad.»"
                )
            ],
            requiere_visita_campo=True
        )
        estado_inicial = "nuevo"
        requiere_revision = True
    else:
        # Enfoque Seguro ConectaTec: El código dispone leyendo la matriz ITIL
        prioridad_sla = calcular_prioridad_itil(clasificacion_ia.impacto, clasificacion_ia.urgencia)
        prioridad_nombre = prioridad_sla.prioridad
        sla_minutos = prioridad_sla.sla_minutos
        descripcion_sla = prioridad_sla.descripcion_sla
        
        # 3. Consulta RAG sobre el corpus de 15 manuales (con soporte de desconexión simulada)
        diagnostico_rag = consultar_base_conocimiento(
            solicitud.descripcion_problema,
            simular_caida_rag=solicitud.simular_caida_rag
        )
        estado_inicial = "escalado_cuadrilla" if diagnostico_rag.requiere_visita_campo else ("en_atencion" if solicitud.simular_caida_rag else "nuevo")
        requiere_revision = (
            metadatos_ia.conmutado or 
            clasificacion_ia.impacto == "Alto" or
            clasificacion_ia.categoria == "Solicitud No Técnica / Fuera de Alcance" or
            solicitud.simular_caida_rag
        )
    
    # 4. Asignación de identificador único de ticket
    codigo_ticket = f"TCK-{str(uuid.uuid4())[:8].upper()}"
    fecha_actual = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    datos_ticket = {
        "ticket_codigo": codigo_ticket,
        "fecha_creacion": fecha_actual,
        "nombre_cliente": solicitud.nombre_cliente,
        "email_cliente": solicitud.email_cliente,
        "descripcion_problema": solicitud.descripcion_problema,
        "categoria": clasificacion_ia.categoria,
        "impacto": clasificacion_ia.impacto,
        "urgencia": clasificacion_ia.urgencia,
        "prioridad": prioridad_nombre,
        "sla_minutos": sla_minutos,
        "descripcion_sla": descripcion_sla,
        "solucion_propuesta": diagnostico_rag.solucion_propuesta,
        "citas": [c.model_dump() for c in diagnostico_rag.citas],
        "estado": estado_inicial,
        "requiere_revision_humana": requiere_revision,
        "metadatos_ia": metadatos_ia.model_dump(),
        "justificacion": clasificacion_ia.justificacion,
        "sintomas_detectados": clasificacion_ia.sintomas_detectados
    }
    
    # 5. Persistencia en SQLite
    nuevo_id = guardar_ticket(datos_ticket)
    datos_ticket["id"] = nuevo_id
    datos_ticket["citas"] = diagnostico_rag.citas
    datos_ticket["metadatos_ia"] = metadatos_ia
    datos_ticket["justificacion"] = clasificacion_ia.justificacion
    datos_ticket["sintomas_detectados"] = clasificacion_ia.sintomas_detectados
    
    return TicketOut(**datos_ticket)


@router.get(
    "",
    response_model=ListaTicketsOut,
    status_code=status.HTTP_200_OK,
    summary="Obtiene la lista completa de tickets para el tablero Kanban"
)
def obtener_todos_los_tickets():
    """Retorna todos los tickets registrados en la base de datos para visualización."""
    tickets_db = listar_tickets()
    tickets_out = []
    
    for t in tickets_db:
        citas_obj = [CitaRAG(**c) for c in t["citas"]]
        metadatos_obj = MetadatosIA(**t["metadatos_ia"])
        t_dict = dict(t)
        t_dict["citas"] = citas_obj
        t_dict["metadatos_ia"] = metadatos_obj
        tickets_out.append(TicketOut(**t_dict))
        
    return ListaTicketsOut(
        total_tickets=len(tickets_out),
        tickets=tickets_out
    )


@router.patch(
    "/{ticket_id}/estado",
    status_code=status.HTTP_200_OK,
    summary="Actualiza el estado de un ticket en el tablero Kanban"
)
def cambiar_estado_ticket(ticket_id: int, payload: ActualizarEstadoIn):
    """Permite a los operadores y cuadrillas mover tickets entre columnas Kanban."""
    exito = actualizar_estado_ticket(ticket_id, payload.nuevo_estado)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no fue encontrado."
        )
    return {
        "status": "ok",
        "ticket_id": ticket_id,
        "nuevo_estado": payload.nuevo_estado,
        "observacion": payload.observacion
    }


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
    summary="Elimina lógicamente un ticket de soporte (Exclusivo Personal TIC)"
)
def eliminar_ticket(
    ticket_id: int,
    usuario_tic: dict = Depends(obtener_usuario_autenticado)
):
    """
    Eliminación lógica de tickets (Soft-delete).
    Registra el usuario responsable y la marca de tiempo para auditoría de seguridad y LOPDP.
    """
    exito = eliminar_ticket_logico(ticket_id, eliminado_por=usuario_tic["usuario"])
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El ticket #{ticket_id} no fue encontrado o ya se encuentra eliminado."
        )
    return {
        "status": "ok",
        "mensaje": f"Ticket #{ticket_id} eliminado exitosamente del tablero Kanban.",
        "ticket_id": ticket_id,
        "eliminado_por": usuario_tic["usuario"]
    }


# ============================================================================
# Endpoints de Confirmación Humana (Human-in-the-Loop - OWASP LLM08)
# Principio: «Antes de registrar, enviar o derivar, el humano autoriza»
# ============================================================================

@router.post(
    "/proponer",
    response_model=PropuestaRegistroTicketOut,
    status_code=status.HTTP_200_OK,
    summary="Genera una propuesta estructurada de ticket antes de registrar (HITL)",
    description="Realiza triaje, priorización ITIL y RAG, retornando una propuesta sin persistir en base de datos hasta que el operador humano la apruebe."
)
def proponer_registro_ticket(solicitud: SolicitudTicketIn, request: Request = None):
    """
    Fase 1 de Registro HITL:
    El modelo propone y el código calcula la prioridad, pero NO se registra en la base de datos
    hasta recibir confirmación explícita del operador técnico.
    """
    clasificacion_ia, metadatos_ia = clasificar_solicitud(
        solicitud.descripcion_problema,
        simular_caida_gemini=solicitud.simular_caida_gemini,
        simular_caida_groq=solicitud.simular_caida_groq,
        simular_error_429=solicitud.simular_error_429,
        simular_timeout=solicitud.simular_timeout,
        simular_respuesta_vacia=solicitud.simular_respuesta_vacia,
        modo_vulnerable=solicitud.modo_vulnerable
    )

    if request:
        request.state.metadatos_ia = metadatos_ia

    prioridad_sla = calcular_prioridad_itil(clasificacion_ia.impacto, clasificacion_ia.urgencia)
    diagnostico_rag = consultar_base_conocimiento(
        solicitud.descripcion_problema,
        simular_caida_rag=solicitud.simular_caida_rag
    )

    codigo_propuesto = f"TCK-{str(uuid.uuid4())[:8].upper()}"

    return PropuestaRegistroTicketOut(
        ticket_codigo_propuesto=codigo_propuesto,
        nombre_cliente=solicitud.nombre_cliente,
        email_cliente=solicitud.email_cliente,
        descripcion_problema=solicitud.descripcion_problema,
        categoria_propuesta=clasificacion_ia.categoria,
        impacto_propuesto=clasificacion_ia.impacto,
        urgencia_propuesta=clasificacion_ia.urgencia,
        prioridad_itil=prioridad_sla.prioridad,
        sla_minutos=prioridad_sla.sla_minutos,
        descripcion_sla=prioridad_sla.descripcion_sla,
        solucion_propuesta=diagnostico_rag.solucion_propuesta,
        citas=diagnostico_rag.citas,
        requiere_confirmacion_humana=True,
        tipo_accion="registro_ticket",
        justificacion_ia=clasificacion_ia.justificacion,
        sintomas_detectados=clasificacion_ia.sintomas_detectados,
        metadatos_ia=metadatos_ia
    )


@router.post(
    "/confirmar-registro",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="Confirma y persiste un ticket tras aprobación humana explícita",
    description="Recibe la propuesta aprobada (o ajustada manualmente por el operador) y la persiste en la base de datos SQLite."
)
def confirmar_y_guardar_ticket(payload: ConfirmarRegistroIn):
    """
    Fase 2 de Registro HITL:
    Persiste formalmente el ticket en la base de datos registrando el operador que autorizó el alta.
    """
    fecha_actual = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    citas_dict = [c.model_dump() for c in payload.citas]

    datos_ticket = {
        "ticket_codigo": payload.ticket_codigo_propuesto,
        "fecha_creacion": fecha_actual,
        "nombre_cliente": payload.nombre_cliente,
        "email_cliente": payload.email_cliente,
        "descripcion_problema": payload.descripcion_problema,
        "categoria": payload.categoria,
        "impacto": payload.impacto,
        "urgencia": payload.urgencia,
        "prioridad": payload.prioridad,
        "sla_minutos": payload.sla_minutos,
        "descripcion_sla": payload.descripcion_sla,
        "solucion_propuesta": payload.solucion_propuesta,
        "citas": citas_dict,
        "estado": "nuevo",
        "requiere_revision_humana": False, # Ya fue revisado y aprobado por el operador
        "justificacion": payload.justificacion or "Registro aprobado tras verificación humana.",
        "sintomas_detectados": payload.sintomas_detectados,
        "confirmado_por": payload.operador_confirmador,
        "fecha_confirmacion": fecha_actual,
        "accion_confirmada": "registro_ticket",
        "metadatos_ia": {
            "proveedor": "gemini",
            "modelo": "gemini-1.5-flash",
            "conmutado": False,
            "motivo_conmutacion": None,
            "latencia_ms": 0.0,
            "modo_vulnerable": False,
            "alucinacion_detectada": False
        }
    }

    nuevo_id = guardar_ticket(datos_ticket)
    ticket_guardado = obtener_ticket_limpio_por_id(nuevo_id)

    if not ticket_guardado:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar el ticket confirmado de la base de datos."
        )

    return TicketOut(**ticket_guardado)


@router.get(
    "/{ticket_id}/proponer-envio",
    response_model=PropuestaEnviarNotificacionOut,
    summary="Genera borrador de notificación antes de remitir al usuario (HITL)",
    description="Genera el asunto y cuerpo del mensaje con citas técnicas para que el operador lo revise antes del envío."
)
def proponer_envio_notificacion(ticket_id: int):
    """
    Fase 1 de Envío HITL:
    Muestra el borrador de resolución técnica con citas verificadas antes de enviar el correo.
    """
    ticket = obtener_ticket_limpio_por_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no existe."
        )

    citas_texto = ""
    if ticket.get("citas"):
        citas_texto = "\n\nProcedimiento oficial aplicado:\n" + "\n".join(
            [f"• {c['documento_id']} ({c.get('paso_exacto', '')}): {c.get('fragmento_aplicado', '')}" for c in ticket["citas"][:2]]
        )

    asunto = f"[{ticket['ticket_codigo']}] Actualización de Soporte Técnico - ConectaTec"
    mensaje = (
        f"Estimado/a {ticket['nombre_cliente']},\n\n"
        f"Su incidencia tecnológica '{ticket['descripcion_problema'][:80]}...' ha sido clasificada con Prioridad {ticket['prioridad']} "
        f"(SLA estimado: {ticket['sla_minutos']} minutos).\n\n"
        f"Diagnóstico preliminar / Solución:\n{ticket['solucion_propuesta']}"
        f"{citas_texto}\n\n"
        f"Estado del ticket: {ticket['estado'].upper()}\n"
        f"Mesa de Ayuda Tecnológica · ConectaTec / TecnoAula"
    )

    return PropuestaEnviarNotificacionOut(
        ticket_id=ticket["id"],
        ticket_codigo=ticket["ticket_codigo"],
        destinatario_email=ticket["email_cliente"],
        asunto_propuesto=asunto,
        mensaje_propuesto=mensaje,
        requiere_confirmacion_humana=True,
        tipo_accion="enviar_notificacion"
    )


@router.post(
    "/{ticket_id}/confirmar-envio",
    response_model=ResultadoConfirmacionHumanaOut,
    summary="Confirma y registra el envío de notificación al cliente tras revisión humana",
    description="Autoriza formalmente el despacho del mensaje al usuario registrando al operador responsable."
)
def confirmar_envio_notificacion_endpoint(ticket_id: int, payload: ConfirmarEnvioIn):
    """
    Fase 2 de Envío HITL:
    Registra el envío y marca 'notificacion_enviada=True' en auditoría.
    """
    ticket = obtener_ticket_limpio_por_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket #{ticket_id} no encontrado."
        )

    exito = confirmar_envio_notificacion(ticket_id, payload.operador_confirmador)
    ahora_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    ticket_actualizado = obtener_ticket_limpio_por_id(ticket_id)

    return ResultadoConfirmacionHumanaOut(
        exito=exito,
        accion_ejecutada="enviado",
        ticket_codigo=ticket["ticket_codigo"],
        mensaje=f"Notificación oficial enviada exitosamente a {payload.destinatario_email} por {payload.operador_confirmador}.",
        confirmado_por=payload.operador_confirmador,
        fecha_confirmacion=ahora_iso,
        ticket_actualizado=TicketOut(**ticket_actualizado) if ticket_actualizado else None
    )


@router.get(
    "/{ticket_id}/proponer-derivacion",
    response_model=PropuestaDerivarCuadrillaOut,
    summary="Genera orden propuesta de despacho presencial antes de derivar cuadrilla (HITL)",
    description="Calcula costo y herramientas requeridas antes de comprometer personal físico en campo."
)
def proponer_derivacion_cuadrilla(ticket_id: int):
    """
    Fase 1 de Derivación HITL:
    Presenta la justificación y costos operativos antes de despachar personal presencial.
    """
    ticket = obtener_ticket_limpio_por_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket #{ticket_id} no encontrado."
        )

    from app.tools.configuracion import obtener_tarifa_por_codigo
    tarifa_hora = obtener_tarifa_por_codigo("SRV-HORA-TECNICA-HABIL")
    costo_h = float(tarifa_hora.get("tarifa_usd", 15.00)) if tarifa_hora else 15.00

    return PropuestaDerivarCuadrillaOut(
        ticket_id=ticket["id"],
        ticket_codigo=ticket["ticket_codigo"],
        sector="Campus Universitario Ambato / Red GPON",
        motivo_derivacion=f"Avería física detectada: {ticket['descripcion_problema'][:100]} (Requiere intervención en caja NAP o acometida)",
        cuadrilla_sugerida="Cuadrilla Nº 03 de Planta Externa",
        herramientas_requeridas=[
            "Fusionadora óptica por arco voltaico Fujikura 70S",
            "Reflectómetro óptico en el dominio del tiempo (OTDR)",
            "Kit de conectores mecánicos SC/APC y bobina de lanzamiento"
        ],
        costo_estimado_usd=round(costo_h * 2.0, 2), # 2 horas estimadas de intervención
        tiempo_estimado_arribo_minutos=45,
        requiere_confirmacion_humana=True,
        tipo_accion="derivar_cuadrilla"
    )


@router.post(
    "/{ticket_id}/confirmar-derivacion",
    response_model=ResultadoConfirmacionHumanaOut,
    summary="Confirma y autoriza el despacho presencial de cuadrilla técnica (HITL)",
    description="Transiciona el ticket a 'escalado_cuadrilla' y genera orden de trabajo física ODT."
)
def confirmar_derivacion_cuadrilla_endpoint(ticket_id: int, payload: ConfirmarDerivacionIn):
    """
    Fase 2 de Derivación HITL:
    Ejecuta el escalamiento físico y genera la orden de trabajo ODT autorizada por el operador.
    """
    ticket = obtener_ticket_limpio_por_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket #{ticket_id} no encontrado."
        )

    import hashlib
    orden_id = payload.orden_despacho_id or f"ODT-FIBRA-{hashlib.sha256(ticket['ticket_codigo'].encode()).hexdigest()[:6].upper()}"

    exito = confirmar_derivacion_cuadrilla(
        ticket_id=ticket_id,
        operador=payload.operador_confirmador,
        orden_id=orden_id,
        cuadrilla=payload.cuadrilla_asignada
    )
    ahora_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    ticket_actualizado = obtener_ticket_limpio_por_id(ticket_id)

    return ResultadoConfirmacionHumanaOut(
        exito=exito,
        accion_ejecutada="derivado",
        ticket_codigo=ticket["ticket_codigo"],
        mensaje=f"Cuadrilla '{payload.cuadrilla_asignada}' despachada formalmente bajo orden {orden_id} por {payload.operador_confirmador}.",
        confirmado_por=payload.operador_confirmador,
        fecha_confirmacion=ahora_iso,
        ticket_actualizado=TicketOut(**ticket_actualizado) if ticket_actualizado else None
    )

