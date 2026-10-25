# DOC-11: Protocolo de Configuración de Router Neutro o Repetidor en Modo Puente

**Categoría:** Enrutamiento / Arquitectura Cliente  
**Fabricante / Origen:** MikroTik RouterOS / Guía de Instalación ConectaTec  
**Versión / Vigencia:** v2.6 - Octubre 2026  

## Descripción General
Procedimiento para evitar problemas de Doble NAT (NAT Loopback) y conflictos de direcciones IP al conectar routers secundarios o repetidores Wi-Fi del cliente.

## Procedimiento Operativo Paso a Paso
### Paso 1: Identificación del problema de Doble NAT
Ocurre cuando el cliente conecta el puerto WAN de su router propio al puerto LAN de la ONT sin configurar modo puente, creando dos redes IP diferentes y bloqueando cámaras y juegos online.

### Paso 2: Desactivación del servidor DHCP en el equipo secundario
Acceda a la configuración del router secundario del cliente y desactive completamente la función 'DHCP Server' para que la ONT ConectaTec sea la única que entregue IPs.

### Paso 3: Modificación de la IP de gestión local
Cambie la dirección IP LAN del router secundario a una IP libre dentro del segmento de la ONT, por ejemplo: 192.168.1.254, para evitar conflicto con la 192.168.1.1.

### Paso 4: Conexión física por puerto LAN a LAN
Desconecte el cable del puerto azul (WAN/Internet) del router secundario y conéctelo en uno de sus puertos amarillos (LAN). Conecte el otro extremo a la ONT.

### Paso 5: Verificación de difusión Wi-Fi unificada
Configure el mismo nombre de red (SSID) y contraseña en ambos equipos para permitir itinerancia (roaming) transparente de los usuarios por todo el inmueble.

## Matriz de Diagnóstico Rápido

| Configuración | Modo Router Típico (Incorrecto) | Modo Access Point / Bridge (Correcto) |
| --- | --- | --- |
| Servidor DHCP | Activo en ambos equipos (Conflicto IP) | Activo solo en la ONT ConectaTec. |
| Segmento de Red | Dos redes separadas (Doble NAT) | Una sola red unificada (/24). |
| Puerto Utilizado | Cable en puerto WAN del router secundario | Cable en puerto LAN del router secundario. |
| Visibilidad de Dispositivos | Dispositivos aislados no se pueden compartir | Impresoras y carpetas visibles en toda la red. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
