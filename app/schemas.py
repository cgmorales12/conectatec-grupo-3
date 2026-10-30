"""
Esquemas Pydantic V2 para ConectaTec (Caso 03 · Grupo 3)
Contratos estrictos de entrada y salida con extra='forbid'
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# ============================================================================
# Enumeraciones y Contratos de Proveedor
# ============================================================================

class ProveedorLLMEnum(str, Enum):
    """Proveedores de Modelos de Lenguaje admitidos por el cliente encapsulado."""
    GEMINI = "gemini"
    GROQ = "groq"
    LOCAL_OFFLINE = "conmutador-local-offline"


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
    simular_error_429: bool = Field(False, description="Simula error HTTP 429 de proveedor para probar reintentos con espera exponencial")
    simular_timeout: bool = Field(False, description="Simula tiempo de espera agotado (timeout) en la llamada al modelo LLM")
    simular_respuesta_vacia: bool = Field(False, description="Simula respuesta vacía o incompleta devuelta por el modelo LLM")
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
# Esquemas Conversacionales y de Análisis Técnico (Endpoints Principales)
# ============================================================================

class MensajeHistorialChat(BaseModel):
    """Mensaje individual en el historial conversacional."""
    model_config = ConfigDict(extra="forbid")

    rol: str = Field(
        ...,
        pattern="^(user|model|asistente|system)$",
        description="Rol del emisor en la conversación"
    )
    contenido: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Contenido del mensaje conversacional"
    )


class SolicitudChatIn(BaseModel):
    """Payload de entrada para el endpoint conversacional con streaming (POST /chat)."""
    model_config = ConfigDict(extra="forbid")

    mensaje: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Pregunta o consulta técnica del usuario para el asistente"
    )
    historial: Optional[List[MensajeHistorialChat]] = Field(
        default_factory=list,
        description="Historial previo de la conversación para mantener contexto"
    )
    simular_caida_gemini: bool = Field(
        False,
        description="Simula caída de Gemini para verificar failover de streaming"
    )
    simular_caida_groq: bool = Field(
        False,
        description="Simula caída de Groq para verificar contingencia offline"
    )


class SolicitudAnalizarIn(BaseModel):
    """Payload para análisis técnico profundo de fallas o incidencias (POST /analizar)."""
    model_config = ConfigDict(extra="forbid")

    descripcion_problema: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Descripción detallada de la avería, síntomas o comportamiento anómalo"
    )
    equipo_afectado: Optional[str] = Field(
        "ONT / Router Wi-Fi",
        max_length=100,
        description="Equipo, servicio o plataforma reportada"
    )
    sintomas: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de síntomas o estados de luces observados"
    )



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


class ResultadoAnalizarOut(BaseModel):
    """Contrato de salida en formato JSON estructurado para POST /analizar."""
    model_config = ConfigDict(extra="forbid")

    diagnostico: str = Field(..., description="Diagnóstico técnico del problema identificado")
    causa_probable: str = Field(..., description="Causa raíz estimada del incidente")
    nivel_severidad: str = Field(..., description="Nivel de severidad técnica (Crítica, Alta, Media, Baja)")
    acciones_recomendadas: List[str] = Field(..., description="Lista ordenada de pasos correctivos o de mitigación")
    requiere_visita_campo: bool = Field(False, description="True si requiere asistencia física de cuadrilla técnica")
    documentos_sugeridos: List[str] = Field(default_factory=list, description="Manuales técnicos sugeridos para consulta")
    metadatos_ia: Optional[MetadatosIA] = Field(None, description="Métricas de ejecución, latencia en ms y consumo de tokens")


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
    vigencia: Optional[str] = Field(None, description="Versión o vigencia del documento")
    url: Optional[str] = Field(None, description="URL canónica oficial del procedimiento en la base de conocimiento")


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
    confirmado_por: Optional[str] = Field(None, description="Nombre del operador que autorizó el registro o acción")
    fecha_confirmacion: Optional[str] = Field(None, description="Fecha y hora de la confirmación humana")
    notificacion_enviada: bool = Field(False, description="True si la notificación por correo fue autorizada y enviada")
    cuadrilla_despachada: bool = Field(False, description="True si la derivación de cuadrilla presencial fue aprobada")
    orden_despacho_id: Optional[str] = Field(None, description="Identificador de la orden de trabajo de cuadrilla")


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


# ============================================================================
# Esquemas de Parámetros Desacoplados (Tarifas, SBU, Calendarios)
# ============================================================================

class TarifaItemOut(BaseModel):
    """Ítem individual del tarifario oficial de equipos y mano de obra."""
    model_config = ConfigDict(extra="forbid")

    codigo: str
    nombre: str
    categoria: str
    tarifa_usd: float
    unidad: str
    garantia_meses: Optional[int] = None
    descripcion: Optional[str] = None


class ItemPresupuestoIn(BaseModel):
    """Línea de ítem para cálculo de presupuesto técnico."""
    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(..., description="Código unívoco del ítem en config/tarifas.json")
    cantidad: float = Field(1.0, ge=0.01, description="Cantidad solicitada")


class PresupuestoIn(BaseModel):
    """Solicitud de cálculo de presupuesto determinista."""
    model_config = ConfigDict(extra="forbid")

    items: List[ItemPresupuestoIn]
    iva_porcentaje: float = Field(0.15, description="Porcentaje de IVA legal (0.15 = 15% Ecuador 2026)")


class PresupuestoCalculadoOut(BaseModel):
    """Resultado del cálculo determinista de presupuesto."""
    model_config = ConfigDict(extra="forbid")

    items_detalle: List[dict]
    subtotal_usd: float
    iva_porcentaje: float
    iva_usd: float
    total_usd: float
    moneda: str
    origen_tarifas: str


class SalarioBasicoOut(BaseModel):
    """Datos oficiales del Salario Básico Unificado desde config/parametros.yaml."""
    model_config = ConfigDict(extra="forbid")

    salario_basico_unificado: float
    moneda: str
    pais: str
    ano: int
    porcentaje_penalizacion_por_hora: float
    origen_configuracion: str


class PenalizacionSLAOut(BaseModel):
    """Cálculo determinista de penalización por exceso de SLA según SBU."""
    model_config = ConfigDict(extra="forbid")

    horas_retraso: float
    salario_basico_unificado: float
    porcentaje_aplicado_por_hora: float
    costo_penalizacion_por_hora_usd: float
    monto_penalizacion_total_usd: float
    moneda: str
    justificacion: str
    origen_regla: str


class ConsultaCalendarioOut(BaseModel):
    """Consulta de turno de soporte y días feriados desde config/calendario.json."""
    model_config = ConfigDict(extra="forbid")

    fecha: str
    hora: str
    es_habil: bool
    jornada: Optional[str] = None
    horario_vigente: Optional[str] = None
    motivo: str
    guardia_noc_24_7_activa: bool


# ============================================================================
# Esquemas de Confirmación Humana (Human-in-the-Loop - OWASP LLM08)
# Principio: «Antes de registrar, enviar o derivar, el humano autoriza»
# ============================================================================

class PropuestaRegistroTicketOut(BaseModel):
    """Propuesta estructurada de pre-triaje antes de registrar en base de datos."""
    model_config = ConfigDict(extra="forbid")

    ticket_codigo_propuesto: str
    nombre_cliente: str
    email_cliente: str
    descripcion_problema: str
    categoria_propuesta: str
    impacto_propuesto: str
    urgencia_propuesta: str
    prioridad_itil: str
    sla_minutos: int
    descripcion_sla: str
    solucion_propuesta: str
    citas: List[CitaRAG] = Field(default_factory=list)
    requiere_confirmacion_humana: bool = True
    tipo_accion: str = "registro_ticket"
    justificacion_ia: Optional[str] = None
    sintomas_detectados: List[str] = Field(default_factory=list)
    metadatos_ia: Optional[MetadatosIA] = None


class ConfirmarRegistroIn(BaseModel):
    """Payload para autorizar y persistir el registro del ticket tras revisión humana."""
    model_config = ConfigDict(extra="forbid")

    ticket_codigo_propuesto: str = Field(..., min_length=4, max_length=50)
    nombre_cliente: str = Field(..., min_length=2, max_length=100)
    email_cliente: str = Field(..., min_length=5, max_length=120)
    descripcion_problema: str = Field(..., min_length=5, max_length=2000)
    categoria: str = Field(..., min_length=3, max_length=100)
    impacto: str = Field(..., min_length=3, max_length=20)
    urgencia: str = Field(..., min_length=3, max_length=20)
    prioridad: str = Field(..., min_length=3, max_length=20)
    sla_minutos: int = Field(..., ge=1, le=10080)
    descripcion_sla: str = Field(..., min_length=5, max_length=300)
    solucion_propuesta: str = Field(..., min_length=10, max_length=2000)
    citas: List[CitaRAG] = Field(default_factory=list)
    justificacion: Optional[str] = None
    sintomas_detectados: List[str] = Field(default_factory=list)
    operador_confirmador: str = Field(..., min_length=2, max_length=100, description="Nombre del técnico u operador que aprueba el registro")
    notas_operador: Optional[str] = Field(None, max_length=500, description="Observaciones técnicas añadidas manualmente")


class PropuestaEnviarNotificacionOut(BaseModel):
    """Borrador de notificación por correo/resolución generado antes de ser enviado."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: int
    ticket_codigo: str
    destinatario_email: str
    asunto_propuesto: str
    mensaje_propuesto: str
    requiere_confirmacion_humana: bool = True
    tipo_accion: str = "enviar_notificacion"


