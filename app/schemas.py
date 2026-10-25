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
    modo_vulnerable: bool = Field(False, description="Desactiva defensas Pydantic y matriz determinista para simular alucinación e inyección libre (OWASP LLM01)")


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
    tokens_prompt: Optional[int] = Field(None, description="Tokens de entrada consumidos (prompt + system)")
    tokens_completado: Optional[int] = Field(None, description="Tokens de salida generados (JSON estructurado)")
    tokens_total: Optional[int] = Field(None, description="Total de tokens consumidos en la llamada LLM")
    modo_vulnerable: Optional[bool] = Field(False, description="True si se procesó en modo vulnerable sin defensas de seguridad")
    alucinacion_detectada: Optional[bool] = Field(False, description="True si se detectó violación de contrato o alucinación simulada")


class ClasificacionIA(BaseModel):
    """Salida estructurada extraída por el LLM desde la solicitud del usuario."""
    model_config = ConfigDict(extra="forbid")

    categoria: str = Field(..., description="Categoría técnica del incidente")
    impacto: str = Field(..., description="Nivel de impacto según alcance")
    urgencia: str = Field(..., description="Nivel de urgencia según criticidad")
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


# ============================================================================
# Esquemas del Personal TIC: Autenticación, RBAC y Gestión de Manuales RAG
# ============================================================================

class LoginIn(BaseModel):
    """Credenciales de acceso para el personal técnico TIC."""
    model_config = ConfigDict(extra="forbid")

    usuario: str = Field(..., min_length=3, max_length=100, description="Correo o alias del técnico TIC")
    password: str = Field(..., min_length=4, max_length=128, description="Contraseña de acceso")


class LoginOut(BaseModel):
    """Respuesta con token de sesión firmado para el operador TIC."""
    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., description="Token Bearer HMAC-SHA256")
    usuario: str = Field(..., description="Usuario autenticado")
    nombre_completo: str = Field(..., description="Nombre completo del técnico")
    rol: str = Field(..., description="Rol asignado (ej. administrador_tic)")
    expira_en_horas: int = Field(8, description="Vigencia del token en horas")


class PerfilTICOut(BaseModel):
    """Datos de la sesión activa del personal TIC."""
    model_config = ConfigDict(extra="forbid")

    usuario: str
    nombre_completo: str
    rol: str


class ManualItemOut(BaseModel):
    """Resumen de un manual técnico almacenado en data/raw/."""
    model_config = ConfigDict(extra="forbid")

    archivo: str = Field(..., description="Nombre del archivo (ej. DOC-01_luces_led_ont_huawei.md)")
    documento_id: str = Field(..., description="Código oficial (ej. DOC-01)")
    titulo: str = Field(..., description="Título descriptivo del procedimiento")
    categoria: str = Field(..., description="Categoría técnica (ONT, Wi-Fi, Fibra, etc.)")
    vigencia: Optional[str] = Field(None, description="Versión o fecha de vigencia del documento")
    tamano_bytes: int = Field(..., description="Tamaño del archivo en bytes")
    fecha_modificacion: str = Field(..., description="Fecha y hora de última modificación")


class ListaManualesOut(BaseModel):
    """Catálogo completo de manuales para el gestor documental TIC."""
    model_config = ConfigDict(extra="forbid")

    total: int
    manuales: List[ManualItemOut]


class ManualDetalleOut(BaseModel):
    """Contenido completo de un manual para visualización o edición."""
    model_config = ConfigDict(extra="forbid")

    archivo: str
    documento_id: str
    titulo: str
    contenido_markdown: str


class GuardarManualIn(BaseModel):
    """Payload para crear o editar un archivo Markdown en la base de conocimiento."""
    model_config = ConfigDict(extra="forbid")

    archivo: str = Field(..., min_length=3, max_length=150, description="Nombre del archivo .md")
    contenido_markdown: str = Field(..., min_length=20, description="Contenido estructurado en Markdown")
    sobrescribir: bool = Field(False, description="True para permitir sobrescribir archivos existentes")


class ConvertirDocIn(BaseModel):
    """Payload para conversión directa de archivos Word o PDF codificados en Base64."""
    model_config = ConfigDict(extra="forbid")

    nombre_archivo: str = Field(..., min_length=4, max_length=200, description="Nombre con extensión (.docx o .pdf)")
    contenido_base64: str = Field(..., description="Contenido del documento codificado en Base64")
    guardar_directo: bool = Field(False, description="True para guardar inmediatamente en data/raw/")


class ResultadoConversionOut(BaseModel):
    """Resultado estructurado de la extracción y conversión a Markdown."""
    model_config = ConfigDict(extra="forbid")

    nombre_archivo_md: str
    documento_id: str
    titulo: str
    contenido_markdown: str
    guardado_en_raw: bool
    mensaje: str
