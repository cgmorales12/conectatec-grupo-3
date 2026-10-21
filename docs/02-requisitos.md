# Ingeniería de Requisitos: ConectaTec

## 1. Introducción
El presente documento describe los requisitos funcionales y no funcionales de *ConectaTec* (Caso N.º 03 - Grupo 3), sistema de triaje automático de incidentes de soporte técnico para un Proveedor Local de Internet (ISP).
Las historias de usuario siguen el estándar *INVEST* y sus criterios de aceptación están redactados bajo el formato *Gherkin* (Dado... Cuando... Entonces...).
# 2. Historias de Usuario (Mínimo 8 Requisitos Funcionales)

### HU-01: Reporte y triaje de falla por corte físico de fibra (Luz LOS roja)
* *Como* cliente de Internet residencial,
* *quiero* reportar que mi router ONT presenta una luz roja en el indicador LOS,
* *para* conocer si mi acometida de fibra óptica sufrió una rotura y recibir asistencia inmediata.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Detección de daño físico de fibra óptica.
    * *Dado* que el cliente ingresa una descripción que incluye "luz roja", "LOS en rojo" o "cable cortado",
    * *cuando* el sistema analiza la solicitud,
    * *entonces* clasifica la solicitud en la categoría "Fibra/Físico", asigna urgencia "Alta" y genera una alerta de daño físico.
  * *Escenario 2:* Escalamiento preventivo.
    * *Dado* que el incidente fue catalogado como daño físico de fibra,
    * *cuando* se crea el ticket en el sistema,
    * *entonces* se escala automáticamente para inspección de cuadrilla técnica de campo sin exigir pruebas de software al usuario.

---

### HU-02: Diagnóstico guiado de lentitud de navegación
* *Como* usuario del servicio de Internet,
* *quiero* recibir instrucciones paso a paso para verificar mi velocidad de conexión,
* *para* descartar saturación local o interferencias antes de reportar una avería general.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Solicitud de prueba cableada oficial.
    * *Dado* que el cliente reporta "Internet lento" o "baja velocidad",
    * *cuando* el sistema procesa el requerimiento,
    * *entonces* responde con el procedimiento oficial de test de velocidad citando el manual DOC-06 e instruye realizar la medición conectando un cable Ethernet directo al router.

---

### HU-03: Optimización y cambio de canal de red Wi-Fi
* *Como* cliente con problemas de cobertura inalámbrica en habitaciones alejadas,
* *quiero* consultar cómo mejorar la señal Wi-Fi de mi hogar,
* *para* optimizar la ubicación de mi router y evitar zonas muertas.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Guía de ubicación y cambio de frecuencia.
    * *Dado* que el usuario consulta que "la señal no llega a mi habitación" o "baja señal Wi-Fi",
    * *cuando* el sistema consulta la base de conocimiento,
    * *entonces* devuelve los pasos de la guía DOC-05 sobre ubicación libre de obstáculos e instruye conectar dispositivos de alto consumo a la banda de 5 GHz.

---

### HU-04: Consulta de estado comercial y suspensión por pago pendiente
* *Como* suscriptor del ISP,
* *quiero* verificar si la pérdida de señal se debe a un corte administrativo por facturación,
* *para* evitar esperas técnicas innecesarias si mantengo valores pendientes.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Orientación ante corte por falta de pago.
    * *Dado* que el cliente consulta por falta de servicio y tiene corte comercial registrado,
    * *cuando* el sistema evalúa los datos del cliente,
    * *entonces* clasifica la solicitud como "Comercial/Facturación", informa el estado de cuenta y proporciona los canales oficiales de pago sin generar ticket de cuadrilla técnica.

---

### HU-05: Solicitud de cambio de credenciales de red Wi-Fi
* *Como* usuario que desea renovar la seguridad de su red local,
* *quiero* solicitar la actualización del nombre (SSID) y clave de mi red inalámbrica,
* *para* gestionar los dispositivos autorizados en mi domicilio.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Entrega del procedimiento de autogestión.
    * *Dado* que el usuario solicita "cambiar contraseña de mi Wi-Fi",
    * *cuando* el sistema analiza la consulta,
    * *entonces* cita el manual DOC-04 y explica los pasos para acceder a la puerta de enlace predeterminada (192.168.1.1) de forma segura.

