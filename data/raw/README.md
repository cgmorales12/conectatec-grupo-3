# Base de Conocimiento Técnica (Corpus RAG) - ConectaTec

En este directorio se almacenan y referencian los documentos técnicos oficiales utilizados para la ingesta y vectorización (RAG) del sistema de triaje de soporte técnico para ISP (Caso 03).

---

## 1. Inventario de Fichas y Procedimientos Oficiales

### DOC-01: Guía de Luces LED ONT Huawei EchoLife (HG8245H / EG8145V5)
* *Origen:* Huawei Carrier Documentation.
* *Resumen operativo:*
  * *POWER:* Verde fijo (alimentación normal). Apagado (corte eléctrico o adaptador defectuoso).
  * *PON:* Verde fijo (enlace con OLT sincronizado). Verde parpadeante (estableciendo enlace).
  * *LOS:* Apagado (potencia óptica correcta). *Rojo parpadeante/fijo:* Nivel óptico por debajo de -27 dBm o fibra rota. Requiere despacho técnico urgente.
  * *LAN 1-4:* Verde parpadeante (tráfico de datos local activo).
  * *WLAN:* Verde fijo (red inalámbrica habilitada).

---

### DOC-02: Diagnóstico de Indicadores Lumínicos ONT ZTE F660/F670
* *Origen:* Soporte Técnico ZTE Global.
* *Resumen operativo:*
  * Indicador *LOS en Rojo:* Falla en la capa física de fibra (corte de acometida, atenuación severa). Acción: Escalamiento inmediato a cuadrilla externa.
  * Indicador *Internet en Rojo/Apagado con PON verde:* Falla de autenticación PPPoE o asignación DHCP de red troncal. Acción: Reinicio lógico y validación de credenciales ISP.

---

### DOC-03: Procedimiento Oficial de Reinicio Eléctrico (Ciclo de Energía)
* *Origen:* Manual Operativo ConectaTec ISP.
* *Pasos:*
  1. Apagar el router ONT mediante el botón posterior o desconectar el adaptador del tomacorriente.
  2. Esperar 30 segundos completos para liberar la energía residual de los condensadores.
  3. Reconectar la fuente de poder y encender el equipo.
  4. Esperar de 2 a 3 minutos hasta que las luces Power y PON se estabilicen en color verde continuo.
  5. Probar conectividad desde un dispositivo.

---

### DOC-04: Guía de Autogestión de Clave Wi-Fi (SSID y Seguridad WPA2/WPA3)
* *Origen:* Guía de Autoservicio ConectaTec ISP.
* *Pasos:*
  1. Conectar el equipo mediante cable Ethernet o red Wi-Fi actual.
  2. Abrir un navegador e ingresar a la dirección IP predeterminada: http://192.168.1.1 (o 192.168.100.1).
  3. Iniciar sesión con las credenciales de gestión de usuario indicadas en la etiqueta posterior del equipo.
  4. Navegar a la sección *WLAN* $\rightarrow$ *Basic Network Settings*.
  5. Modificar el campo WPA PreSharedKey con una clave de al menos 10 caracteres combinando letras mayúsculas, minúsculas y números.
  6. Guardar cambios (el equipo se reiniciará automáticamente).

---

### DOC-05: Optimización de Cobertura Wi-Fi: Comparativa 2.4 GHz vs. 5 GHz
* *Origen:* Whitepaper Wi-Fi Alliance.
* *Directrices:*
  * *Frecuencia 2.4 GHz:* Mayor alcance y mejor penetración a través de paredes y losas, pero menor velocidad (hasta 50-70 Mbps reales) y propensa a interferencias. Recomendada para domótica y zonas lejanas.
  * *Frecuencia 5 GHz:* Altísima velocidad (hasta el límite contratado del plan) y baja latencia, pero alcance reducido y sensible a obstáculos físicos. Recomendada para PCs, consolas y Smart TVs ubicados en el mismo ambiente del router.

---

### DOC-06: Protocolo de Medición de Velocidad de Conexión (Speedtest)
* *Origen:* Estándar Ookla / ConectaTec ISP.
* *Condiciones obligatorias para validez técnica:*
  1. Conectar la computadora directamente al puerto LAN 1 del router mediante cable UTP Categoría 5e o superior.
  2. Desconectar o pausar descargas, streaming y desconectar temporalmente las redes Wi-Fi de otros equipos.
  3. Cerrar aplicaciones en segundo plano (torrents, actualizaciones de Windows).
  4. Ejecutar el test apuntando al servidor local más cercano del ISP.

---

### DOC-07: Depuración de Resolución de Nombres de Dominio (DNS)
* *Origen:* RFC 1035 / Guía Técnica de Red.
* *Procedimiento:*
  1. Comprobar si hay ping hacia una IP pública directa (ping 8.8.8.8). Si responde, hay enlace de capa 3.
  2. Ejecutar nslookup google.com. Si no responde, existe fallo en los servidores DNS configurados.
  3. Ejecutar en consola: ipconfig /flushdns para vaciar caché corrupta.
  4. En caso de persistencia, configurar manualmente los DNS públicos primario (1.1.1.1) y secundario (8.8.8.8).

---

### DOC-08: Verificación de Integridad de Cableado de Red (UTP / RJ-45)
* *Origen:* Norma TIA-568.
* *Verificaciones:*
  * Si la tarjeta de red negocia a 100 Mbps en un enlace contratado de mayor velocidad, verificar si el cable carece de los 8 hilos funcionales o si la pestaña del conector RJ-45 está rota.
  * Inspeccionar dobleces pronunciados de 90 grados o aplastamiento bajo puertas.

---

### DOC-09: Criterios de Escalamiento Técnico por Rotura de Fibra Óptica
* *Origen:* Procedimiento de Cuadrilla de Planta Externa ISP.
* *Regla:* Ante reportes de luz LOS roja o quiebre evidente del jumper amarillo de fibra, se prohíbe exigir pruebas lógicas al abonado. El sistema debe generar orden de trabajo con prioridad Alta/Crítica para inspección y fusionado en campo por técnicos de cuadrilla.

---

### DOC-10 a DOC-15: Procedimientos Complementarios
* *DOC-10:* Interferencias electromagnéticas por electrodomésticos (hornos microondas, monitores de bebé en 2.4 GHz).
* *DOC-11:* Enlace y configuración de extensores de rango en modo punto de acceso cableado.
* *DOC-12:* Escaneo y selección de canales limpios (canales 1, 6 u 11 en 2.4 GHz).
* *DOC-13:* Diagnóstico de microcortes por atenuación fluctuante y renegociación PPPoE.
* *DOC-14:* Verificación de cortes administrativos por fecha de vencimiento y flujo de reactivación tras pago.
* *DOC-15:* Matriz estándar ITIL de cálculo determinista de prioridad (Cruce Impacto x Urgencia).
  
