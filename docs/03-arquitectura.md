## 1. Contexto general del sistema

```mermaid
flowchart TD
    subgraph Usuarios
        C["Cliente de Internet"]
        T["Técnico de Soporte"]
        O["Operador de Mesa de Ayuda"]
    end

    subgraph Plataforma_ConectaTec
        CT["Sistema ConectaTec<br/>Triaje y Gestión ISP"]
    end

    subgraph Sistemas_Externos
        LLM["Google Gemini / Groq API"]
        MAIL["Servidor de Correo Notificaciones"]
        OLT["Sistema de Monitoreo OLT (Semana 3)"]
    end

    C -->|Reporta incidentes y recibe diagnóstico| CT
    T -->|Gestiona tickets priorizados en Kanban| CT
    O -->|Supervisa colas y excepciones| CT

    CT -->|Clasificación y extracción JSON| LLM
    CT -->|Envío de alertas de tickets| MAIL
    CT -.->|Consulta de telemetría de red| OLT
```

## 2. Arquitectura interna de ConectaTec

```mermaid
flowchart TD
    subgraph Usuarios
        Cliente["Cliente de Internet"]
        Tecnico["Técnico de Soporte"]
    end

    subgraph Sistema_ConectaTec
        WEB["Frontend Web<br/>HTML + JavaScript / Responsive<br/>Formulario de reporte y tablero Kanban"]
        API["Backend API<br/>FastAPI (Python)<br/>Endpoints REST, validación con Pydantic"]
        SERVICE_IA["Servicio IA (llm.py)<br/>Manejo de reintentos, fallback y timeout"]
        PROMPTS[("Prompts Versionados<br/>app/prompts/<br/>system_v1, v2, v3")]
        DB[("Base de Datos<br/>SQLite (soporte.db)<br/>Tickets, estados e historial")]
        LOGS["Registro y Auditoría<br/>Logs estructurados sin datos personales"]
        RAG[("Base Vectorial RAG<br/>Semana 3 - ChromaDB<br/>15 manuales técnicos")]
        AGENT["Agente y Herramientas<br/>Semana 3<br/>clasificar, priorizar, buscar_solucion, escalar"]
    end

    subgraph Proveedores_Externos
        GEMINI["Proveedor Principal<br/>Google Gemini 1.5 Flash"]
        GROQ["Proveedor de Respaldo<br/>Groq (Llama 3.3 70B)"]
        MAIL_EXT["Servidor de Correo"]
    end

    Cliente -->|HTTPS / JSON| WEB
    Tecnico -->|HTTPS / JSON| WEB
    WEB -->|REST API| API

    API -->|Carga de plantillas| PROMPTS
    API -->|Lectura / Escritura| DB
    API -->|Registro de eventos| LOGS
    API -->|Llamadas orquestadas| SERVICE_IA

    SERVICE_IA -->|API Key vía .env| GEMINI
    SERVICE_IA -.->|Fallback ante 429/timeout| GROQ
    API -->|Alertas| MAIL_EXT

    API -.->|Búsqueda contextual| RAG
    API -.->|Orquestación autónoma| AGENT
```

## 3. Endpoints principales

| Método | Endpoint | Propósito | Formato Entrada / Salida |
|--------|----------|-----------|---------------------------|
| POST | `/chat` | **Conversacional Interactivo (Streaming):** Diálogo técnico continuo token a token con asistencia en vivo. | **In:** `SolicitudChatIn` (Pydantic, `extra="forbid"`)<br/>**Out:** `StreamingResponse` (`text/plain; charset=utf-8` o SSE) |
| POST | `/clasificar` | **Triaje e Inferencia Estructurada:** Extracción de categoría, impacto y urgencia con cálculo ITIL determinista. | **In:** `SolicitudTicketIn` (Pydantic, `extra="forbid"`)<br/>**Out:** `TicketOut` (JSON estricto Pydantic) |
| POST | `/analizar` | **Diagnóstico Técnico de Averías:** Análisis de causas probables, severidad y pasos correctivos. | **In:** `SolicitudAnalizarIn` (Pydantic, `extra="forbid"`)<br/>**Out:** `ResultadoAnalizarOut` (JSON estricto Pydantic) |
| GET | `/v1/tickets` | Listado consolidado de tickets clasificados para el tablero técnico Kanban. | **In:** Query params opcionales<br/>**Out:** `ListaTicketsOut` (JSON) |
| PUT | `/v1/tickets/{codigo}/estado` | Actualiza el estado operativo de un ticket (`nuevo`, `en_atencion`, `resuelto`, `escalado_cuadrilla`). | **In:** `ActualizarEstadoIn` (JSON)<br/>**Out:** `TicketOut` (JSON) |
| GET | `/v1/salud` | Chequeo de salud del servicio backend, arquitectura y conectividad de modelos. | **In:** Ninguno<br/>**Out:** `{"status": "ok", "servicio": "conectatec-api"}` |


## 4. Secuencia de atención de una solicitud

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente
    participant FE as Frontend Web
    participant BE as Backend FastAPI
    participant LLM as Google Gemini 1.5
    participant DB as SQLite (soporte.db)

    C->>FE: Completa formulario de falla técnica
    FE->>BE: POST /solicitudes (payload con descripción)
    BE->>BE: Sanitiza texto (remueve contraseñas/datos sensibles)
    BE->>LLM: Prompt estructurado (system_v1.md) + solicitud
    LLM-->>BE: JSON {categoría, impacto, urgencia, diagnostico}
    BE->>BE: Calcula prioridad determinista (Matriz ITIL en código)
    BE->>DB: Guarda ticket con estado "Nuevo" y prioridad
    BE-->>FE: HTTP 201 con ticket y pasos de diagnóstico
    FE-->>C: Muestra diagnóstico guiado y código de ticket
```

## 5. Estrategia de tolerancia a fallos

**Llamada principal:** Toda solicitud de inferencia se dirige inicialmente a Google Gemini 1.5 Flash con un tiempo límite (`timeout`) de 3 segundos.

**Reintentos:** Se aplica reintento con retroceso exponencial (*exponential backoff*) ante errores transitorios de red.

**Conmutación por falla (Fallback):** Si la API responde con límite de tasa (HTTP 429) o falla de servicio (HTTP 5xx), el cliente conmuta de inmediato a Groq con el modelo `llama-3.3-70b-versatile`.

**Degradación elegante:** Si ambos proveedores fallan, el ticket se registra automáticamente en estado `Nuevo` con prioridad por defecto `Media` para revisión manual, garantizando que el usuario nunca pierda su reporte.
