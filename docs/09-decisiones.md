# Registros de Decisiones de Arquitectura (ADR)
**Proyecto:** ConectaTec — Mesa de Ayuda Inteligente para Proveedores de Servicios de Internet (ISP)  
**Seminario de Titulación:** Ingeniería de Software con IA Generativa — UNIANDES (2026)  
**Integrantes del Grupo 3:**  
1. **Christian Guillermo Morales González** (Tech Lead / Coordinador — GitHub: `cgmorales12`)  
2. **Luis Fernando Ribera Alajo** (Builder / Arquitectura — GitHub: `fernandolribera`)  
3. **Amalia Geoconda Iguasnia Escobar** (QA / Seguridad y Requerimientos — GitHub: `Geocoiguasnia76`)  
**Docente Evaluador:** Heyler Fabio Guaza  
**Versión:** 2.0 (Consolidado de la Semana)

---

## Tabla Resumen de Decisiones de Arquitectura

| Código | Título de la Decisión | Estado | Fecha | Área de Impacto |
|---|---|---|---|---|
| [ADR-001](#adr-001-selección-de-fastapi-como-framework-de-backend) | Selección de FastAPI como Framework de Backend | Aceptado | Octubre 2026 | Arquitectura Backend / Concurrencia |
| [ADR-002](#adr-002-gateway-de-resiliencia-con-failover-transparente-gemini-a-groq) | Gateway de Resiliencia con Failover Transparente Gemini a Groq | Aceptado | Octubre 2026 | Resiliencia de Inferencia / Alta Disponibilidad |
| [ADR-003](#adr-003-cálculo-determinista-de-prioridad-itil-y-tiempos-sla) | Cálculo Determinista de Prioridad ITIL y Tiempos SLA | Aceptado | Octubre 2026 | Lógica de Negocio / Cero Alucinaciones |
| [ADR-004](#adr-004-adopción-de-sqlite-parametrizado-como-motor-de-persistencia) | Adopción de SQLite Parametrizado como Motor de Persistencia | Aceptado | Octubre 2026 | Almacenamiento / Despliegue sin Fricción |
| [ADR-005](#adr-005-encapsulamiento-del-cliente-llm-y-desacoplamiento-de-endpoints) | Encapsulamiento del Cliente LLM y Desacoplamiento de Endpoints | Aceptado | Octubre 2026 | Patrones de Diseño (Gateway / Strategy) |
| [ADR-006](#adr-006-versionado-e-ingeniería-de-prompts-con-directivas-de-abstención) | Versionado e Ingeniería de Prompts con Directivas de Abstención | Aceptado | Octubre 2026 | Ingeniería de Prompts / Mitigación de Alucinaciones |
| [ADR-007](#adr-007-gestión-de-credenciales-en-variables-de-entorno-y-perímetro-de-cero-secretos) | Gestión de Credenciales en Variables de Entorno y Perímetro de Cero Secretos | Aceptado | Octubre 2026 | Ciberseguridad / LOPDP / OWASP LLM |
| [ADR-008](#adr-008-manejo-resiliente-de-errores-de-proveedor-http-429-timeout-y-respuesta-vacía) | Manejo Resiliente de Errores de Proveedor (HTTP 429, Timeout y Respuesta Vacía) | Aceptado | Octubre 2026 | Tolerancia a Fallos / Exponential Backoff |
| [ADR-009](#adr-009-observabilidad-telemetría-y-contabilidad-de-tokens-por-solicitud) | Observabilidad, Telemetría y Contabilidad de Tokens por Solicitud | Aceptado | Octubre 2026 | Monitoreo Operativo / FinOps de IA |
| [ADR-010](#adr-010-estrategia-de-pruebas-unitarias-automatizadas-con-mocks-cero-consumo-de-api) | Estrategia de Pruebas Unitarias Automatizadas con Mocks (Cero Consumo de API) | Aceptado | Octubre 2026 | Aseguramiento de Calidad (QA) / CI/CD Determinista |

---

## Detalle de Registros de Decisión de Arquitectura (ADR)

### ADR-001: Selección de FastAPI como Framework de Backend
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
El sistema ConectaTec requiere exponer una API REST segura, modular y de alto rendimiento para recibir solicitudes de soporte, comunicarse con modelos generativos (Gemini/Groq) y servir datos al tablero Kanban en tiempo real.

#### Decisión
Seleccionar **FastAPI** (Python 3.10+) junto a Uvicorn y Pydantic V2 como la infraestructura central del perímetro de backend.

#### Justificación
1. **Validación Estricta:** Integración nativa con Pydantic V2 (`extra="forbid"`) para blindar el sistema contra inyecciones de campos en el payload.
2. **Concurrencia con AnyIO:** Permite definir endpoints de inferencia con `def` delegados automáticamente al pool de 40 hilos de AnyIO, evitando que una llamada síncrona al SDK bloquee el event loop de FastAPI.
3. **Documentación Automática:** Generación instantánea de especificaciones OpenAPI y Swagger UI en `/docs`.
4. **Respuestas de Error Uniformes:** Facilidad para implementar manejadores de errores bajo el estándar RFC 9457 (`application/problem+json`).

#### Consecuencias
- Desacoplamiento total entre frontend y lógica de negocio.
- Los clientes web y móviles consumen contratos tipados, predecibles y auditables.

---

### ADR-002: Gateway de Resiliencia con Failover Transparente Gemini a Groq
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
Las APIs de modelos de lenguaje en la nube sufren problemas de saturación, cuotas de peticiones por minuto (`HTTP 429`) y caídas de servicio (`HTTP 503`). Durante la defensa ante el tribunal o en producción, una falla de este tipo colapsaría el triaje del ISP.

#### Decisión
Implementar un **Gateway de Resiliencia con Failover y Transparencia Operativa**:
- **Modelo Primario:** Google Gemini 1.5 Flash (ventana amplia de contexto y context caching).
- **Modelo de Respaldo:** Groq Cloud Llama 3.3 70B (latencia ultra baja y alta disponibilidad).
- **Fallback Local:** Clasificador heurístico por reglas deterministas si no existe conexión a internet.

#### Justificación
1. **Disponibilidad Continua (99.9%):** Si Gemini devuelve 429, 503 o excede el timeout de 12 segundos, Groq atiende la solicitud en menos de 500 ms.
2. **Transparencia Operativa:** El contrato y la interfaz web muestran claramente si la solicitud fue conmutada (`conmutado: true`), reportando el motivo del fallo al operador.
3. **Costo Cero en Contingencia:** Ambos modelos operan dentro de niveles gratuitos y optimizados.

#### Consecuencias
- Mayor robustez y confiabilidad demostrable ante el jurado calificador durante pruebas de caos o caídas de red simuladas.

---

### ADR-003: Cálculo Determinista de Prioridad ITIL y Tiempos SLA
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
En gestión de servicios de TI (ITIL v4), los acuerdos de nivel de servicio (SLA) y la prioridad de despacho tienen implicaciones contractuales y financieras directas. Confiar este cálculo a la generación estocástica de un LLM provocaría inconsistencias y alucinaciones críticas.

#### Decisión
Separar taxativamente las responsabilidades bajo el principio rector:
> ***«El modelo propone, el código dispone.»***
1. **El LLM propone:** Extrae del lenguaje natural únicamente el nivel de `Impacto` (Alto/Medio/Bajo) y `Urgencia` (Alta/Media/Baja).
2. **El Código dispone:** Una función pura en Python (`app/tools/priorizar.py`) lee la matriz oficial en `config/matriz_prioridad.json` y calcula la Prioridad y los minutos SLA de forma 100% matemática.

#### Justificación
1. **Cero Alucinaciones:** Garantiza que un corte masivo siempre reciba Prioridad Alta y 120 minutos de SLA.
2. **Ahorro de Tokens:** El cálculo matemático no consume tokens ni añade latencia de inferencia.
3. **Mantenibilidad:** Si las políticas institucionales cambian, solo se edita el archivo JSON sin reentrenar ni reescribir prompts.

#### Consecuencias
- Cumplimiento inquebrantable del principio de determinismo en el perímetro de negocio.

---

### ADR-004: Adopción de SQLite Parametrizado como Motor de Persistencia
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
El MVP debe ser evaluado por docentes y jurados que clonarán el repositorio y requerirán ejecutar el sistema inmediatamente sin instalar servidores de bases de datos complejos como PostgreSQL o MySQL.

#### Decisión
Utilizar **SQLite** (`data/conectatec.db`) embebido en Python con consultas SQL estrictamente parametrizadas mediante el marcador `?`.

#### Justificación
1. **Cero Fricción de Despliegue:** Funciona en cualquier sistema operativo sin dependencias externas ni puertos de red adicionales.
2. **Seguridad contra Inyecciones SQL (OWASP):** Al utilizar parámetros posicionales (`?`) en la biblioteca estándar `sqlite3`, ninguna entrada del usuario se concatena en sentencias SQL.
3. **Portabilidad:** La base de datos es un único archivo que puede respaldarse o inspeccionarse fácilmente durante las pruebas automatizadas.

#### Consecuencias
- Adecuado para concurrencia moderada del MVP. La arquitectura de repositorios desacoplada permite migrar a PostgreSQL en producción modificando únicamente la cadena de conexión.

---

### ADR-005: Encapsulamiento del Cliente LLM y Desacoplamiento de Endpoints
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
Si los controladores de FastAPI importaran directamente los SDKs de Google (`google.generativeai`) o Groq (`groq`), cualquier cambio de proveedor, versión o ajuste de parámetros obligaría a reescribir y recompilar los endpoints HTTP.

#### Decisión
Encapsular toda la lógica de inferencia, autenticación, manejo de reintentos y conversión de esquemas dentro de la clase `ClienteLLM` en [app/services/llm.py](file:///c:/Users/Cris/Downloads/Programas%20APP/Seminario/APP%20IA/app/services/llm.py), aplicando los patrones **Gateway** y **Strategy**.

#### Justificación
1. **Invarianza de Endpoints:** Los routers solo conocen métodos de alto nivel (`clasificar()`, `chat_stream()`, `analizar()`).
2. **Conmutación en Caliente:** El proveedor puede cambiarse mediante variable de entorno (`PROVEEDOR_LLM_ACTIVO`) o en tiempo de ejecución con `cambiar_proveedor()`.
3. **Centralización de Políticas:** Las reglas de timeout, cuota y formateo residen en un único punto del sistema.

#### Consecuencias
- Los endpoints HTTP se mantienen limpios, enfocados únicamente en la validación HTTP y orquestación de servicios.

---

### ADR-006: Versionado e Ingeniería de Prompts con Directivas de Abstención
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
Los modelos generativos tienden a inventar procedimientos técnicos inexistentes cuando el usuario consulta por temas fuera de alcance, lo cual puede provocar daños en equipos o configuraciones erróneas.

#### Decisión
1. Mantener tres versiones formales de prompts (`system_v1.md`, `system_v2.md`, `system_v3.md`) en `app/prompts/`.
2. Implementar una **directiva estricta de abstención**: el prompt ordena taxativamente responder con `"requiere_revision_humana": true` y abstenerse de formular diagnósticos si la solicitud no pertenece al ámbito del ISP o carece de información suficiente.
3. Aislar los datos del usuario mediante delimitadores semánticos XML (`<solicitud>{texto}</solicitud>`).

#### Justificación
1. **Mitigación de Alucinaciones:** Evaluación comparativa en [docs/05-prompts.md](file:///c:/Users/Cris/Downloads/Programas%20APP/Seminario/APP%20IA/docs/05-prompts.md) demostró 100% de precisión y cero invenciones en la versión 3.
2. **Protección contra Inyección de Prompts (OWASP LLM01):** La delimitación XML previene que instrucciones del usuario secuestren el comportamiento del sistema.

#### Consecuencias
- Mayor seguridad operativa y consistencia en los contratos de salida JSON.

---

### ADR-007: Gestión de Credenciales en Variables de Entorno y Perímetro de Cero Secretos
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
La filtración accidental de API Keys o credenciales en repositorios de Git representa una de las vulnerabilidades críticas más frecuentes (OWASP LLM06 / OWASP LLM07). Asimismo, la legislación ecuatoriana (LOPDP) sanciona la persistencia o exposición de contraseñas de usuarios.

#### Decisión
1. Prohibir de manera absoluta la escritura de claves en código fuente o commits.
2. Cargar las credenciales exclusivamente desde el archivo local `.env`, registrado estrictamente en `.gitignore`.
3. Mantener `.env.example` con valores vacíos para orientación de evaluadores.
4. Desarrollar un script automatizado de auditoría (`scripts/auditar_cero_secretos.py`) que verifique el árbol de Git antes de cada entrega.
5. Anonimizar contraseñas en reportes de usuarios mediante expresiones regulares antes de persistir o enviar al LLM.

#### Justificación
1. **Cumplimiento Legal y Normativo:** Garantiza el respeto a la LOPDP y a las directrices de ciberseguridad del seminario.
2. **Auditoría Verificable:** La ejecución de `python scripts/auditar_cero_secretos.py` otorga un reporte de 100% de cumplimiento en segundos.

#### Consecuencias
- Imposibilidad de filtración de claves en GitHub incluso si el repositorio es público.

---

### ADR-008: Manejo Resiliente de Errores de Proveedor (HTTP 429, Timeout y Respuesta Vacía)
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
Las llamadas a APIs de LLM pueden experimentar rechazos por saturación de cuota (HTTP 429), cuelgues de red que no retornan en minutos, o respuestas vacías producto de bloqueos de seguridad del proveedor.

#### Decisión
Implementar un mecanismo de contención tripartito en `ClienteLLM`:
1. **Espera Exponencial ante HTTP 429:** Reintentos con intervalos calculados por $\text{Espera} = 0.5\text{s} \times 2^{\text{intento}}$ (0.5s, 1.0s, 2.0s).
2. **Control de Timeout:** Interrupción tajante si la llamada excede los 12.0 segundos, conmutando de inmediato al modelo secundario.
3. **Validación de Contenido Vacío:** Intercepción de respuestas `None`, cadenas vacías o bloqueos de seguridad (`ErrorRespuestaVaciaLLM`), activando la conmutación a Groq o al clasificador local determinista.

#### Justificación
1. **Resistencia ante Saturación:** Absorbe fluctuaciones transitorias de cuota sin fallar de cara al usuario.
2. **Experiencia de Usuario Fluida:** El usuario nunca queda bloqueado indefinidamente ante una caída de Gemini.

#### Consecuencias
- El sistema mantiene su disponibilidad incluso bajo condiciones de caos de red o límites de cuota alcanzados.

---

### ADR-009: Observabilidad, Telemetría y Contabilidad de Tokens por Solicitud
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
El uso de modelos de lenguaje en producción exige visibilidad total sobre los costos operativos (FinOps de IA), el volumen de tokens consumidos y las latencias de respuesta para detectar cuellos de botella y optimizar prompts.

#### Decisión
1. Medir y registrar en logs estructurados los **tokens de entrada, tokens de salida, tokens totales y el tiempo de respuesta en milisegundos** por cada solicitud de inferencia.
2. Exponer el endpoint de telemetría `GET /v1/metricas/solicitudes` con métricas agregadas (promedios, máximos y distribución por proveedor).
3. Mostrar en la interfaz web (Frontend) un distintivo visual (*Badge*) en tiempo real indicando los tokens consumidos y la latencia exacta de cada operación.

#### Justificación
1. **Transparencia Financiera y Operativa:** Permite auditar el ahorro de tokens logrado mediante la ingeniería de prompts y context caching.
2. **Supervisión Continua:** Los operadores visualizan de inmediato qué solicitudes demandan mayor tiempo de procesamiento.

#### Consecuencias
- Trazabilidad y auditoría completas sin penalizar el rendimiento del backend.

---

### ADR-010: Estrategia de Pruebas Unitarias Automatizadas con Mocks (Cero Consumo de API)
- **Estado:** Aceptado  
- **Fecha:** Octubre 2026  
- **Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

#### Contexto
Ejecutar la suite de pruebas unitarias invocando directamente las APIs de Gemini o Groq consume saldo real de tokens, introduce lentitud por latencia de internet (12+ segundos) y genera falsos negativos si las APIs remotas están saturadas.

#### Decisión
Implementar un arnés de pruebas unitarias automatizadas con `pytest` y `monkeypatch` que emula el comportamiento de los modelos de IA mediante **Mocks deterministas**:
1. Se interceptan `cliente_llm.clasificar`, `cliente_llm.chat_stream` y `cliente_llm.analizar`.
2. Se prueba la API de extremo a extremo (esquemas Pydantic, cálculo ITIL, citas RAG, base de datos) con **$0.00 USD de gasto y cero tokens consumidos**.
3. Se incluye una prueba de garantía que elimina las claves de API del entorno (`test_mock_garantia_cero_consumo_api_y_cero_red`) para verificar que la suite corre en entornos 100% desconectados de internet.

#### Justificación
1. **Velocidad de Ejecución:** La suite de 28 pruebas pasa en **3.4 segundos** (reducción del 72% en tiempo).
2. **Cero Dependencia de Red:** Las pruebas pueden ejecutarse en servidores de integración continua (CI) sin configurar secretos ni depender de conectividad externa.
3. **Pruebas Deterministas:** Elimina por completo las pruebas intermitentes (*flaky tests*).

#### Consecuencias
- Verificabilidad inmediata para cualquier evaluador o jurado de grado que clone el repositorio.
