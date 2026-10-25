"""
Script para generar el corpus oficial de 15 Manuales Técnicos en formato PDF y Markdown
Proyecto: ConectaTec - Triaje Inteligente de Incidentes ISP (Caso N.º 03 · Grupo 3)
Seminario de Titulación: Ingeniería de Software con IA Generativa - UNIANDES 2026
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

# Definición del corpus de 15 manuales técnicos oficiales
MANUALES = [
    {
        "id": "DOC-01",
        "archivo": "DOC-01_luces_led_ont_huawei",
        "titulo": "Guía de Interpretación de Luces LED en ONT Huawei EchoLife",
        "categoria": "Equipos de Cliente / ONT",
        "fabricante": "Huawei Technologies Co., Ltd. / Carrier Support",
        "version": "v3.2 - Octubre 2026",
        "descripcion": "Diagnóstico de conectividad y averías mediante la lectura del panel frontal de LEDs en terminales de red óptica (ONT) Huawei HG8245H, HG8546M y serie EchoLife.",
        "pasos": [
            ("Paso 1: Identificación de LED POWER", "Verifique que el indicador POWER permanezca encendido en color verde fijo. Si el LED está apagado, revise la conexión del adaptador de corriente de 12V / 1.5A a la toma de pared."),
            ("Paso 2: Diagnóstico de LED PON y LOS (Enlace Óptico)", "El LED PON en verde fijo indica enlace sincronizado con la OLT. Si el LED LOS parpadea en color rojo, existe rotura de fibra o potencia óptica inferior a -27 dBm. Proceda a verificar la curvatura de la fibra."),
            ("Paso 3: Verificación de LED LAN (Conexión Cableada)", "Los puertos LAN1 a LAN4 deben mostrar luz verde fija o intermitente al conectar un cable de red UTP hacia la PC o router secundario. Si no enciende, cambie de puerto o sustituya el cable de red."),
            ("Paso 4: Estado de LED WLAN e Internet", "El LED WLAN en verde intermitente confirma la emisión de radiofrecuencia inalámbrica 2.4 GHz. Si el LED Internet está rojo, el equipo no obtiene IP pública por falla de autenticación PPPoE."),
            ("Paso 5: Protocolo de Escalamiento", "Si el LED LOS continúa rojo tras reiniciar el equipo durante 10 segundos, no manipule el conector azul SC/APC y escale a soporte técnico para visita de cuadrilla por corte de fibra.")
        ],
        "tabla": [
            ["LED", "Color / Estado", "Significado Operativo", "Acción Recomendada"],
            ["POWER", "Verde Fijo", "Alimentación eléctrica correcta", "Ninguna acción requerida."],
            ["PON", "Verde Fijo", "ONT autenticada y registrada en OLT", "Servicio sincronizado."],
            ["LOS", "Rojo Parpadeante", "Pérdida de señal óptica (< -27 dBm)", "Revisar curvatura; escalar a cuadrilla."],
            ["LAN 1-4", "Verde Intermitente", "Tráfico de datos activo en puerto", "Conexión local operativa."],
            ["WLAN", "Verde Intermitente", "Transmisión Wi-Fi activa", "Red inalámbrica disponible."]
        ]
    },
    {
        "id": "DOC-02",
        "archivo": "DOC-02_indicadores_ont_zte",
        "titulo": "Manual de Diagnóstico de Indicadores Lumínicos en ONT ZTE F660/F670",
        "categoria": "Equipos de Cliente / ONT",
        "fabricante": "ZTE Corporation / Global Technical Support",
        "version": "v2.8 - Octubre 2026",
        "descripcion": "Manual de resolución de problemas de capa física y enlace GPON para equipos ONT ZTE modelos F660 (Mono-banda) y F670 (Doble banda AC1200).",
        "pasos": [
            ("Paso 1: Verificación del Indicador Power", "Compruebe que el LED Power esté verde continuo. En caso de parpadeo rojo, indica sobretensión o fallo interno del circuito de alimentación de la ONT."),
            ("Paso 2: Comprobación del Indicador PON", "El LED PON debe permanecer verde sin intermitencia. Si parpadea lentamente (1 Hz), la ONT está en proceso de descubrimiento y registro con la OLT."),
            ("Paso 3: Alarma de Indicador LOS", "El LED LOS apagado indica potencia óptica dentro del umbral normal (-8 dBm a -25 dBm). Si se enciende en rojo permanente, la fibra está desconectada o quebrada."),
            ("Paso 4: Indicadores Wi-Fi 2.4G y 5G", "En el modelo ZTE F670, ambos indicadores deben titilar rápidamente cuando hay intercambio de paquetes con dispositivos conectados."),
            ("Paso 5: Pruebas de Puerto Telefónico (POTS / TEL)", "Si el cliente reporta fallo de telefonía fija VoIP, el LED Phone/POTS debe estar verde fijo. Si parpadea, indica descolgado o fallo de registro SIP.")
        ],
        "tabla": [
            ["Indicador", "Patrón de Luz", "Estado del Enlace", "Diagnóstico Técnico"],
            ["Power", "Verde Continuo", "Normal", "Alimentación de 12V DC correcta."],
            ["PON", "Verde Continuo", "Enlace Sincronizado", "Sesión GPON activa con cabecera."],
            ["LOS", "Rojo Fijo", "Sin Señal Óptica", "Acometida cortada o conector sucio."],
            ["Internet", "Verde Titilante", "Tráfico WAN Activo", "Navegación habilitada en red."],
            ["WLAN", "Verde Titilante", "Radio Wi-Fi Activa", "Redes 2.4G / 5G transmitiendo."]
        ]
    },
    {
        "id": "DOC-03",
        "archivo": "DOC-03_reinicio_electrico_equipos",
        "titulo": "Protocolo de Verificación y Reinicio Eléctrico de Routers y ONT",
        "categoria": "Soporte Nivel 1 / Procedimientos",
        "fabricante": "ConectaTec ISP / Dirección de Operaciones de Red",
        "version": "v4.0 - Octubre 2026",
        "descripcion": "Procedimiento estándar para la purga de memoria volátil, resolución de microbloqueos de firmware y restablecimiento seguro de sesión de red en equipos terminales.",
        "pasos": [
            ("Paso 1: Verificación previa del estado de los cables", "Antes de desconectar la energía, confirme que el cable amarillo de fibra óptica no esté tirante ni doblado en ángulo menor a 90 grados. No toque la punta del conector óptico."),
            ("Paso 2: Desconexión segura del adaptador eléctrico", "Retire el conector cilíndrico de poder de la parte trasera de la ONT o router, o desconecte el transformador de la toma de pared."),
            ("Paso 3: Período de reposo de condensadores (Regla de los 30 segundos)", "Espere exactamente 30 segundos continuos con el equipo desconectado. Este lapso descarga los condensadores y vacía la tabla ARP y la memoria RAM del equipo."),
            ("Paso 4: Reconexión y secuencia de arranque", "Vuelva a conectar el adaptador de corriente. Espere entre 90 y 120 segundos mientras el procesador carga el firmware y negocia la sincronización PON."),
            ("Paso 5: Comprobación de navegación", "Una vez que los LEDs Power, PON y WLAN estén fijos, verifique la navegación abriendo un navegador en modo incógnito hacia un sitio externo.")
        ],
        "tabla": [
            ["Fase", "Tiempo Estimado", "Comportamiento Esperado", "Criterio de Validación"],
            ["Desconexión", "30 segundos", "Todos los LEDs apagados", "Descarga total de energía residual."],
            ["Secuencia Boot", "60 segundos", "Parpadeo secuencial de LEDs", "Carga de firmware y tablas locales."],
            ["Sincronización", "45 segundos", "LED PON fijo verde", "Autenticación correcta en OLT."],
            ["Prueba WAN", "15 segundos", "Ping exitoso a 8.8.8.8", "Servicio de navegación restablecido."]
        ]
    },
    {
        "id": "DOC-04",
        "archivo": "DOC-04_cambio_clave_wifi",
        "titulo": "Guía de Autogestión de Credenciales Wi-Fi (SSID y Clave WPA2/WPA3)",
        "categoria": "Redes Inalámbricas / Seguridad",
        "fabricante": "ConectaTec ISP / Centro de Atención al Cliente",
        "version": "v3.1 - Octubre 2026",
        "descripcion": "Instrucciones paso a paso para el cambio seguro del nombre de red (SSID) y contraseña de seguridad inalámbrica a través de la interfaz web institucional y portal de cliente.",
        "pasos": [
            ("Paso 1: Conexión al equipo mediante cable de red o Wi-Fi actual", "Conéctese preferiblemente por cable de red UTP a cualquier puerto LAN de la ONT, o mantenga conexión activa a la red Wi-Fi actual."),
            ("Paso 2: Acceso a la interfaz gráfica de administración", "Abra su navegador web e ingrese en la barra de direcciones la IP de puerta de enlace predeterminada: http://192.168.1.1 o http://192.168.100.1."),
            ("Paso 3: Autenticación de credenciales de usuario", "Ingrese el usuario y contraseña proporcionados en la etiqueta inferior de su equipo o use las credenciales seguras del portal de autogestión ConectaTec."),
            ("Paso 4: Modificación de parámetros inalámbricos (WLAN Settings)", "Navegue a la pestaña 'Network' -> 'WLAN' -> 'SSID Settings'. Modifique el campo 'SSID Name' y en 'WPA PreSharedKey' escriba una nueva clave con mínimo 10 caracteres alfanuméricos."),
            ("Paso 5: Aplicar cambios y reconexión de dispositivos", "Haga clic en 'Apply' o 'Guardar'. La red inalámbrica se reiniciará inmediatamente. Vuelva a vincular todos sus dispositivos con la nueva contraseña.")
        ],
        "tabla": [
            ["Parámetro", "Valor Recomendado", "Estándar de Seguridad", "Recomendación Técnica"],
            ["Modo de Seguridad", "WPA2-PSK [AES] / WPA3", "Estándar de cifrado robusto", "Evite WEP o WPA-TKIP obsoletos."],
            ["Longitud de Clave", "Mínimo 10 - 16 caracteres", "Políticas LOPDP de seguridad", "Combine mayúsculas, minúsculas y números."],
            ["Frecuencia 2.4 GHz", "Ancho de canal 20 MHz", "Mayor penetración en muros", "Ideal para dispositivos IoT y telefonía."],
            ["Frecuencia 5 GHz", "Ancho de canal 40/80 MHz", "Ultra velocidad y bajo retardo", "Ideal para streaming 4K y gaming."]
        ]
    },
    {
        "id": "DOC-05",
        "archivo": "DOC-05_cobertura_24ghz_5ghz",
        "titulo": "Optimización de Cobertura Inalámbrica: Bandas 2.4 GHz vs. 5 GHz",
        "categoria": "Redes Inalámbricas / Rendimiento",
        "fabricante": "Wi-Fi Alliance / Especificaciones Técnicas IEEE 802.11ax",
        "version": "v2.5 - Octubre 2026",
        "descripcion": "Criterios técnicos para la correcta selección de frecuencias inalámbricas, diferenciación de alcances físicos y mitigación de problemas de velocidad en domicilios y oficinas.",
        "pasos": [
            ("Paso 1: Entendimiento de las diferencias físicas entre bandas", "La banda 2.4 GHz posee ondas electromagnéticas más largas que atraviesan paredes pero con menor velocidad (hasta 70 Mbps reales). La banda 5 GHz ofrece ultra velocidad (hasta 500 Mbps) pero su alcance se atenúa drásticamente con muros."),
            ("Paso 2: Ubicación física óptima del router", "Coloque el router a una altura mínima de 1.2 a 1.5 metros del suelo, en una zona céntrica del inmueble, lejos de espejos, muros de concreto grueso y armarios metálicos."),
            ("Paso 3: Separación de nombres de red (SSID diferenciado)", "Configure nombres de red distintos para cada frecuencia, por ejemplo: 'ConectaTec_Familia_2.4G' y 'ConectaTec_Familia_5G' para elegir manualmente la mejor opción."),
            ("Paso 4: Asignación de dispositivos por banda", "Conecte televisores Smart TV, consolas de videojuegos y laptops de teletrabajo a la banda 5 GHz. Conecte impresoras, cámaras de seguridad y smartphones lejanos a la banda 2.4 GHz."),
            ("Paso 5: Solución de cobertura extendida (Mesh / Repetidores)", "Si el inmueble supera los 90 metros cuadrados o posee varias plantas, instale repetidores enlazados por cable Ethernet o un sistema Wi-Fi Mesh homologado.")
        ],
        "tabla": [
            ["Característica", "Banda 2.4 GHz", "Banda 5 GHz", "Uso Recomendado"],
            ["Alcance Físico", "Alto (aprox. 15 - 20 m)", "Medio-Bajo (aprox. 7 - 10 m)", "2.4G para distancia, 5G para cercanía."],
            ["Velocidad Máxima Real", "40 a 70 Mbps", "200 a 600+ Mbps", "5G para planes de alta velocidad contratados."],
            ["Interferencia Externa", "Alta (Bluetooth, microondas)", "Muy baja (canales limpios)", "5G libre de saturación residencial."],
            ["Penetración de Muros", "Buena (atraviesa 2-3 tabiques)", "Baja (se atenúa tras 1 muro)", "Evite 5G a través de muros de hormigón."]
        ]
    },
    {
        "id": "DOC-06",
        "archivo": "DOC-06_test_velocidad_ethernet",
        "titulo": "Procedimiento Oficial para Prueba de Velocidad de Navegación (Test Ethernet)",
        "categoria": "Soporte Nivel 1 / Calidad de Servicio",
        "fabricante": "Ookla Speedtest / Directrices ConectaTec NOC",
        "version": "v3.0 - Octubre 2026",
        "descripcion": "Protocolo técnico vinculante para medir con precisión la tasa de transferencia de bajada y subida según la velocidad contratada, descartando cuellos de botella inalámbricos.",
        "pasos": [
            ("Paso 1: Desconexión de dispositivos concurrentes", "Desactive temporalmente la conexión Wi-Fi en todos los teléfonos móviles, consolas y Smart TVs del hogar para que ningún consumo de fondo afecte la medición."),
            ("Paso 2: Conexión directa mediante cable Ethernet", "Conecte una computadora portátil o de escritorio directamente a un puerto LAN Gigabit de la ONT utilizando un cable de red UTP Categoría 5e o Categoría 6."),
            ("Paso 3: Verificación de la velocidad de negociación de la tarjeta", "En Windows, abra 'Conexiones de red' y confirme que la tarjeta Ethernet indique 'Velocidad: 1.0 Gbps (1000 Mbps)'. Si marca 100 Mbps, el cable o la tarjeta limitan el test."),
            ("Paso 4: Ejecución del test de velocidad en servidor local", "Cierre aplicaciones P2P, torrents y descargas. Ingrese a https://www.speedtest.net y seleccione el servidor oficial de ConectaTec en su ciudad."),
            ("Paso 5: Criterio de conformidad de velocidad", "El test debe entregar al menos el 80% de la velocidad contratada por cable. Las pruebas por Wi-Fi no son válidas legalmente para reclamos de ancho de banda.")
        ],
        "tabla": [
            ["Plan Contratado", "Negociación LAN Mínima", "Velocidad de Bajada Aceptable", "Latencia Máxima (Ping)"],
            ["100 Mbps Simétrico", "1000 Mbps (Gigabit)", "90 a 100 Mbps", "< 15 ms en servidor local"],
            ["200 Mbps Simétrico", "1000 Mbps (Gigabit)", "180 a 200 Mbps", "< 12 ms en servidor local"],
            ["400 Mbps Simétrico", "1000 Mbps (Gigabit)", "360 a 400 Mbps", "< 10 ms en servidor local"],
            ["600 Mbps Simétrico", "1000 Mbps (Gigabit)", "540 a 600 Mbps", "< 8 ms en servidor local"]
        ]
    },
    {
        "id": "DOC-07",
        "archivo": "DOC-07_diagnostico_dns",
        "titulo": "Diagnóstico y Depuración de Resolución de Nombres de Dominio (DNS)",
        "categoria": "Redes IP / Configuración",
        "fabricante": "IETF RFC 1035 / ConectaTec Network Engineering",
        "version": "v2.2 - Octubre 2026",
        "descripcion": "Detección y solución del síntoma 'Conectado sin acceso a Internet' originado por fallos de caché local de DNS o servidores de resolución no disponibles.",
        "pasos": [
            ("Paso 1: Identificación del síntoma de fallo DNS", "El síntoma clásico ocurre cuando aplicaciones como WhatsApp o Telegram funcionan (conectan por IP), pero los navegadores muestran 'No se puede acceder a este sitio' (ERR_NAME_NOT_RESOLVED)."),
            ("Paso 2: Ejecución de ping por dirección IP directa", "Abra la consola de comandos (`cmd`) y ejecute: `ping 8.8.8.8`. Si hay respuesta pero `ping google.com` falla, el problema es 100% de resolución DNS."),
            ("Paso 3: Purga de caché local de resolución DNS", "En la consola de comandos de Windows ejecute el comando: `ipconfig /flushdns` y presione Enter. El sistema confirmará que se vació la caché correctamente."),
            ("Paso 4: Configuración manual de servidores DNS públicos", "En las propiedades del protocolo TCP/IPv4 de su adaptador, asigne manualmente: Servidor DNS preferido: 8.8.8.8 y Servidor DNS alternativo: 1.1.1.1."),
            ("Paso 5: Validación final con comando nslookup", "Ejecute en la consola: `nslookup conectatec.ec` para comprobar que la resolución retorne la dirección IP pública correcta en menos de 30 ms.")
        ],
        "tabla": [
            ["Servidor DNS", "IP Primaria", "IP Secundaria", "Ventaja Operativa"],
            ["ConectaTec Primario", "190.15.10.2", "190.15.10.3", "Menor latencia nacional por ruta directa."],
            ["Google Public DNS", "8.8.8.8", "8.8.4.4", "Alta disponibilidad global y estabilidad."],
            ["Cloudflare 1.1.1.1", "1.1.1.1", "1.0.0.1", "Máxima velocidad de resolución y privacidad."]
        ]
    },
    {
        "id": "DOC-08",
        "archivo": "DOC-08_cableado_red_utp",
        "titulo": "Verificación de Cableado de Red de Cobre (UTP Categoría 5e / 6)",
        "categoria": "Infraestructura Física / Cableado",
        "fabricante": "TIA/EIA-568-C.2 / ConectaTec Infraestructura",
        "version": "v2.0 - Octubre 2026",
        "descripcion": "Identificación de degradación de velocidad a 100 Mbps (Fast Ethernet) provocada por daños en pines de conectores RJ-45, dobleces o cables UTP de categoría deficiente.",
        "pasos": [
            ("Paso 1: Inspección visual del cable y conectores RJ-45", "Examine los extremos del cable de red. La pestaña plástica de retención no debe estar rota y los 8 pines dorados deben estar alineados sin óxido."),
            ("Paso 2: Comprobación de la categoría impresa en el forro", "Verifique el texto impreso en el cable. Debe indicar 'UTP CAT.5E' (soporta hasta 1000 Mbps a corta distancia) o 'UTP CAT.6' (óptimo para Gigabit). Los cables Categoría 5 antigua solo dan 100 Mbps."),
            ("Paso 3: Detección del síntoma de degradación a 100 Mbps", "Si un cliente con plan de 200 Mbps o más solo recibe 94-95 Mbps en el test de velocidad, significa que uno de los 8 hilos del cable UTP está roto y el puerto conmutó a 100 Mbps."),
            ("Paso 4: Prueba con cable de parcheo (Patch Cord) alternativo", "Sustituya el cable sospechoso por un cable nuevo certificado Categoría 6 de 1 o 2 metros y repita la comprobación en el adaptador de red."),
            ("Paso 5: Normas de crimpado estándar T568B", "En caso de rehacer los conectores, verifique el código de colores oficial: Blanco-Naranja, Naranja, Blanco-Verde, Azul, Blanco-Azul, Verde, Blanco-Marrón, Marrón.")
        ],
        "tabla": [
            ["Categoría UTP", "Velocidad Máxima", "Frecuencia", "Uso Recomendado"],
            ["Categoría 5", "100 Mbps", "100 MHz", "Obsoleto. Reemplazar de inmediato."],
            ["Categoría 5e", "1000 Mbps (1 Gbps)", "100 MHz", "Mínimo aceptable para planes de hasta 300 Mbps."],
            ["Categoría 6", "1000 Mbps / 10 Gbps", "250 MHz", "Estándar oficial ConectaTec para todos los clientes."]
        ]
    },
    {
        "id": "DOC-09",
        "archivo": "DOC-09_rotura_fibra_optica",
        "titulo": "Criterios de Escalamiento por Atenuación y Rotura de Acometida de Fibra Óptica",
        "categoria": "Red Óptica / Escalamiento Campo",
        "fabricante": "ITU-T G.984 GPON / ConectaTec Planta Externa",
        "version": "v3.5 - Octubre 2026",
        "descripcion": "Protocolo para determinar cuándo una incidencia no es solucionable de forma remota y debe escalarse con prioridad Alta para despacho de cuadrilla con fusionadora óptica.",
        "pasos": [
            ("Paso 1: Detección de alarma óptica crítica", "Si la ONT presenta el LED LOS en rojo permanente o parpadeante, y la potencia reportada por telemetría OLT es '-Infinity dBm', existe corte físico de la fibra."),
            ("Paso 2: Inspección de la roseta óptica interior", "Solicite al usuario verificar si el cable fino negro o amarillo que va desde la roseta de pared hasta la ONT fue mordido por mascotas, aplastado por muebles o desconectado."),
            ("Paso 3: Consulta en sistema de monitoreo OLT", "El operador del NOC verifica si el corte afecta a una sola ONT (rotura de acometida individual) o si afecta a varias ONTs del mismo puerto PON (rotura de cable troncal / NAP dañada)."),
            ("Paso 4: Registro y escalamiento en tablero de tickets", "Si la rotura es confirmada, genere un ticket con Categoría 'Fibra Óptica', Impacto 'Medio' (o 'Alto' si es empresa), Urgencia 'Alta' y Prioridad 'Alta'."),
            ("Paso 5: Asignación de cuadrilla de planta externa", "Despache la orden de trabajo al técnico de cuadrilla con el metraje estimado y ubicación geográfica del divisor óptico (Splitter) correspondiente.")
        ],
        "tabla": [
            ["Potencia Óptica (Rx)", "Estado del Enlace", "Nivel de Servicio", "Acción Operativa"],
            ["-15 a -24 dBm", "Óptimo", "100% Calidad", "Operación normal de enlace."],
            ["-25 a -27 dBm", "Marginal", "Degradación / Alerta", "Programar mantenimiento preventivo."],
            ["Menor a -28 dBm", "Crítico", "Microcortes frecuentes", "Escalar ticket a cuadrilla por atenuación."],
            ["-Infinity (LOS Rojo)", "Corte Total", "Sin Enlace Óptico", "Escalamiento inmediato: cuadrilla de campo."]
        ]
    },
    {
        "id": "DOC-10",
        "archivo": "DOC-10_interferencias_wifi",
        "titulo": "Detección de Interferencias por Electrodomésticos y Atenuación Estructural",
        "categoria": "Redes Inalámbricas / Diagnóstico",
        "fabricante": "TP-Link Technical Support / Wi-Fi Troubleshooting",
        "version": "v2.1 - Octubre 2026",
        "descripcion": "Identificación de fuentes electromagnéticas parásitas y materiales de construcción que degradan la potencia de radiofrecuencia en instalaciones residenciales y comerciales.",
        "pasos": [
            ("Paso 1: Detección de interferencia por hornos microondas", "Los hornos microondas emiten radiación en la frecuencia exacta de 2.45 GHz. Si el cliente experimenta desconexión total del Wi-Fi al calentar alimentos, la causa es fuga electromagnética del microondas."),
            ("Paso 2: Evaluación de teléfonos inalámbricos y monitores de bebé", "Muchos transmisores analógicos de vigilancia de bebés y teléfonos DECT antiguos saturan la banda 2.4 GHz. Separe el router al menos 3 metros de estos equipos."),
            ("Paso 3: Análisis de obstáculos estructurales (Paredes y Espejos)", "El concreto armado y los vidrios espejados (con recubrimiento metálico) atenúan la señal Wi-Fi hasta en un 80%. Nunca ubique el router detrás de televisores grandes o peceras."),
            ("Paso 4: Mitigación inmediata mediante migración a 5 GHz", "Conecte los dispositivos de trabajo a la banda 5 GHz, la cual opera en un espectro completamente inmune a interferencias de microondas y dispositivos Bluetooth."),
            ("Paso 5: Reubicación física del equipo", "Si la cobertura es insuficiente, reubique el router en una posición despejada y elevada, libre de encerramientos en muebles de madera maciza.")
        ],
        "tabla": [
            ["Material / Dispositivo", "Nivel de Atenuación", "Efecto en la Señal Wi-Fi", "Distancia Mínima Recomendada"],
            ["Horno Microondas", "Crítico (Banda 2.4G)", "Corte total de transmisión", "Mínimo 3 metros de distancia."],
            ["Muro de Concreto Armado", "Alto (-12 a -18 dB)", "Pérdida drástica de señal", "Requiere repetidor o cable UTP."],
            ["Espejos y Vidrio Templado", "Medio-Alto (-8 a -10 dB)", "Reflexión y rebote de onda", "No instalar router frente a espejos."],
            ["Pared de Drywall / Tabique", "Bajo (-2 a -4 dB)", "Atenuación mínima tolerable", "Permite cobertura normal."]
        ]
    },
    {
        "id": "DOC-11",
        "archivo": "DOC-11_router_modo_puente",
        "titulo": "Protocolo de Configuración de Router Neutro o Repetidor en Modo Puente",
        "categoria": "Enrutamiento / Arquitectura Cliente",
        "fabricante": "MikroTik RouterOS / Guía de Instalación ConectaTec",
        "version": "v2.6 - Octubre 2026",
        "descripcion": "Procedimiento para evitar problemas de Doble NAT (NAT Loopback) y conflictos de direcciones IP al conectar routers secundarios o repetidores Wi-Fi del cliente.",
        "pasos": [
            ("Paso 1: Identificación del problema de Doble NAT", "Ocurre cuando el cliente conecta el puerto WAN de su router propio al puerto LAN de la ONT sin configurar modo puente, creando dos redes IP diferentes y bloqueando cámaras y juegos online."),
            ("Paso 2: Desactivación del servidor DHCP en el equipo secundario", "Acceda a la configuración del router secundario del cliente y desactive completamente la función 'DHCP Server' para que la ONT ConectaTec sea la única que entregue IPs."),
            ("Paso 3: Modificación de la IP de gestión local", "Cambie la dirección IP LAN del router secundario a una IP libre dentro del segmento de la ONT, por ejemplo: 192.168.1.254, para evitar conflicto con la 192.168.1.1."),
            ("Paso 4: Conexión física por puerto LAN a LAN", "Desconecte el cable del puerto azul (WAN/Internet) del router secundario y conéctelo en uno de sus puertos amarillos (LAN). Conecte el otro extremo a la ONT."),
            ("Paso 5: Verificación de difusión Wi-Fi unificada", "Configure el mismo nombre de red (SSID) y contraseña en ambos equipos para permitir itinerancia (roaming) transparente de los usuarios por todo el inmueble.")
        ],
        "tabla": [
            ["Configuración", "Modo Router Típico (Incorrecto)", "Modo Access Point / Bridge (Correcto)"],
            ["Servidor DHCP", "Activo en ambos equipos (Conflicto IP)", "Activo solo en la ONT ConectaTec."],
            ["Segmento de Red", "Dos redes separadas (Doble NAT)", "Una sola red unificada (/24)."],
            ["Puerto Utilizado", "Cable en puerto WAN del router secundario", "Cable en puerto LAN del router secundario."],
            ["Visibilidad de Dispositivos", "Dispositivos aislados no se pueden compartir", "Impresoras y carpetas visibles en toda la red."]
        ]
    },
    {
        "id": "DOC-12",
        "archivo": "DOC-12_canales_wifi_saturacion",
        "titulo": "Guía de Detección de Saturación de Canal Wi-Fi y Selección Manual",
        "categoria": "Redes Inalámbricas / Optimización",
        "fabricante": "IEEE 802.11 Spectral Standards / ConectaTec NOC",
        "version": "v2.3 - Octubre 2026",
        "descripcion": "Método para auditar el espectro radioeléctrico con herramientas de análisis de redes y fijar canales inalámbricos limpios evitando solapamientos destructivos.",
        "pasos": [
            ("Paso 1: Detección de lentitud por interferencia cocanal", "En edificios residenciales, múltiples routers de vecinos transmiten en el mismo canal, generando colisiones de paquetes y lentitud extrema a pesar de tener buena señal."),
            ("Paso 2: Escaneo de radiofrecuencia con aplicaciones móviles", "Utilice una app de análisis de espectro (como WiFi Analyzer) para observar qué canales están ocupados en la frecuencia 2.4 GHz."),
            ("Paso 3: Regla de los tres canales no solapados (1, 6 y 11)", "En la banda 2.4 GHz, únicamente los canales 1, 6 y 11 no se interfieren entre sí. Jamás seleccione canales intermedios como el 2, 3, 4, 5, 7, 8, 9 o 10."),
            ("Paso 4: Fijación manual de canal en la ONT", "Ingrese a la interfaz web de la ONT (192.168.1.1), navegue a WLAN y cambie la opción 'Channel: Auto' al canal menos saturado (1, 6 u 11)."),
            ("Paso 5: Configuración de canales en banda 5 GHz", "En 5 GHz elija canales limpios del rango bajo (canales 36, 40, 44 o 48) para evitar caídas provocadas por radares meteorológicos (canales DFS).")
        ],
        "tabla": [
            ["Canal 2.4 GHz", "Frecuencia Central", "Canales con los que Interfiere", "Estado de Homologación"],
            ["Canal 1", "2412 MHz", "Canales 2, 3", "Recomendado oficial ConectaTec."],
            ["Canales 2 al 5", "2417 a 2432 MHz", "Interfiere con canal 1 y canal 6", "Prohibido: genera solapamiento."],
            ["Canal 6", "2437 MHz", "Canales 4, 5, 7, 8", "Recomendado oficial ConectaTec."],
            ["Canales 7 al 10", "2442 a 2457 MHz", "Interfiere con canal 6 y canal 11", "Prohibido: genera solapamiento."],
            ["Canal 11", "2462 MHz", "Canales 9, 10", "Recomendado oficial ConectaTec."]
        ]
    },
    {
        "id": "DOC-13",
        "archivo": "DOC-13_intermitencia_pppoe",
        "titulo": "Procedimiento ante Microcortes o Caídas Intermitentes de Sesión PPPoE",
        "categoria": "Protocolos de Acceso / Diagnóstico ISP",
        "fabricante": "Broadband Forum TR-101 / ConectaTec Core Network",
        "version": "v3.2 - Octubre 2026",
        "descripcion": "Diagnóstico y resolución de fallos donde la luz óptica (PON) permanece verde pero la conexión se corta cada pocos minutos debido a desautenticación en el servidor BRAS.",
        "pasos": [
            ("Paso 1: Verificación de la estabilidad física de la fibra", "Confirme en el sistema de telemetría de la OLT que la potencia óptica no fluctúe más de 2 dBm durante el día. Si la potencia es estable, la falla no es física."),
            ("Paso 2: Consulta del registro de caídas en el servidor de autenticación (BRAS)", "Revise el historial del cliente en el servidor RADIUS. Si aparecen mensajes 'Terminated: Lost-Carrier' o 'Admin-Reset', la sesión está siendo forzada a desconectar."),
            ("Paso 3: Verificación de MTU / MRU en la configuración WAN", "Asegúrese de que el parámetro MTU en la conexión PPPoE de la ONT esté configurado exactamente en 1492 bytes. Un MTU de 1500 causa fragmentación y microcortes."),
            ("Paso 4: Comprobación de clonación de credenciales PPPoE", "Verifique que el usuario PPPoE del cliente no esté activo simultáneamente en otra ONT de la red, lo que causaría desconexión cíclica continua."),
            ("Paso 5: Reinicio de puerto lógico en OLT", "Ejecute el comando de reinicio administrativo de la interfaz lógica GPON del cliente en la OLT para forzar una reasignación limpia de IP pública.")
        ],
        "tabla": [
            ["Causa Posible", "Código de Alerta en Registro", "Impacto en el Usuario", "Acción Correctiva"],
            ["MTU Desajustado", "Packet Fragmentation Needed", "Páginas cargan a medias o lentas", "Configurar MTU en 1492 bytes."],
            ["Fluctuación Óptica", "Optical Loss of Margin", "Microcortes cada 5 - 10 minutos", "Limpiar conector SC/APC de fibra."],
            ["Conflicto de Usuario", "Duplicate User Login Rejected", "Corte total cada 2 minutos", "Resetear contraseña PPPoE en RADIUS."],
            ["Reinicio de Firmware", "System Uptime Reset", "Equipo se apaga solo", "Sustituir transformador de 12V dañado."]
        ]
    },
    {
        "id": "DOC-14",
        "archivo": "DOC-14_facturacion_cortes_mora",
        "titulo": "Guía de Consulta de Estado Comercial, Corte por Mora y Canales de Pago",
        "categoria": "Atención al Cliente / Facturación",
        "fabricante": "ConectaTec ISP / Gerencia de Administración y Cobranzas",
        "version": "v4.1 - Octubre 2026",
        "descripcion": "Protocolo para identificar suspensiones comerciales del servicio por cuotas pendientes, diferenciar cortes técnicos de administrativos y orientar al cliente.",
        "pasos": [
            ("Paso 1: Identificación del estado de suspensión comercial", "Cuando el servicio está suspendido por falta de pago, los LEDs de la ONT están normales (Power, PON y WLAN verdes), pero al navegar el usuario es redirigido al portal de cobros."),
            ("Paso 2: Consulta en el sistema de facturación y CRM", "El agente de mesa de ayuda o el bot inteligente consulta el número de cédula o código de abonado en la base de datos comercial para verificar deudas pendientes."),
            ("Paso 3: Notificación de saldos y fecha de corte", "Informe al cliente el valor pendiente de pago, la fecha límite que venció y las facturas acumuladas de forma clara y respetuosa según las leyes de defensa del consumidor."),
            ("Paso 4: Canales de pago electrónico autorizados", "Indique los canales habilitados para pago inmediato: transferencia bancaria a Banco Pichincha / Guayaquil, botón de pagos en web ConectaTec y puntos de pago externos."),
            ("Paso 5: Reactivación automática del servicio", "Una vez procesado el pago en el sistema bancario, el servidor de facturación emite la orden automática a la OLT y el servicio se restablece en un lapso máximo de 15 minutos.")
        ],
        "tabla": [
            ["Estado en Sistema", "Comportamiento del Navegador", "Tipo de Bloqueo", "Tiempo de Reactivación"],
            ["Activo al Día", "Navegación normal a toda velocidad", "Sin bloqueo", "Inmediato."],
            ["Suspendido por Mora", "Redirección a portal de pagos institucional", "Bloqueo comercial de tráfico", "Máximo 15 minutos tras pagar."],
            ["Promesa de Pago", "Navegación rehabilitada por 48 horas", "Prórroga temporal", "Automática al registrar promesa."],
            ["Cancelado Definitivo", "Sin perfil en OLT / Retiro de equipo", "Desinstalación física", "Requiere nuevo contrato de servicio."]
        ]
    },
    {
        "id": "DOC-15",
        "archivo": "DOC-15_matriz_itil_incidentes",
        "titulo": "Matriz ITIL de Clasificación de Incidentes, Impacto, Urgencia y SLA",
        "categoria": "Gestión de Servicios TI / ITIL v4",
        "fabricante": "AXELOS ITIL v4 Foundation / ConectaTec Operations",
        "version": "v5.0 - Octubre 2026",
        "descripcion": "Matriz oficial determinista para la priorización matemática de solicitudes técnicas según el cruce de Impacto y Urgencia, con tiempos SLA vinculantes.",
        "pasos": [
            ("Paso 1: Determinación del Impacto Institucional", "El impacto mide el alcance o daño del problema. Es Alto si afecta a empresas, instituciones educativas o zonas enteras; Medio si afecta a un hogar completo; Bajo si afecta a un solo equipo."),
            ("Paso 2: Determinación de la Urgencia del Reporte", "La urgencia mide la rapidez necesaria para actuar. Es Alta si hay corte total del servicio o evento crítico en curso; Media si hay lentitud o degradación; Baja si es una consulta informativa."),
            ("Paso 3: Cruce matricial determinista en código Python", "El sistema toma el Impacto y la Urgencia extraídos por el modelo y aplica la tabla determinista sin intervención estocástica de la IA para obtener la Prioridad."),
            ("Paso 4: Asignación de tiempo máximo de resolución (SLA)", "A cada prioridad se le asigna un tiempo máximo de atención: Prioridad Alta = 2 horas; Prioridad Media = 6 horas; Prioridad Baja = 24 horas."),
            ("Paso 5: Monitoreo y alarma de vencimiento de SLA", "El sistema supervisa los tiempos en el tablero Kanban. Si un ticket de Prioridad Alta no es atendido en 60 minutos, se emite una notificación de advertencia al supervisor.")
        ],
        "tabla": [
            ["Impacto", "Urgencia", "Prioridad Resultante", "Tiempo SLA Máximo", "Nivel de Atención"],
            ["Alto (Zona/Empresa)", "Alta (Corte Total)", "ALTA", "2 Horas", "Cuadrilla Inmediata / NOC Nivel 2"],
            ["Alto (Zona/Empresa)", "Media (Lentitud)", "MEDIA", "6 Horas", "Optimización de Enlace"],
            ["Alto (Zona/Empresa)", "Baja (Consulta)", "BAJA", "24 Horas", "Mesa de Ayuda Nivel 1"],
            ["Medio (Hogar)", "Alta (Corte Total)", "ALTA", "4 Horas", "Soporte Presencial Nivel 2"],
            ["Medio (Hogar)", "Media (Lentitud)", "MEDIA", "8 Horas", "Soporte Remoto Nivel 1"],
            ["Bajo (1 Dispositivo)", "Baja (Consulta)", "BAJA", "24 Horas", "Autoatención / Bot IA"]
        ]
    }
]

def generar_archivos():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    styles = getSampleStyleSheet()
    
    # Estilos tipográficos personalizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F2E2C'),
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#A64B24'),
        spaceAfter=12
    )
    
    desc_style = ParagraphStyle(
        'DocDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#3E5450'),
        spaceAfter=14
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E6F64'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'StepBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1D1D1F'),
        spaceAfter=8
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1D1D1F')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    for doc in MANUALES:
        # 1. Generar archivo Markdown (.md)
        md_filename = f"{doc['archivo']}.md"
        md_path = os.path.join(output_dir, md_filename)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {doc['id']}: {doc['titulo']}\n\n")
            f.write(f"**Categoría:** {doc['categoria']}  \n")
            f.write(f"**Fabricante / Origen:** {doc['fabricante']}  \n")
            f.write(f"**Versión / Vigencia:** {doc['version']}  \n\n")
            f.write(f"## Descripción General\n{doc['descripcion']}\n\n")
            f.write("## Procedimiento Operativo Paso a Paso\n")
            for paso_num, paso_txt in doc['pasos']:
                f.write(f"### {paso_num}\n{paso_txt}\n\n")
            f.write("## Matriz de Diagnóstico Rápido\n\n")
            headers = doc['tabla'][0]
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
            for row in doc['tabla'][1:]:
                f.write("| " + " | ".join(row) + " |\n")
            f.write("\n---\n*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*\n")
            
        # 2. Generar archivo PDF (.pdf)
        pdf_filename = f"{doc['archivo']}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        pdf = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch
        )
        
        elements = []
        
        # Cabecera
        elements.append(Paragraph(f"{doc['id']} · CONECTATEC ISP", subtitle_style))
        elements.append(Paragraph(doc['titulo'], title_style))
        elements.append(Paragraph(f"<b>Categoría:</b> {doc['categoria']} | <b>Fabricante:</b> {doc['fabricante']} | <b>Vigencia:</b> {doc['version']}", desc_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E6F64'), spaceAfter=10))
        
        # Descripción
        elements.append(Paragraph("<b>Descripción del Procedimiento:</b>", h2_style))
        elements.append(Paragraph(doc['descripcion'], body_style))
        elements.append(Spacer(1, 6))
        
        # Pasos
        elements.append(Paragraph("<b>Procedimiento Técnico Paso a Paso:</b>", h2_style))
        for paso_num, paso_txt in doc['pasos']:
            elements.append(Paragraph(f"<b>{paso_num}:</b> {paso_txt}", body_style))
        elements.append(Spacer(1, 8))
        
        # Tabla de diagnóstico
        elements.append(Paragraph("<b>Matriz Operativa de Diagnóstico y Criterios:</b>", h2_style))
        raw_table_data = doc['tabla']
        formatted_table_data = []
        
        # Cabecera de la tabla
        header_row = [Paragraph(f"<b>{cell}</b>", table_header_style) for cell in raw_table_data[0]]
        formatted_table_data.append(header_row)
        
        # Filas de datos
        for row in raw_table_data[1:]:
            formatted_row = [Paragraph(cell, table_text_style) for cell in row]
            formatted_table_data.append(formatted_row)
            
        t = Table(formatted_table_data, colWidths=[1.3*inch, 1.8*inch, 2.2*inch, 1.9*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2E2C')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D6DED8')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FAFBF7')]),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 14))
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#D6DED8'), spaceAfter=6))
        elements.append(Paragraph("<font size=7 color='#5E716D'>Documento Oficial ConectaTec ISP · Prohibida su alteración no autorizada · Seminario de Titulación UNIANDES 2026</font>", desc_style))
        
        pdf.build(elements)
        print(f"Generado con éxito: {pdf_filename} y {md_filename}")

if __name__ == "__main__":
    generar_archivos()
