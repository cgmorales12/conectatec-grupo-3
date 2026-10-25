# AGENTS.md · Reglas de Contexto Persistente para Asistentes y Agentes de Código
**Proyecto:** TecnoAula — Mesa de Ayuda Inteligente para Instituciones Educativas (Caso N.º 03 · Grupo 3)  
**Seminario de Titulación:** Ingeniería de Software con IA Generativa — UNIANDES (Octubre – Noviembre 2026)  
**Integrantes del Grupo 3:**  
1. **Christian Guillermo Morales González** (Tech Lead / Coordinador — GitHub: `cgmorales12`)  
2. **Luis Fernando Ribera Alajo** (Builder / Arquitectura — GitHub: `fernandolribera`)  
3. **Amalia Geoconda Iguasnia Escobar** (QA / Seguridad y Requerimientos — GitHub: `Geocoiguasnia76`)  
**Docente Evaluador:** Heyler Fabio Guaza (Ing. Informático · Mg. en Ciberseguridad · OPD · Abogado)  
**Repositorio GitHub:** `https://github.com/cgmorales12/conectatec-mvp`  

---

## 1. Misión, Filosofía y Alcance del Proyecto
El objetivo del Grupo 3 es construir **TecnoAula**, una aplicación web de triaje y resolución inteligente de incidencias tecnológicas para instituciones educativas (docentes, personal administrativo y técnicos).

### 1.1. Principio Rector de Arquitectura
> ***«El modelo propone, el código dispone.»***  
> El Modelo de Lenguaje (LLM) es un componente externo, probabilístico, falible y costoso. Todo su comportamiento debe estar gobernado por código backend determinista, esquemas estrictos de validación, manejo estructurado de errores y reglas de negocio inviolables.

### 1.2. Alcance Funcional del MVP Sencillo
1. **Recepción de Solicitudes:** Vía formulario web interactivo o correo simulado (averías de proyectores, Wi-Fi de campus, correo institucional, impresoras, Moodle/EVA y computadoras de laboratorios).
2. **Clasificación Estructurada (IA):** Extracción de categoría, impacto y urgencia mediante JSON validado con Pydantic.
3. **Priorización Determinista (Código):** Cálculo matemático de prioridad (`Alta`, `Media`, `Baja`) y SLA de resolución leyendo `config/matriz_prioridad.json`. El LLM **nunca** calcula la prioridad.
4. **Resolución de Primer Nivel (RAG):** Búsqueda semántica en ChromaDB sobre un corpus de 15 manuales técnicos oficiales con citas verificables (ID de documento y paso exacto).
5. **Tablero Kanban de Tickets:** Interfaz visual con estados (`nuevo`, `en atención`, `resuelto`, `escalado`), asignación a técnicos y derivación presencial cuando se requiere intervención física.

> **Restricción de Producto:** La interfaz principal es un **tablero de tickets con estados**, NO una sala de chat abierta sin propósito.

---

## 2. Nomenclatura e Idioma de Carpetas y Archivos
Todo el repositorio debe mantener su nomenclatura, documentación y comentarios en **español**:

