# DOC-06: Procedimiento Oficial para Prueba de Velocidad de Navegación (Test Ethernet)

**Categoría:** Soporte Nivel 1 / Calidad de Servicio  
**Fabricante / Origen:** Ookla Speedtest / Directrices ConectaTec NOC  
**Versión / Vigencia:** v3.0 - Octubre 2026  

## Descripción General
Protocolo técnico vinculante para medir con precisión la tasa de transferencia de bajada y subida según la velocidad contratada, descartando cuellos de botella inalámbricos.

## Procedimiento Operativo Paso a Paso
### Paso 1: Desconexión de dispositivos concurrentes
Desactive temporalmente la conexión Wi-Fi en todos los teléfonos móviles, consolas y Smart TVs del hogar para que ningún consumo de fondo afecte la medición.

### Paso 2: Conexión directa mediante cable Ethernet
Conecte una computadora portátil o de escritorio directamente a un puerto LAN Gigabit de la ONT utilizando un cable de red UTP Categoría 5e o Categoría 6.

### Paso 3: Verificación de la velocidad de negociación de la tarjeta
En Windows, abra 'Conexiones de red' y confirme que la tarjeta Ethernet indique 'Velocidad: 1.0 Gbps (1000 Mbps)'. Si marca 100 Mbps, el cable o la tarjeta limitan el test.

### Paso 4: Ejecución del test de velocidad en servidor local
Cierre aplicaciones P2P, torrents y descargas. Ingrese a https://www.speedtest.net y seleccione el servidor oficial de ConectaTec en su ciudad.

### Paso 5: Criterio de conformidad de velocidad
El test debe entregar al menos el 80% de la velocidad contratada por cable. Las pruebas por Wi-Fi no son válidas legalmente para reclamos de ancho de banda.

## Matriz de Diagnóstico Rápido

| Plan Contratado | Negociación LAN Mínima | Velocidad de Bajada Aceptable | Latencia Máxima (Ping) |
| --- | --- | --- | --- |
| 100 Mbps Simétrico | 1000 Mbps (Gigabit) | 90 a 100 Mbps | < 15 ms en servidor local |
| 200 Mbps Simétrico | 1000 Mbps (Gigabit) | 180 a 200 Mbps | < 12 ms en servidor local |
| 400 Mbps Simétrico | 1000 Mbps (Gigabit) | 360 a 400 Mbps | < 10 ms en servidor local |
| 600 Mbps Simétrico | 1000 Mbps (Gigabit) | 540 a 600 Mbps | < 8 ms en servidor local |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