class ConfirmarEnvioIn(BaseModel):
    """Autorización y confirmación humana para remitir la notificación oficial al usuario."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: int
    destinatario_email: str = Field(..., min_length=5, max_length=120)
    asunto: str = Field(..., min_length=5, max_length=200)
    mensaje_final: str = Field(..., min_length=10, max_length=5000)
    operador_confirmador: str = Field(..., min_length=2, max_length=100)


class PropuestaDerivarCuadrillaOut(BaseModel):
    """Propuesta de escalamiento presencial con personal de planta externa."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: int
    ticket_codigo: str
    sector: str
    motivo_derivacion: str
    cuadrilla_sugerida: str
    herramientas_requeridas: List[str]
    costo_estimado_usd: float
    tiempo_estimado_arribo_minutos: int
    requiere_confirmacion_humana: bool = True
    tipo_accion: str = "derivar_cuadrilla"


class ConfirmarDerivacionIn(BaseModel):
    """Autorización explícita para despachar cuadrilla física presencial de campo."""
    model_config = ConfigDict(extra="forbid")

    ticket_id: int
    cuadrilla_asignada: str = Field(..., min_length=3, max_length=120)
    sector: str = Field(..., min_length=3, max_length=120)
    motivo: str = Field(..., min_length=5, max_length=500)
    operador_confirmador: str = Field(..., min_length=2, max_length=100)
    autoriza_despacho_presencial: bool = True
    orden_despacho_id: Optional[str] = Field(None, max_length=40)


class ResultadoConfirmacionHumanaOut(BaseModel):
    """Resultado auditado de la acción humana confirmada (HITL)."""
    model_config = ConfigDict(extra="forbid")

    exito: bool
    accion_ejecutada: str
    ticket_codigo: str
    mensaje: str
    confirmado_por: str
    fecha_confirmacion: str
    ticket_actualizado: Optional[TicketOut] = None


