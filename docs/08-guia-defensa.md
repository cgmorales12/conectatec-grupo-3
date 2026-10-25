# Guía de Defensa de Grado y Preguntas del Tribunal
**Proyecto:** ConectaTec - Triaje Inteligente de Incidentes ISP (Caso N.º 03)  
**Seminario de Titulación:** Ingeniería de Software con IA Generativa — UNIANDES 2026  
**Integrantes Grupo 3:** Christian Morales · Fernando Ribera · Geoconda Iguasnia  
**Docente Evaluador:** Heyler Fabio Guaza  

---

## 1. Estructura de la Presentación Oral (10 Minutos)

1. **Introducción y Problema Real (2 min):**
   - El colapso de las mesas de ayuda de ISPs por consultas repetitivas de primer nivel (luces de router, dudas de Wi-Fi, cortes comerciales).
   - El costo innecesario de enviar cuadrillas de campo para problemas que el abonado puede resolver con un manual oficial.
2. **Arquitectura y Principio Rector (3 min):**
   - Explicar la regla: *«El modelo propone, el código dispone»*.
   - Demostrar la frontera de confianza: el frontend no conoce claves; el backend valida con Pydantic V2 (`extra="forbid"`).
   - Mostrar el cálculo determinista de la matriz ITIL en Python (`config/matriz_prioridad.json`).
3. **Demostración en Vivo (3 min):**
   - Ingresar un caso crítico de corte de fibra (Luz LOS roja): mostrar cómo se clasifica con Prioridad Alta, SLA de 2 horas y escala automáticamente a Cuadrilla citando `DOC-01`.
   - Mostrar el distintivo de transparencia de IA: `🟢 Gemini 1.5 Flash` y la conmutación hacia `🟠 Groq Cloud (Llama 3.3)`.
   - Mover el ticket entre columnas Kanban.
4. **Ciberseguridad y LOPDP (2 min):**
   - Demostrar que si un usuario escribe una contraseña en el reporte, el backend la sustituye por `[CONFIDENCIAL_REMOVIDO]` antes de procesarla.
   - Mostrar el limitador de tasa Token Bucket que responde con HTTP 429 y `Retry-After`.

---

## 2. Preguntas Probables del Tribunal y Respuestas Técnicas

### Pregunta 1: *«¿Por qué no le pidieron al LLM que calcule directamente la prioridad y el tiempo SLA?»*
* **Respuesta del Equipo:**  
  *«Porque los LLMs son modelos probabilísticos, no motores de cálculo determinista. En ingeniería de software crítica y gestión de servicios ITIL v4, los tiempos de respuesta contractuales (SLA) no pueden depender de la estocasticidad del modelo. El LLM extrae el Impacto y la Urgencia desde el lenguaje natural del cliente, pero la prioridad matemática la calcula una función pura en Python leyendo nuestra matriz JSON. Así garantizamos cero alucinaciones y 100% de reproducibilidad sin costo de tokens.»*

### Pregunta 2: *«¿Qué ocurre si durante la operación en vivo la API de Google Gemini se cae o da error 429 de cuota excedida?»*
* **Respuesta del Equipo:**  
  *«Diseñamos un Gateway de Resiliencia con conmutación automática por fallo (failover). Si Gemini devuelve HTTP 429, 503 o sufre un timeout, el backend captura la excepción e invoca instantáneamente a nuestro modelo de respaldo Llama 3.3 70B en Groq Cloud. Además, cumplimos con el principio de transparencia: el payload y la interfaz web muestran una alerta naranja indicando que la solicitud fue atendida por el respaldo.»*

### Pregunta 3: *«¿Cómo garantizan el cumplimiento de la Ley Orgánica de Protección de Datos Personales (LOPDP de Ecuador)?»*
* **Respuesta del Equipo:**  
  *«Aplicamos tres salvaguardas: Primero, anonimización por expresiones regulares (Art. 23 LOPDP), que detecta contraseñas accidentales en el reporte y las sustituye por `[CONFIDENCIAL_REMOVIDO]`. Segundo, uso de `response_model` en FastAPI para filtrar campos internos y evitar la fuga de datos sensibles (OWASP LLM02). Tercero, consultas SQL 100% parametrizadas con marcadores de posición (`?`) en SQLite para neutralizar inyecciones.»*

### Pregunta 4: *«¿Cómo justificaron el tamaño de los fragmentos y las citas en el sistema RAG?»*
* **Respuesta del Equipo:**  
  *«Curamos un corpus oficial de 15 manuales técnicos en `data/raw/` (DOC-01 a DOC-15). La fragmentación se realizó preservando la unidad de los procedimientos operativos paso a paso (entre 300 y 600 tokens), evitando cortes arbitrarios. Cada respuesta de autoatención incluye la cita obligatoria con el ID del documento y el paso exacto para que el usuario pueda verificar la información.»*

### Pregunta 5: *«¿Por qué eligieron FastAPI y no Django o Flask?»*
* **Respuesta del Equipo:**  
  *«Por tres razones técnicas (registradas en nuestro ADR-001): integración nativa con Pydantic V2 para validación estricta de contratos, documentación Swagger automática (`/docs`), y concurrencia segura mediante AnyIO, que delega las llamadas síncronas al LLM a un pool de 40 hilos de trabajo, evitando el bloqueo que afectaría a los usuarios concurrentes.»*

### Pregunta 6: *«¿Dónde y cómo están programadas las defensas contra inyección de prompts y alucinaciones (OWASP LLM01)?»*
* **Respuesta del Equipo:**  
  *«En 3 archivos complementarios: en `app/services/llm.py` mediante el aislamiento semántico `<solicitud>{texto}</solicitud>`, en `app/schemas.py` mediante contratos Pydantic V2 con `extra="forbid"`, y en `app/tools/priorizar.py` calculando el SLA con código determinista puro en Python. Toda la trazabilidad está detallada en nuestro documento [docs/10-perimetro-seguridad-y-defensas-llm.md](file:///c:/Users/Cris/Downloads/Programas%20APP/Seminario/APP%20IA/docs/10-perimetro-seguridad-y-defensas-llm.md).»*

### Pregunta 7: *«¿Cómo demuestran en vivo la diferencia entre un LLM vulnerable y su sistema con gobernanza determinista?»*
* **Respuesta del Equipo:**  
  *«Implementamos un interruptor en el Simulador de Resiliencia: 'Modo Vulnerable (Sin Defensas)'. Al apagar las defensas, el evaluador observa en vivo cómo el LLM cede al prompt adverso, alucinando 'Prioridad Infinita' y el manual falso 'DOC-99' en una tarjeta roja. Al encender nuevamente 'Defensas IA', el sistema contiene el mismo ataque de forma matemática en Prioridad Baja y Nivel 0 Fuera de Alcance.»*

