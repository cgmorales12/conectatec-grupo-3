# Arquitectura del Sistema: ConectaTec

## 1. Visión General del Sistema
*ConectaTec* es una solución de triaje inteligente y gestión de incidentes diseñada para proveedores locales de Internet (ISP). Automatiza la categorización, evaluación de impacto/urgencia y diagnóstico de primer nivel a partir de guías y manuales técnicos oficiales, escalando únicamente los casos que requieren atención técnica de campo.

---

## 2. Diagrama de Contexto (C4 Nivel 1)
Describe las interacciones de los usuarios y sistemas externos con la plataforma ConectaTec.

```mermaid
graph TD
    subgraph Usuarios
        C[Cliente de Internet]
        T[Técnico de Soporte]
        O[Operador de Mesa de Ayuda]
    end

    subgraph Plataforma ConectaTec
        CT[Sistema ConectaTec<br/>Triaje y Gestión ISP]
    end

    subgraph Sistemas Externos
        LLM[Google Gemini / Groq API]
        MAIL[Servidor de Correo Notificaciones]
        OLT[Sistema de Monitoreo OLT (Semana 3)]
    end

    C -->|Reporta incidentes y recibe diagnóstico| CT
    T -->|Gestiona tickets priorizados en Kanban| CT
    O -->|Supervisa colas y excepciones| CT

    CT -->|Clasificación y extracción JSON| LLM
    CT -->|Envío de alertas de tickets| MAIL
    CT -.->|Consulta de telemetría de red| OLT

graph TD
    subgraph Usuarios
        Cliente[Cliente de Internet]
        Tecnico[Técnico de Soporte]
    end

    subgraph Sistema ConectaTec
        WEB["Frontend Web<br/><b>HTML + JavaScript / Responsive</b><br/>Formulario de reporte y tablero Kanban"]
        API["Backend API<br/><b>FastAPI (Python)</b><br/>Endpoints REST, validación con Pydantic"]
        SERVICE_IA["Servicio IA (llm.py)<br/>Manejo de reintentos, fallback y timeout"]
        PROMPTS["Prompts Versionados<br/><b>app/prompts/</b><br/>system_v1, v2, v3"]
        DB[("Base de Datos<br/><b>SQLite (soporte.db)</b><br/>Tickets, estados e historial")]
        LOGS["Registro y Auditoría<br/>Logs estructurados sin datos personales"]
        RAG[("Base Vectorial RAG<br/><i>(Semana 3 - ChromaDB)</i><br/>15 manuales técnicos")]
        AGENT["Agente y Herramientas<br/><i>(Semana 3)</i><br/>clasificar, priorizar, buscar_solucion, escalar"]
    end

    subgraph Proveedores Externos
        GEMINI["Proveedor Principal<br/><b>Google Gemini 1.5 Flash</b>"]
        GROQ["Proveedor de Respaldo<br/><b>Groq (Llama 3.3 70B)</b>"]
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

[10:00 p.m., 20/10/2026] Cnt Moralitos: graph TD
    subgraph Usuarios
        Cliente[Cliente de Internet]
        Tecnico[Técnico de Soporte]
    end

    subgraph Sistema ConectaTec
        WEB["Frontend Web<br/><b>HTML + JavaScript / Responsive</b><br/>Formulario de reporte y tablero Kanban"]
        API["Backend API<br/><b>FastAPI (Python)</b><br/>Endpoints REST, validación con Pydantic"]
        SERVICE_IA["Servicio IA (llm.py)<br/>Manejo de reintentos, fallback y timeout"]
        PROMPTS["Prompts Versionados<br/><b>app/prompts/</b><br/>system_v1, v2, v3"]
        DB[("Base de Datos<br/><b>SQLite (soporte.db)</b><br/>Tickets, estados e historial")]
        LOGS["Registro y Auditoría<br/>Logs estructurados sin datos personales"]
        RAG[("Base Vectorial RAG<br/><i>(Semana 3 - ChromaDB)</i><br/>15 manuales técnicos")]
        AGENT["Agente y Herramientas<br/><i>(Semana 3)</i><br/>clasificar, priorizar, buscar_solucion, escalar"]
    end

    subgraph Proveedores Externos
        GEMINI["Proveedor Principal<br/><b>Google Gemini 1.5 Flash</b>"]
        GROQ["Proveedor de Respaldo<br/><b>Groq (Llama 3.3 70B)</b>"]
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
[10:01 p.m., 20/10/2026] Cnt Moralitos: Método	Endpoint	Propósito	Formato Entrada / Salida
POST	/solicitudes	Recibe reporte de incidente del cliente, invoca al LLM y calcula prioridad determinista.	
In: SolicitudCreate (JSON)


Out: TicketResponse (JSON estructurado)

GET	/tickets	Obtiene el listado consolidado de tickets clasificados para el tablero técnico.	
In: Query params (estado, prioridad)


Out: Listado de tickets (JSON)

PATCH	/tickets/{id}	Actualiza el estado operativo de un ticket (Nuevo, En atención, Resuelto, Escalado).	
In: EstadoUpdate (JSON)


Out: TicketResponse (JSON)

GET	/health	Chequeo de salud del servicio backend, conectividad con base de datos y proveedor LLM.	
In: Ninguno


Out: {"status": "ok"}

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

Llamada Principal: Toda solicitud de inferencia se dirige inicialmente a Google Gemini 1.5 Flash con un tiempo límite (timeout) de 3 segundos.

Reintentos: Se aplica reintento con retroceso exponencial (exponential backoff) ante errores transitorios de red.

Conmutación por Falla (Fallback): Si la API responde con límite de tasa (HTTP 429) o falla de servicio (HTTP 5xx), el cliente conmuta de inmediato a Groq con el modelo llama-3.3-70b-versatile.

Degradación Elegante: Si ambos proveedores fallan, el ticket se registra automáticamente en estado Nuevo con prioridad por defecto Media para revisión manual, garantizando que el usuario nunca pierda su reporte.

4. *Confirmar el Commit:*
   * En la esquina superior derecha, pulsar el botón verde *Commit changes...*[cite: 18].
   * En el mensaje del commit puede colocar[cite: 18]:  
     docs: agregar arquitectura C4 (nivel 1 y 2), endpoints y flujo de consulta
   * Verificar que esté marcado *Commit directly to the main branch*[cite: 18].
   * Hacer clic en el botón verde *Commit changes*[cite: 18].

---

Una vez que él guarde el archivo, regresa a tu formulario de la *Lista de verificación de la entrega 1* y marca con un visto la tercera casilla:  
*☑️ docs/03-arquitectura.md*[cite: 16].

Avísame cuando Fernando lo suba para guiarte con el paso 4 (docs/04-fuentes.md)[cite: 16].
