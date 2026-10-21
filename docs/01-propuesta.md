# Propuesta del Proyecto: ConectaTec

## 1. Identificación del Proyecto
* **Producto:** ConectaTec - Triaje Inteligente de Solicitudes para Proveedores Locales de Internet (ISP)
* **Caso Asignado:** Caso N.º 03 (Grupo 3) - Automatización de proceso con agente
* **Institución:** Universidad Regional Autónoma de Los Andes (UNIANDES)
* **Carrera:** Software - Seminario de Titulación Complexivo (Octubre 2026)
* **Integrantes:**
  * Christian Guillermo Morales González
  * Luis Fernando Ribera Alajo
  * Amalia Geoconda Iguasnia Escobar

---

## 2. Problema Real
Los clientes de proveedores locales de Internet (ISP) enfrentan demoras e incertidumbre ante cortes de servicio, caídas de enlace o fallas de configuración. Por otro lado, el personal técnico colapsa atendiendo reclamos repetitivos de primer nivel (luces del router, dudas de cobertura Wi-Fi, pruebas de velocidad), lo que retrasa la atención de incidentes críticos y genera costos innecesarios por despacho de cuadrillas técnicas para problemas que el usuario podría solucionar por sí mismo.

---

## 3. Usuarios del Sistema
1. **Cliente de Internet (Residencial / Corporativo):** Ingresa el reporte de falla mediante formulario web y recibe diagnósticos paso a paso con base en manuales oficiales.
2. **Operador de Mesa de Ayuda:** Monitorea las solicitudes entrantes, revisa clasificaciones automáticas y supervisa la cola de atención.
3. **Técnico de Cuadrilla de Campo:** Gestiona los incidentes escalados a través de un tablero Kanban priorizado por impacto y urgencia.

---

## 4. Alcance del Sistema

### 4.1 Alcance Positivo (Lo que el sistema hace)
* **Clasificación Automática:** Extrae mediante el modelo generativo y salida estructurada (JSON) la categoría (Fibra/Físico, Wi-Fi, Lógico/Configuración, Comercial), el impacto y la urgencia del incidente.
* **Cálculo Determinista de Prioridad:** Aplica una matriz de priorización tipo ITIL (configuración externa en JSON) para definir prioridades (Crítica, Alta, Media, Baja) mediante código Python determinista, sin delegar cálculos numéricos al modelo.
* **Diagnóstico Guiado y RAG:** Provee al cliente pasos de solución basados estrictamente en un corpus de 15 guías técnicas oficiales del ISP (luces ONT, router, pruebas cableadas, DNS), citando el procedimiento exacto.
* **Tablero de Tickets y Escalamiento:** Presenta un tablero de incidentes con estados (`Nuevo`, `En atención`, `Resuelto`, `Escalado`) y escala a cuadrilla técnica cuando se detecta daño físico (ej. luz LOS roja) o cuando los pasos guiados no resuelven la falla.

### 4.2 Alcance Negativo (Lo que el sistema NUNCA hará)
* **No diagnosticará fallas de enlace troncal sin validación:** No declarará cortes masivos de red sin confirmación de monitoreo.
* **No solicitará ni almacenará contraseñas:** El sistema nunca pedirá, registrará ni repetirá contraseñas de red Wi-Fi o credenciales de acceso al router (regla de seguridad y cumplimiento LOPDP).
* **No ejecutará acciones comerciales automáticas:** No suspenderá servicios ni emitirá cobros o notas de crédito sin autorización y confirmación humana.
* **No emitirá diagnósticos fuera de los manuales:** Ante problemas no documentados, el sistema se abstendrá explícitamente y derivará al operador.

---

## 5. Análisis de Riesgos y Mitigación
* **Riesgo 1: Alucinación en diagnósticos técnicos.**
  * *Mitigación:* Implementación de RAG con citas obligatorias al manual de origen y directiva estricta de abstención en el system prompt.
* **Riesgo 2: Fuga o almacenamiento de contraseñas de usuarios.**
  * *Mitigación:* Filtro y sanitización mediante expresiones regulares en la entrada de datos antes de enviar al modelo o registrar en base de datos.
* **Riesgo 3: Saturación o falla de la API del modelo (Error 429).**
  * *Mitigación:* Cliente `LLMClient` con reintentos mediante espera exponencial y conmutación automática al proveedor de respaldo (Groq).

---

## 6. Justificación del Modelo Generativo Elegido
Se selecciona **Google Gemini 1.5 Flash** (mediante Google AI Studio) como modelo principal por las siguientes razones técnicas:
1. **Capacidad de salida estructurada nativa:** Garantiza respuestas en formato JSON estricto mediante esquemas definidos con Pydantic.
2. **Baja latencia y eficiencia:** Ideal para clasificación en tiempo real de incidentes con tiempos de respuesta menores a 3 segundos.
3. **Capa gratuita sostenible:** Permite operar y validar el MVP sin requerir tarjeta de crédito ni incurrir en costos durante el seminario.
4. **Respaldo con Groq (Llama 3.3):** Asegura alta disponibilidad y tolerancia a fallos ante posibles cuotas agotadas.
