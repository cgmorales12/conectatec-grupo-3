"""
Esquemas Pydantic V2 para ConectaTec (Caso 03 · Grupo 3)
Contratos estrictos de entrada y salida con extra='forbid'
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# ============================================================================
# Esquemas de Entrada (Request DTOs)
# ============================================================================

class SolicitudTicketIn(BaseModel):
    """Payload de entrada para ingresar un reporte de incidente técnico."""
    model_config = ConfigDict(extra="forbid")

    nombre_cliente: str = Field(..., min_length=2, max_length=100, description="Nombre del abonado o usuario que reporta")
    email_cliente: str = Field(..., min_length=5, max_length=120, description="Correo electrónico de contacto")
    descripcion_problema: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Descripción detallada de la avería, síntomas o luces del equipo"
    )
    codigo_abonado: Optional[str] = Field(None, max_length=20, description="Código de contrato o cliente ISP")
    # Banderas de Simulación de Resiliencia / Chaos Engineering (Demostración de Grado)
    simular_caida_gemini: bool = Field(False, description="Simula fallo HTTP 503 o cuota 429 en Google Gemini")
    simular_caida_groq: bool = Field(False, description="Simula indisponibilidad en el respaldo Groq Cloud")
    simular_caida_rag: bool = Field(False, description="Simula corte o desconexión del corpus de 15 manuales RAG")


class ActualizarEstadoIn(BaseModel):
    """Payload para actualizar el estado del ticket en el tablero Kanban."""
    model_config = ConfigDict(extra="forbid")

    nuevo_estado: str = Field(
        ...,
        pattern="^(nuevo|en_atencion|resuelto|escalado_cuadrilla)$",
        description="Estado del ticket: nuevo, en_atencion, resuelto, escalado_cuadrilla"
    )
    observacion: Optional[str] = Field(None, max_length=500, description="Nota técnica sobre el cambio de estado")


# ============================================================================
# Esquemas de IA y Negocio (Internal & Output DTOs)
# ============================================================================

class MetadatosIA(BaseModel):
    """Metadatos de transparencia sobre el proveedor y modelo de IA ejecutado."""
    model_config = ConfigDict(extra="forbid")

    proveedor: str = Field(..., description="Proveedor que atendió: gemini o groq")
    modelo: str = Field(..., description="Nombre del modelo LLM ejecutado")
    conmutado: bool = Field(False, description="True si falló el modelo primario y actuó el respaldo")
    motivo_conmutacion: Optional[str] = Field(None, description="Detalle del fallo que activó el respaldo")
    latencia_ms: Optional[float] = Field(None, description="Tiempo de inferencia en milisegundos")


class ClasificacionIA(BaseModel):
    """Salida estructurada extraída por el LLM desde la solicitud del usuario."""
    model_config = ConfigDict(extra="forbid")

    categoria: str = Field(..., description="Categoría técnica del incidente")
    impacto: str = Field(..., pattern="^(Alto|Medio|Bajo)$", description="Nivel de impacto según alcance")
    urgencia: str = Field(..., pattern="^(Alta|Media|Baja)$", description="Nivel de urgencia según criticidad")
    sintomas_detectados: List[str] = Field(default_factory=list, description="Lista de síntomas o luces identificadas")
    justificacion: str = Field(..., description="Breve justificación técnica de la clasificación")


class CitaRAG(BaseModel):
    """Cita verificable del corpus documental que respalda el diagnóstico."""
    model_config = ConfigDict(extra="forbid")

    documento_id: str = Field(..., description="Identificador del manual (ej. DOC-01)")
    titulo_documento: str = Field(..., description="Título oficial del manual técnico")
    paso_exacto: str = Field(..., description="Paso o sección citada (ej. Paso 2)")
    fragmento_aplicado: str = Field(..., description="Texto instructivo para el cliente")


class DiagnosticoRAG(BaseModel):
    """Diagnóstico de primer nivel generado por RAG con citas."""
    model_config = ConfigDict(extra="forbid")

    solucion_propuesta: str = Field(..., description="Pasos de autoatención recomendados al usuario")
    citas: List[CitaRAG] = Field(default_factory=list, description="Manuales oficiales citados")
    requiere_visita_campo: bool = Field(False, description="True si existe daño físico que requiere cuadrilla")


class PrioridadSLA(BaseModel):
    """Cálculo determinista de prioridad y tiempo máximo de atención ITIL."""
    model_config = ConfigDict(extra="forbid")

    prioridad: str = Field(..., description="Prioridad calculada: Alta, Media o Baja")
    sla_minutos: int = Field(..., description="Tiempo máximo de resolución en minutos")
    descripcion_sla: str = Field(..., description="Descripción del nivel de servicio")


class TicketOut(BaseModel):
    """Contrato de salida limpio para el frontend y clientes de API."""
    model_config = ConfigDict(extra="forbid")

    id: int
    ticket_codigo: str
    fecha_creacion: str
    nombre_cliente: str
    email_cliente: str
    descripcion_problema: str
    categoria: str
    impacto: str
    urgencia: str
    prioridad: str
    sla_minutos: int
    descripcion_sla: str
    solucion_propuesta: str
    citas: List[CitaRAG]
    estado: str
    requiere_revision_humana: bool
    metadatos_ia: MetadatosIA
    justificacion: Optional[str] = Field(None, description="Justificación técnica de la clasificación generada por la IA")
    sintomas_detectados: List[str] = Field(default_factory=list, description="Lista de síntomas técnicos identificados")


class ListaTicketsOut(BaseModel):
    """Lista paginada de tickets para el tablero Kanban."""
    model_config = ConfigDict(extra="forbid")

    total_tickets: int
    tickets: List[TicketOut]


# ============================================================================
# Esquema de Errores Estándar RFC 9457 (Problem Details)
# ============================================================================

class DetalleProblemaRFC9457(BaseModel):
    """Formato estándar de error application/problem+json según RFC 9457."""
    model_config = ConfigDict(extra="forbid")

    type: str = Field(..., description="URI de referencia del tipo de error")
    title: str = Field(..., description="Título legible del problema")
    status: int = Field(..., description="Código de estado HTTP")
    detail: str = Field(..., description="Explicación detallada del error")
    instance: str = Field(..., description="Identificador único opaco de la solicitud")
