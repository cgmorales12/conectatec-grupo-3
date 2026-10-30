# ADR-012: Flujo Automatizado de Triaje con IA y Vía de Revisión Humana

**Proyecto:** ConectaTec / TecnoAula — Triaje y Resolución Inteligente de Incidencias Técnicas  
**Caso Asignado:** Caso N.º 03 (Mesa de Ayuda para Instituciones Educativas e ISP)  
**Grupo de Desarrollo N.º 03:**  
* **Christian Guillermo Morales González** (Tech Lead / Coordinador — GitHub: `cgmorales12`)  
* **Luis Fernando Ribera Alajo** (Builder / Arquitectura — GitHub: `fernandolribera`)  
* **Amalia Geoconda Iguasnia Escobar** (QA / Seguridad y Requerimientos — GitHub: `Geocoiguasnia76`)  
**Docente Evaluador:** Heyler Fabio Guaza  
**Fecha:** 29 de octubre de 2026 (Semana 3 · Clase 4)  
**Estado:** Aprobado / Implementado  

---

## 1. Contexto y Problema

En la mesa de ayuda educativa e ISP, el equipo técnico recibe entre 40 y 120 reportes diarios de incidentes (averías de proyectores en aulas híbridas, fallas de Wi-Fi de campus, cortes de fibra óptica, contraseñas bloqueadas y cuentas de correo institucional).  

Históricamente, un técnico abría manualmente cada ticket, interpretaba la descripción del usuario, buscaba en manuales PDF el procedimiento correspondiente y calculaba la prioridad ITIL. Este proceso manual introducía:
1. Demoras operativas de 15 a 45 minutos por solicitud antes de asignar el caso.
2. Inconsistencias en la asignación de prioridades y SLAs.
3. Riesgo de errores silenciosos por fatiga del operador.

---

## 2. Decisión de Arquitectura: Flujo Fijo Híbrido (No Agente Autónomo)

Se adopta una arquitectura de **cinta de procesamiento (flujo fijo híbrido)** en lugar de un agente autónomo libre:
* **Disparador:** Webhook de formulario web / cola de eventos (`POST /webhook/incidente`).
* **Entrada típica:** Descripción del incidente en lenguaje natural enviada por docentes o usuarios.
* **Acción final:** Registrar el ticket en la base de datos transaccional con su prioridad y SLA calculados, publicándolo en el tablero Kanban y notificando al técnico asignado.
* **Justificación de Flujo Fijo:**
  * Los pasos de triaje son siempre los mismos e invariables.
  * Cada estación debe ser auditable de forma determinista ante el evaluador y directivos.
  * El volumen es repetitivo y requiere latencia predecible (< 1 segundo).
  * Se evitan los bucles infinitos y costos no acotados propios de los agentes autónomos.

---

## 3. Matriz de Estaciones y Propietarios Técnicos

Principio rector: ***«La IA decide lo difuso · El código decide lo exacto · Una persona decide lo riesgoso.»***

| # | Estación | Qué Hace | Decide | Qué Sale |
| :-: | :--- | :--- | :---: | :--- |
| **1** | **Disparador** | Llega el reporte de incidente por formulario web o correo | **Sistema** | Evento encolado con respuesta `202 Accepted` |
| **2** | **Clasificar** | Determina la categoría del incidente y calcula índice de certeza | **IA** | JSON estructurado con `tipo` y `confianza` (0.00 a 1.00) |
| **3** | **Umbral** | Si `confianza < 0.85`, desvía a revisión humana asistida | **Código** | Flujo continuo hacia estación 4 o cola de revisión humana |
| **4** | **Extraer** | Extrae servicio afectado, impacto y urgencia con Pydantic V2 | **IA** | Objeto validado con `extra="forbid"` |
| **5** | **Reglas** | Calcula prioridad y SLA leyendo `config/matriz_prioridad.json` | **Código** | Prioridad (`Alta`, `Media`, `Baja`) y SLA exacto determinista |
| **6** | **Revisión** | El técnico de guardia confirma casos críticos P1 o confianza baja | **Persona** | Aprobación o ajuste con el trabajo prellenado |
| **7** | **Actuar** | Registra el ticket en SQLite/Kanban de forma idempotente | **Sistema** | Registro con hash único y trazabilidad inmutable |

---

## 4. Gestión del Umbral de Confianza (`0.85`)

* **Ubicación del Umbral:** Declarado en [`config/parametros.yaml`](../config/parametros.yaml) como `umbral_confianza: 0.85`.
* **Calibración con el Conjunto Dorado:**
  * Con umbral $0.50$: Se producían errores silenciosos en documentos con múltiples temas o escaneos borrosos.
  * Con umbral $0.85$: **0 errores silenciosos** (tolerancia cero). El $25\%$ de los casos con ambigüedad pasa a revisión humana con los campos ya legibles prellenados.

---

## 5. Reglas Inviolables de Ciberseguridad

1. **Cero Confianza en Entradas:** Todo texto que ingresa por el disparador se trata como no confiable (*untrusted input*).
2. **Contratos Cerrados:** La IA solo produce campos declarados en esquemas Pydantic V2 (`extra="forbid"`); nunca ejecuta sentencias SQL ni llamadas directas al sistema operativo.
3. **Control Humano Obligatorio (*Human-in-the-loop*):** Ninguna estación automática despacha camionetas de cuadrilla técnica presencial ni altera matrices de servicio sin la confirmación de una persona.
4. **Idempotencia:** Toda acción de escritura utiliza claves de idempotencia (`doc.id` o hash SHA-256) para evitar duplicados ante reintentos de red.