---

### HU-06: Escalamiento automático de incidentes no resueltos
* *Como* operador de mesa de ayuda,
* *quiero* que los incidentes que no pudieron resolverse mediante las guías de primer nivel se deriven automáticamente,
* *para* despachar una cuadrilla técnica con el historial completo de pruebas realizadas.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Marcado de falla persistente.
    * *Dado* que el cliente indica que siguió los pasos guiados pero el problema persiste,
    * *cuando* se actualiza el ticket,
    * *entonces* el estado cambia de "En atención" a "Escalado", adjuntando el motivo y asignándose a la cola del equipo técnico de campo.

---

### HU-07: Tablero de control de tickets priorizados para soporte
* *Como* técnico de soporte de guardia,
* *quiero* visualizar un tablero con los tickets organizados por estados y nivel de prioridad,
* *para* atender con urgencia los incidentes críticos y masivos antes que las dudas cotidianas.
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Ordenamiento por matriz de prioridad ITIL.
    * *Dado* que existen tickets registrados con diferentes prioridades (Crítica, Alta, Media, Baja),
    * *cuando* el técnico consulta el tablero web,
    * *entonces* los tickets se presentan agrupados por columnas de estado (Nuevo, En atención, Resuelto, Escalado) y ordenados descendentemente por su prioridad calculada.

---

### HU-08: Protección y sanitización de contraseñas compartidas
* *Como* oficial de seguridad de la información y privacidad,
* *quiero* que el sistema impida el almacenamiento de contraseñas de red o de router ingresadas por los usuarios,
* *para* proteger las credenciales privadas y cumplir la Ley Orgánica de Protección de Datos Personales (LOPDP).
* *Criterios de Aceptación (Gherkin):*
  * *Escenario 1:* Detección y censura de contraseñas.
    * *Dado* que el cliente escribe un mensaje que contiene frases como "mi contraseña es...", "mi clave es 12345" o credenciales explícitas,
    * *cuando* el backend valida la entrada antes de procesarla con el modelo,
    * *entonces* sanitiza el texto reemplazando la clave por [DATO_CONFIDENCIAL_REMOVIDO], advierte al usuario no compartir contraseñas y garantiza que dicho dato no se guarde en la base de datos ni en los registros (logs).

---

## 3. Requisitos No Funcionales (RNF Medibles)

| ID | Parámetro | Requisito Medible | Criterio de Verificación |
| :--- | :--- | :--- | :--- |
| *RNF-01* | *Tiempo de respuesta (Latencia)* | El endpoint de clasificación y triaje debe responder en un tiempo $\le 3.0$ segundos en el percentil 95 (P95). | Medido en logs del servidor backend por solicitud. |
| *RNF-02* | *Salida Estructurada* | El 100% de las respuestas de clasificación deben entregarse en formato JSON válido bajo el esquema de Pydantic. | Validación de tipos y campos obligatorios antes del retorno HTTP. |
| *RNF-03* | *Tolerancia a Fallos (Disponibilidad)* | Ante fallas consecutivas o límite de tasa (código HTTP 429) del proveedor principal, el sistema debe conmutar al proveedor de respaldo en menos de 2 segundos. | Prueba de caída simulada con proveedor secundario (Groq). |
| *RNF-04* | *Privacidad y Seguridad (LOPDP)* | Cero contraseñas o datos personales sensibles deben persistirse en bases de datos relacionales o archivos de logs. | Verificado mediante pruebas automatizadas de seguridad con expresiones regulares. |
| *RNF-05* | *Determinismo de Prioridad* | El cálculo de la prioridad debe realizarse estrictamente en código mediante la matriz ITIL versionada, con tolerancia cero a discrepancias numéricas. | Pruebas unitarias con pytest sobre matriz impacto-urgencia. |
