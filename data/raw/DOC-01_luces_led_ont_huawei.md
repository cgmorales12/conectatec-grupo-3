# DOC-01: Guía de Interpretación de Luces LED en ONT Huawei EchoLife

**Categoría:** Equipos de Cliente / ONT  
**Fabricante / Origen:** Huawei Technologies Co., Ltd. / Carrier Support  
**Versión / Vigencia:** v3.2 - Octubre 2026  

## Descripción General
Diagnóstico de conectividad y averías mediante la lectura del panel frontal de LEDs en terminales de red óptica (ONT) Huawei HG8245H, HG8546M y serie EchoLife.

## Procedimiento Operativo Paso a Paso
### Paso 1: Identificación de LED POWER
Verifique que el indicador POWER permanezca encendido en color verde fijo. Si el LED está apagado, revise la conexión del adaptador de corriente de 12V / 1.5A a la toma de pared.

### Paso 2: Diagnóstico de LED PON y LOS (Enlace Óptico)
El LED PON en verde fijo indica enlace sincronizado con la OLT. Si el LED LOS parpadea en color rojo, existe rotura de fibra o potencia óptica inferior a -27 dBm. Proceda a verificar la curvatura de la fibra.

### Paso 3: Verificación de LED LAN (Conexión Cableada)
Los puertos LAN1 a LAN4 deben mostrar luz verde fija o intermitente al conectar un cable de red UTP hacia la PC o router secundario. Si no enciende, cambie de puerto o sustituya el cable de red.

### Paso 4: Estado de LED WLAN e Internet
El LED WLAN en verde intermitente confirma la emisión de radiofrecuencia inalámbrica 2.4 GHz. Si el LED Internet está rojo, el equipo no obtiene IP pública por falla de autenticación PPPoE.

### Paso 5: Protocolo de Escalamiento
Si el LED LOS continúa rojo tras reiniciar el equipo durante 10 segundos, no manipule el conector azul SC/APC y escale a soporte técnico para visita de cuadrilla por corte de fibra.

## Matriz de Diagnóstico Rápido

| LED | Color / Estado | Significado Operativo | Acción Recomendada |
| --- | --- | --- | --- |
| POWER | Verde Fijo | Alimentación eléctrica correcta | Ninguna acción requerida. |
| PON | Verde Fijo | ONT autenticada y registrada en OLT | Servicio sincronizado. |
| LOS | Rojo Parpadeante | Pérdida de señal óptica (< -27 dBm) | Revisar curvatura; escalar a cuadrilla. |
| LAN 1-4 | Verde Intermitente | Tráfico de datos activo en puerto | Conexión local operativa. |
| WLAN | Verde Intermitente | Transmisión Wi-Fi activa | Red inalámbrica disponible. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
