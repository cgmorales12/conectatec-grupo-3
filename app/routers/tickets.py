"""
Enrutador de Tickets de Soporte Técnico - ConectaTec
Endpoints: Clasificación Inteligente, Consulta de Tickets y Cambio de Estado Kanban.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
import uuid


from app.schemas import (
    SolicitudTicketIn,
    TicketOut,
    ListaTicketsOut,
    ActualizarEstadoIn,
    CitaRAG,
    DiagnosticoRAG,
    MetadatosIA
)
from app.services.llm import clasificar_solicitud
from app.tools.priorizar import calcular_prioridad_itil
from app.services.rag import consultar_base_conocimiento
from app.database import guardar_ticket, listar_tickets, actualizar_estado_ticket

router = APIRouter(prefix="/v1/tickets", tags=["Tickets de Soporte"])


@router.post(
    "/clasificar",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="Clasifica y genera un ticket de soporte con IA y RAG"
)
def clasificar_y_crear_ticket(solicitud: SolicitudTicketIn):
    """
    Recibe el reporte de una avería, extrae impacto y urgencia con Gemini/Groq,
    calcula la prioridad matemática con la matriz ITIL y consulta los manuales técnicos RAG.
    """
    # 1. Extracción estructurada con IA y Gateway resiliente (con soporte de Chaos Engineering y Modo Vulnerable)
    clasificacion_ia, metadatos_ia = clasificar_solicitud(
        solicitud.descripcion_problema,
        simular_caida_gemini=solicitud.simular_caida_gemini,
        simular_caida_groq=solicitud.simular_caida_groq,
        modo_vulnerable=solicitud.modo_vulnerable
    )
    
    # 2. Priorización determinista por código Python (Matriz ITIL) vs Alucinación en Modo Vulnerable
    if solicitud.modo_vulnerable:
        prioridad_nombre = "Infinita (Alucinada)"
        sla_minutos = 0
        descripcion_sla = "SLA Vulnerado · Prioridad alucinada por LLM sin matriz determinista ITIL"
        
        diagnostico_rag = DiagnosticoRAG(
            solucion_propuesta="Solución Alucinada: Proceder con teletransportación cuántica de fibra óptica descrita en manual ficticio DOC-99.",
            citas=[
                CitaRAG(
                    documento_id="DOC-99 (Inventado)",
                    titulo_documento="Teletransportación Cuántica de Fibra Óptica (Alucinación)",
                    paso_exacto="Paso Cuántico 1.1: Fusión de fotones estelares",
                    fragmento_aplicado="«Inventando el manual técnico inexistente DOC-99 de teletransportación cuántica de fibra óptica.»"
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
