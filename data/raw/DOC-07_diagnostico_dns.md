# DOC-07: Diagnóstico y Depuración de Resolución de Nombres de Dominio (DNS)

**Categoría:** Redes IP / Configuración  
**Fabricante / Origen:** IETF RFC 1035 / ConectaTec Network Engineering  
**Versión / Vigencia:** v2.2 - Octubre 2026  

## Descripción General
Detección y solución del síntoma 'Conectado sin acceso a Internet' originado por fallos de caché local de DNS o servidores de resolución no disponibles.

## Procedimiento Operativo Paso a Paso
### Paso 1: Identificación del síntoma de fallo DNS
El síntoma clásico ocurre cuando aplicaciones como WhatsApp o Telegram funcionan (conectan por IP), pero los navegadores muestran 'No se puede acceder a este sitio' (ERR_NAME_NOT_RESOLVED).

### Paso 2: Ejecución de ping por dirección IP directa
Abra la consola de comandos (`cmd`) y ejecute: `ping 8.8.8.8`. Si hay respuesta pero `ping google.com` falla, el problema es 100% de resolución DNS.

### Paso 3: Purga de caché local de resolución DNS
En la consola de comandos de Windows ejecute el comando: `ipconfig /flushdns` y presione Enter. El sistema confirmará que se vació la caché correctamente.

### Paso 4: Configuración manual de servidores DNS públicos
En las propiedades del protocolo TCP/IPv4 de su adaptador, asigne manualmente: Servidor DNS preferido: 8.8.8.8 y Servidor DNS alternativo: 1.1.1.1.

### Paso 5: Validación final con comando nslookup
Ejecute en la consola: `nslookup conectatec.ec` para comprobar que la resolución retorne la dirección IP pública correcta en menos de 30 ms.

## Matriz de Diagnóstico Rápido

| Servidor DNS | IP Primaria | IP Secundaria | Ventaja Operativa |
| --- | --- | --- | --- |
| ConectaTec Primario | 190.15.10.2 | 190.15.10.3 | Menor latencia nacional por ruta directa. |
| Google Public DNS | 8.8.8.8 | 8.8.4.4 | Alta disponibilidad global y estabilidad. |
| Cloudflare 1.1.1.1 | 1.1.1.1 | 1.0.0.1 | Máxima velocidad de resolución y privacidad. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