```
.
├── app/                        # Perímetro backend de la aplicación (FastAPI)
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada y configuración de endpoints
│   ├── schemas.py              # Esquemas Pydantic V2 de entrada/salida (extra="forbid")
│   ├── routers/                # Enrutadores modulares (clasificacion, tickets, salud)
│   ├── services/               # Lógica de integración LLM (Gemini, Groq, conmutación)
│   ├── tools/                  # Funciones deterministas (priorizar.py leyendo JSON)
│   └── database.py             # Conexión y repositorio SQLite parametrizado
├── config/                     # Configuraciones deterministas del negocio
│   └── matriz_prioridad.json   # Matriz ITIL de Impacto x Urgencia y tiempos SLA
├── data/                       # Almacenamiento de datos y corpus
│   ├── raw/                    # Manuales y procedimientos técnicos en PDF / Markdown
│   └── chroma/                 # Base de datos vectorial persistente para RAG
├── docs/                       # Documentación técnica, académica y guías de defensa
│   ├── 01-propuesta.md         # Propuesta formal del proyecto
│   ├── 02-historias-usuario.md # Historias de usuario ágiles con Gherkin BDD
│   ├── 03-arquitectura.md      # Modelo C4 (Contexto, Contenedores, Componentes)
│   ├── 04-fuentes.md           # Inventario y chunking de los 15 manuales técnicos
│   ├── 05-prompts.md           # Catálogo versionado de prompts (R.E.C.E.T.A.)
│   ├── 06-manual-usuario.md    # Manual paso a paso para el usuario final / docente
│   ├── 07-manual-tecnico.md    # Manual de despliegue, arquitectura y mantenimiento
│   ├── 08-guia-defensa.md      # Guía para la defensa de grado y preguntas del jurado
│   └── 09-decisiones/          # Registros de Decisiones de Arquitectura (ADR-001 a 004)
├── frontend/                   # Interfaz de usuario sencilla (Streamlit o HTML/JS)
│   └── app.py                  # Tablero Kanban y formulario de tickets
├── tests/                      # Suite de pruebas automatizadas con Mocks
│   └── test_endpoints.py       # Pruebas unitarias de endpoints sin conexión a internet
├── .env.example                # Plantilla de variables de entorno con claves vacías
├── .gitignore                  # Registro estricto de secretos y temporales
├── requirements.txt            # Dependencias del proyecto fijadas por versión
└── README.md                   # Guía de inicio rápido para cualquier evaluador
```

---

## 3. Estrategia de Ahorro y Optimización de Tokens

Para garantizar que el sistema opere con **consumo mínimo de tokens** y bajo costo (o costo cero):

1. **Context Caching de Gemini:**
   - La API de Gemini cachea implícitamente prefijos repetidos de $\ge 4.096$ tokens (-50% latencia y -75% costo de tokens de entrada).
   - El *System Prompt* institucional y las políticas fijas se colocan siempre al inicio. **Nunca** anteponer la fecha u hora con segundos al comienzo del prompt.
2. **Prompts Concisos con Delimitadores XML:**
   - Redacción directa bajo el método R.E.C.E.T.A. sin rodeos literarios ni redundancias.
   - Aislamiento estricto de la entrada del usuario mediante etiquetas `<solicitud>...</solicitud>`.
3. **Modelo Liviano y Resiliente (Fallback y Transparencia):**
   - **Modelo Primario:** `gemini-1.5-flash` (alta velocidad, bajo costo, ventana amplia).
   - **Modelo Secundario (Fallback):** `llama-3.3-70b-versatile` en Groq Cloud (API ultrarrápida y gratuita para contingencia ante caídas HTTP 503 o cuotas 429).
   - **Transparencia Operativa y Notificación:** Si el modelo primario falla (por timeout, cuota 429 o error 503) y entra el respaldo (Groq), el sistema debe registrarlo y notificarlo de forma explícita tanto en los logs como en el contrato de salida y en la interfaz de usuario:
     * El payload de respuesta incluirá los metadatos: `proveedor: "gemini" | "groq"`, `modelo: str`, `conmutado: bool` y `motivo_conmutacion: Optional[str]`.
     * La interfaz gráfica (Frontend) mostrará un distintivo visual claro: `🟢 Proveedor: Gemini 1.5 Flash` cuando opere normalmente, o `🟠 Respaldo Activo: Groq Llama 3.3 (Motivo: Gemini no disponible)` cuando ocurra una conmutación.
4. **Embeddings Locales para RAG:**
   - Vectorización de fragmentos de manuales con modelos locales ligeros (`all-MiniLM-L6-v2`) o embeddings por lotes, evitando llamadas costosas por cada búsqueda semántica.
5. **Filtrado Previo Determinista:**
   - Consultas habituales o repetidas se resuelven consultando primero la base local o caché de preguntas frecuentes antes de invocar al LLM.

---

## 4. Perímetro de Ciberseguridad y Privacidad (LOPDP y OWASP LLM 2025)

### 4.1. Cero Secretos en Git
- Prohibición absoluta de escribir API Keys, tokens o credenciales en el código fuente o en commits de Git.
- Cargar siempre las credenciales mediante variables de entorno en el backend (`os.environ.get("LLM_API_KEY")`).
- El archivo `.env` debe permanecer estrictamente en `.gitignore`.

