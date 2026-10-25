# DOC-12: Guía de Detección de Saturación de Canal Wi-Fi y Selección Manual

**Categoría:** Redes Inalámbricas / Optimización  
**Fabricante / Origen:** IEEE 802.11 Spectral Standards / ConectaTec NOC  
**Versión / Vigencia:** v2.3 - Octubre 2026  

## Descripción General
Método para auditar el espectro radioeléctrico con herramientas de análisis de redes y fijar canales inalámbricos limpios evitando solapamientos destructivos.

## Procedimiento Operativo Paso a Paso
### Paso 1: Detección de lentitud por interferencia cocanal
En edificios residenciales, múltiples routers de vecinos transmiten en el mismo canal, generando colisiones de paquetes y lentitud extrema a pesar de tener buena señal.

### Paso 2: Escaneo de radiofrecuencia con aplicaciones móviles
Utilice una app de análisis de espectro (como WiFi Analyzer) para observar qué canales están ocupados en la frecuencia 2.4 GHz.

### Paso 3: Regla de los tres canales no solapados (1, 6 y 11)
En la banda 2.4 GHz, únicamente los canales 1, 6 y 11 no se interfieren entre sí. Jamás seleccione canales intermedios como el 2, 3, 4, 5, 7, 8, 9 o 10.

### Paso 4: Fijación manual de canal en la ONT
Ingrese a la interfaz web de la ONT (192.168.1.1), navegue a WLAN y cambie la opción 'Channel: Auto' al canal menos saturado (1, 6 u 11).

### Paso 5: Configuración de canales en banda 5 GHz
En 5 GHz elija canales limpios del rango bajo (canales 36, 40, 44 o 48) para evitar caídas provocadas por radares meteorológicos (canales DFS).

## Matriz de Diagnóstico Rápido

| Canal 2.4 GHz | Frecuencia Central | Canales con los que Interfiere | Estado de Homologación |
| --- | --- | --- | --- |
| Canal 1 | 2412 MHz | Canales 2, 3 | Recomendado oficial ConectaTec. |
| Canales 2 al 5 | 2417 a 2432 MHz | Interfiere con canal 1 y canal 6 | Prohibido: genera solapamiento. |
| Canal 6 | 2437 MHz | Canales 4, 5, 7, 8 | Recomendado oficial ConectaTec. |
| Canales 7 al 10 | 2442 a 2457 MHz | Interfiere con canal 6 y canal 11 | Prohibido: genera solapamiento. |
| Canal 11 | 2462 MHz | Canales 9, 10 | Recomendado oficial ConectaTec. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
