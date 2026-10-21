# Evidencias de Trabajo y Práctica: Semana 1 - ConectaTec

## 1. Identificación del Equipo y Proyecto
* **Proyecto:** ConectaTec - Triaje Inteligente de Solicitudes para ISP
* **Caso Asignado:** Caso N.º 03 (Grupo 3)
* **Integrantes:**
  * Christian Guillermo Morales González
  * Luis Fernando Ribera Alajo
  * Amalia Geoconda Iguasnia Escobar
* **Periodo de Evaluación:** Semana 1 - Arquitectura, Fundamentos de LLM y Requisitos

---

## 2. Decisiones Técnicas Clave de la Semana 1
1. **Modelo Generativo Principal:** Se seleccionó `gemini-1.5-flash` por su latencia reducida (< 3 s), soporte nativo para esquemas JSON estructurados y capa gratuita operativa.
2. **Estrategia de Tolerancia a Fallos:** Conmutación automática (*fallback*) hacia `Groq` con `llama-3.3-70b-versatile` ante errores de cuota o rate limit (`HTTP 429`).
3. **Determinismo en Priorización:** El cálculo de la prioridad (Crítica, Alta, Media, Baja) se implementa mediante código Python estricto aplicando la matriz ITIL versionada, delegando al LLM únicamente la extracción de impacto y urgencia.
4. **Cumplimiento de Privacidad (LOPDP):** Se implementó una directiva estricta de sanitización de credenciales y contraseñas de red antes del procesamiento en backend.

---

## 3. Práctica de Evaluación de Respuestas del Modelo (Clase 1)
Evaluación de 3 consultas técnicas de soporte realizadas contra `gemini-1.5-flash` para medir precisión técnica y alucinaciones:

| N.º | Consulta Enviada al LLM | Respuesta Obtenida del Modelo | Evaluación | Justificación Técnica |
| :---: | :--- | :--- | :---: | :--- |
| **01** | *"¿Por qué la luz LOS parpadea en rojo en mi ONT Huawei y qué puedo hacer?"* | Explicó que indica una pérdida total de potencia óptica en la fibra y sugirió verificar que el conector amarillo no esté doblado, recomendando llamar a soporte si no cambia. | **Correcta** | Coincide 100% con el manual oficial `DOC-01` de Huawei Carrier para atenuación menor a -27 dBm. |
| **02** | *"Tengo contratados 100 Mbps pero por Wi-Fi recibo 25 Mbps en la habitación contigua. ¿Mi proveedor me está estafando?"* | Afirmó categóricamente que el proveedor entrega menos ancho de banda del contratado sin consultar la banda de conexión ni obstáculos. | **Incorrecta** | Ignoró la atenuación física de la banda 2.4 GHz, interferencias y obstáculos estructurales (`DOC-05`). El procedimiento oficial exige test cableado directo por Ethernet (`DOC-06`). |
| **03** | *"¿El modelo HG8245H soporta autenticación GPON Clase B+ y C+ simultáneamente en la misma OLT?"* | Indicó que soporta ambas clases ópticas según la configuración del módulo SFP de la cabecera OLT. | **No verificable** | Depende de la óptica específica del fabricante, la distancia del enlace y la versión de firmware del proveedor local, requiriendo validación en laboratorio con telemetría real. |

---

## 4. Registro de Colaboración Git (Semana 1)
* **Christian Morales:** Definición de propuesta de proyecto (`docs/01-propuesta.md`), inventario de fuentes técnicas (`docs/04-fuentes.md`) y consolidado de evidencias (`docs/evidencias/semana-1/README.md`).
* **Amalia Iguasnia:** Especificación de historias de usuario con criterios Gherkin y RNF (`docs/02-requisitos.md`) y levantamiento de preguntas frecuentes (`docs/05-preguntas-frecuentes.md`).
* **Luis Fernando Ribera:** Arquitectura del sistema C4 Nivel 1 y 2, endpoints FastAPI y secuencia de triaje (`docs/03-arquitectura.md`), junto con la base técnica en `data/raw/README.md`.