### 4.2. Cumplimiento LOPDP (Ecuador) y Mitigación de Fugas (OWASP LLM02 / LLM07)
- **Anonimización de Contraseñas:** Si un docente incluye su contraseña por error en el correo de reporte, el backend debe detectarla mediante expresiones regulares, emitir una advertencia de seguridad y sustituirla por `[CONFIDENCIAL_REMOVIDO]` antes de persistir o enviar al LLM.
- **Filtro de Contrato (`response_model`):** FastAPI utiliza esquemas de salida que impiden la fuga de PII, system prompts, URLs internas o costos de inferencia hacia el navegador.
- **Consultas Parametrizadas:** Ninguna entrada del usuario se concatena en sentencias SQL. Se usa el marcador `?` en SQLite para neutralizar inyecciones SQL.

### 4.3. Mitigación de Inyección de Prompts y XSS (OWASP LLM01 / LLM05)
- **4 Capas de Defensa:**
  1. *Delimitación semántica:* `<solicitud>{texto}</solicitud>`.
  2. *Esquemas Pydantic cerrados:* `model_config = ConfigDict(extra="forbid")`.
  3. *Lógica determinista:* La acción la decide el código Python evaluando banderas booleanas, no la prosa del modelo.
  4. *Sanitización en Frontend:* Todo contenido retornado por el modelo se renderiza como texto plano escapado o se pasa por `DOMPurify` para evitar ejecución de scripts maliciosos.

### 4.4. Control de Consumo (Token Bucket)
- Implementación de un limitador de tasa por sesión (capacidad 10 fichas, recarga de 1 ficha cada 6 segundos).
- Solicitudes abusivas reciben **`429 Too Many Requests`** con encabezado `Retry-After: N` según RFC 6585.

---

## 5. Arquitectura del Backend y Manejo de Errores (RFC 9457)

1. **Concurrencia en FastAPI (AnyIO):**
   - Endpoints con llamadas síncronas a SDKs de IA se declaran como `def` estándar para aprovechar el pool de 40 hilos de AnyIO, evitando el bloqueo del bucle de eventos que provocaría un `async def` mal implementado.
2. **Formato de Error Estándar (`application/problem+json`):**
   - Todos los errores retornan un payload con `type`, `title`, `status`, `detail` e `instance`.
   - Ante errores 500, se expone un identificador de rastreo opaco (`req-XXXX`), guardando el traceback exclusivamente en el servidor.
3. **El Protocolo de Corrección y Derivación:**
   - Si la salida del LLM no cumple el esquema Pydantic, se realiza un único intento de auto-reparación indicando el error al modelo.
   - Si la falla persiste, el backend responde **`200 OK`** con el atributo `requiere_revision_humana: true`. Esto es un éxito del flujo operativo de contingencia, no una caída del servidor.

---

## 6. Integración y Trabajo Colaborativo en Git (3 Integrantes)

Para cumplir con el criterio de evaluación de trabajo en equipo:
1. **Commits Distribuidos:** Cada tarea se registra con el autor correspondiente:
   - `Christian Morales` (`cgmorales12`): Endpoints de API, Gateway resiliente, integración de modelos.
   - `Luis Fernando Ribera` (`fernandolribera`): Matriz ITIL, base de datos SQLite, servicios RAG.
   - `Amalia Geoconda Iguasnia` (`Geocoiguasnia76`): Validación Pydantic, pruebas con mocks, reglas de seguridad LOPDP.
2. **Convención de Commits:** Se utilizará *Conventional Commits 1.0.0*:
   - `feat:` Nuevas funcionalidades del MVP.
   - `fix:` Corrección de defectos de código.
   - `docs:` Documentación técnica, manuales o diagramas.
   - `test:` Casos de prueba automatizados.
   - `refactor:` Mejoras de código sin cambiar comportamiento.

---

## 7. Comandos Operativos Estándar
- **Instalar dependencias:** `pip install -r requirements.txt`
- **Iniciar backend (FastAPI):** `uvicorn app.main:app --reload --port 8000`
- **Iniciar frontend (Streamlit / Web):** `streamlit run frontend/app.py`
- **Ejecutar pruebas unitarias con Mocks:** `pytest -v tests/`
- **Análisis estático de seguridad (SAST):** `bandit -r app/`
- **Ingesta de manuales para RAG:** `python scripts/ingestar_manuales.py`
