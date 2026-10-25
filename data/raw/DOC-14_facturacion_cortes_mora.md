# DOC-14: Guía de Consulta de Estado Comercial, Corte por Mora y Canales de Pago

**Categoría:** Atención al Cliente / Facturación  
**Fabricante / Origen:** ConectaTec ISP / Gerencia de Administración y Cobranzas  
**Versión / Vigencia:** v4.1 - Octubre 2026  

## Descripción General
Protocolo para identificar suspensiones comerciales del servicio por cuotas pendientes, diferenciar cortes técnicos de administrativos y orientar al cliente.

## Procedimiento Operativo Paso a Paso
### Paso 1: Identificación del estado de suspensión comercial
Cuando el servicio está suspendido por falta de pago, los LEDs de la ONT están normales (Power, PON y WLAN verdes), pero al navegar el usuario es redirigido al portal de cobros.

### Paso 2: Consulta en el sistema de facturación y CRM
El agente de mesa de ayuda o el bot inteligente consulta el número de cédula o código de abonado en la base de datos comercial para verificar deudas pendientes.

### Paso 3: Notificación de saldos y fecha de corte
Informe al cliente el valor pendiente de pago, la fecha límite que venció y las facturas acumuladas de forma clara y respetuosa según las leyes de defensa del consumidor.

### Paso 4: Canales de pago electrónico autorizados
Indique los canales habilitados para pago inmediato: transferencia bancaria a Banco Pichincha / Guayaquil, botón de pagos en web ConectaTec y puntos de pago externos.

### Paso 5: Reactivación automática del servicio
Una vez procesado el pago en el sistema bancario, el servidor de facturación emite la orden automática a la OLT y el servicio se restablece en un lapso máximo de 15 minutos.

## Matriz de Diagnóstico Rápido

| Estado en Sistema | Comportamiento del Navegador | Tipo de Bloqueo | Tiempo de Reactivación |
| --- | --- | --- | --- |
| Activo al Día | Navegación normal a toda velocidad | Sin bloqueo | Inmediato. |
| Suspendido por Mora | Redirección a portal de pagos institucional | Bloqueo comercial de tráfico | Máximo 15 minutos tras pagar. |
| Promesa de Pago | Navegación rehabilitada por 48 horas | Prórroga temporal | Automática al registrar promesa. |
| Cancelado Definitivo | Sin perfil en OLT / Retiro de equipo | Desinstalación física | Requiere nuevo contrato de servicio. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
