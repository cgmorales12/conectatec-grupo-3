# Levantamiento Real de Información: Preguntas Frecuentes de Soporte Técnico (ISP)

## 1. Contexto del Levantamiento
* *Proyecto:* ConectaTec - Triaje Inteligente de Solicitudes ISP
* *Caso de Estudio:* Caso N.º 03 (Grupo 3) - Automatización de proceso con agente
* *Objetivo:* Recopilación de incidentes, consultas y dudas reales formuladas por usuarios residenciales y corporativos ante la mesa de ayuda de un Proveedor Local de Internet (ISP) para parametrizar el sistema de triaje, la categorización de urgencia/impacto y las pruebas de evaluación de la IA.

---

## 2. Consolidado de Consultas Reales de Soporte (15 Casos de Estudio)

| N.º | Pregunta / Incidencia Real del Cliente | Categoría Identificada | Impacto | Urgencia | Procedimiento o Ficha de Soporte Asociada |
| :---: | :--- | :--- | :---: | :---: | :--- |
| *01* | "En mi router parpadea una luz roja que dice LOS y no carga ninguna página web en ningún equipo." | Fibra / Físico | Alto | Alta | DOC-01 / DOC-09 (Detección de rotura física de fibra óptica) |
| *02* | "Tengo contratados 100 megas pero al hacer test en mi celular solo me llegan 15 megas en el dormitorio." | Wi-Fi / Cobertura | Medio | Media | DOC-05 / DOC-10 (Atenuación por distancia y paredes en 2.4 GHz) |
| *03* | "En mi computadora conectada con cable de red el Internet funciona rápido, pero los teléfonos por Wi-Fi se desconectan constantemente." | Wi-Fi / Red Local | Medio | Media | DOC-05 / DOC-12 (Interferencia de canal y saturación inalámbrica) |
| *04* | "¿Cómo puedo cambiar la contraseña de mi red Wi-Fi para que no se conecten los vecinos?" | Configuración / Solicitud | Bajo | Baja | DOC-04 (Guía de cambio de credenciales SSID en 192.168.1.1) |
| *05* | "Ayer hubo una tormenta eléctrica y hoy todas las luces del módem están apagadas, aunque esté conectado al tomacorriente." | Físico / Hardware | Alto | Alta | DOC-03 (Falla de fuente de poder o daño eléctrico de ONT) |
| *06* | "No me abre WhatsApp ni Google, pero la luz PON está verde y fija. Me sale error de DNS en el navegador." | Lógico / Configuración | Medio | Media | DOC-07 (Depuración de resolución DNS y vaciado de caché) |
| *07* | "Se me cayó un mueble encima del cable amarillo delgado que viene de la calle y se dobló feo, desde ahí no tengo servicio." | Fibra / Físico | Alto | Alta | DOC-09 (Atenuación extrema o quiebre de jumper de fibra) |
| *08* | "El servicio se corta cada 10 minutos y vuelve a conectar solo; mientras juego en línea me bota de las partidas." | Red / Sesión | Medio | Alta | DOC-13 (Intermitencia por renegociación PPPoE o SNR inestable) |
| *09* | "Me salió una pantalla diciendo que mi servicio está suspendido por falta de pago, pero ya transferí esta mañana." | Comercial / Facturación | Alto | Media | DOC-14 (Verificación de comprobante de pago y reactivación) |
| *10* | "Compré un repetidor Wi-Fi en la tienda pero no sé cómo enlazarlo al router principal que me instaló la empresa." | Configuración / Wi-Fi | Bajo | Baja | DOC-11 (Configuración en modo puente / Access Point) |
| *11* | "El cable de red que conecta la computadora al router tiene rota la patita de plástico y se sale a cada rato." | Físico / Cableado | Bajo | Baja | DOC-08 (Reemplazo de conector RJ-45 en cable UTP) |
| *12* | "Cuando enciendo el microondas en la cocina, la videollamada de mi laptop en la sala se congela por completo." | Wi-Fi / Interferencia | Bajo | Media | DOC-10 (Interferencia electromagnética en la banda de 2.4 GHz) |
| *13* | "¿Cuál es la diferencia entre la red Wi-Fi normal y la que termina en '_5G'? ¿A cuál me conviene conectar mi Smart TV?" | Consulta General | Bajo | Baja | DOC-05 (Comparativa de rendimiento entre 2.4 GHz y 5 GHz) |
| *14* | "En mi edificio somos varios vecinos con la misma empresa y a ninguno le funciona el Internet desde las 3 de la tarde." | Masivo / Red Troncal | Alto | Alta | Protocolo de escalamiento a Centro de Operaciones de Red (NOC) |
| *15* | "Quiero reiniciar mi router de fábrica metiendo un clip en el agujerito de Reset porque olvidé la clave." | Advertencia Técnica | Medio | Alta | DOC-03 / DOC-04 (Alerta: desconfiguración de VLAN y PPPoE) |

---

## 3. Conclusiones para el Modelo de Triaje
1. *Priorización Crítica:* Las incidencias con luz LOS roja o quiebre físico de cable (preguntas 1 y 7) representan averías no resolubles por software y se deben escalar directamente a cuadrilla de campo[cite: 1].
2. *Autogestión de Primer Nivel:* Más del 40% de los incidentes corresponden a dudas de cobertura Wi-Fi, canales o pruebas de velocidad (preguntas 2, 3, 4, 10, 12, 13), casos en los que el agente RAG resuelve la consulta citando el procedimiento oficial sin despachar técnicos innecesariamente.
3. *Casos Administrativos:* Las consultas de mora y cortes comerciales (pregunta 9) deben filtrarse hacia canales de cobro y no saturar la cola operativa técnica.
