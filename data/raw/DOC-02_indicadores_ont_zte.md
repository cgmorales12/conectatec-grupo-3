# DOC-02: Manual de Diagnóstico de Indicadores Lumínicos en ONT ZTE F660/F670

**Categoría:** Equipos de Cliente / ONT  
**Fabricante / Origen:** ZTE Corporation / Global Technical Support  
**Versión / Vigencia:** v2.8 - Octubre 2026  

## Descripción General
Manual de resolución de problemas de capa física y enlace GPON para equipos ONT ZTE modelos F660 (Mono-banda) y F670 (Doble banda AC1200).

## Procedimiento Operativo Paso a Paso
### Paso 1: Verificación del Indicador Power
Compruebe que el LED Power esté verde continuo. En caso de parpadeo rojo, indica sobretensión o fallo interno del circuito de alimentación de la ONT.

### Paso 2: Comprobación del Indicador PON
El LED PON debe permanecer verde sin intermitencia. Si parpadea lentamente (1 Hz), la ONT está en proceso de descubrimiento y registro con la OLT.

### Paso 3: Alarma de Indicador LOS
El LED LOS apagado indica potencia óptica dentro del umbral normal (-8 dBm a -25 dBm). Si se enciende en rojo permanente, la fibra está desconectada o quebrada.

### Paso 4: Indicadores Wi-Fi 2.4G y 5G
En el modelo ZTE F670, ambos indicadores deben titilar rápidamente cuando hay intercambio de paquetes con dispositivos conectados.

### Paso 5: Pruebas de Puerto Telefónico (POTS / TEL)
Si el cliente reporta fallo de telefonía fija VoIP, el LED Phone/POTS debe estar verde fijo. Si parpadea, indica descolgado o fallo de registro SIP.

## Matriz de Diagnóstico Rápido

| Indicador | Patrón de Luz | Estado del Enlace | Diagnóstico Técnico |
| --- | --- | --- | --- |
| Power | Verde Continuo | Normal | Alimentación de 12V DC correcta. |
| PON | Verde Continuo | Enlace Sincronizado | Sesión GPON activa con cabecera. |
| LOS | Rojo Fijo | Sin Señal Óptica | Acometida cortada o conector sucio. |
| Internet | Verde Titilante | Tráfico WAN Activo | Navegación habilitada en red. |
| WLAN | Verde Titilante | Radio Wi-Fi Activa | Redes 2.4G / 5G transmitiendo. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
