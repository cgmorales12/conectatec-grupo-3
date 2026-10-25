# DOC-13: Procedimiento ante Microcortes o Caídas Intermitentes de Sesión PPPoE

**Categoría:** Protocolos de Acceso / Diagnóstico ISP  
**Fabricante / Origen:** Broadband Forum TR-101 / ConectaTec Core Network  
**Versión / Vigencia:** v3.2 - Octubre 2026  

## Descripción General
Diagnóstico y resolución de fallos donde la luz óptica (PON) permanece verde pero la conexión se corta cada pocos minutos debido a desautenticación en el servidor BRAS.

## Procedimiento Operativo Paso a Paso
### Paso 1: Verificación de la estabilidad física de la fibra
Confirme en el sistema de telemetría de la OLT que la potencia óptica no fluctúe más de 2 dBm durante el día. Si la potencia es estable, la falla no es física.

### Paso 2: Consulta del registro de caídas en el servidor de autenticación (BRAS)
Revise el historial del cliente en el servidor RADIUS. Si aparecen mensajes 'Terminated: Lost-Carrier' o 'Admin-Reset', la sesión está siendo forzada a desconectar.

### Paso 3: Verificación de MTU / MRU en la configuración WAN
Asegúrese de que el parámetro MTU en la conexión PPPoE de la ONT esté configurado exactamente en 1492 bytes. Un MTU de 1500 causa fragmentación y microcortes.

### Paso 4: Comprobación de clonación de credenciales PPPoE
Verifique que el usuario PPPoE del cliente no esté activo simultáneamente en otra ONT de la red, lo que causaría desconexión cíclica continua.

### Paso 5: Reinicio de puerto lógico en OLT
Ejecute el comando de reinicio administrativo de la interfaz lógica GPON del cliente en la OLT para forzar una reasignación limpia de IP pública.

## Matriz de Diagnóstico Rápido

| Causa Posible | Código de Alerta en Registro | Impacto en el Usuario | Acción Correctiva |
| --- | --- | --- | --- |
| MTU Desajustado | Packet Fragmentation Needed | Páginas cargan a medias o lentas | Configurar MTU en 1492 bytes. |
| Fluctuación Óptica | Optical Loss of Margin | Microcortes cada 5 - 10 minutos | Limpiar conector SC/APC de fibra. |
| Conflicto de Usuario | Duplicate User Login Rejected | Corte total cada 2 minutos | Resetear contraseña PPPoE en RADIUS. |
| Reinicio de Firmware | System Uptime Reset | Equipo se apaga solo | Sustituir transformador de 12V dañado. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
