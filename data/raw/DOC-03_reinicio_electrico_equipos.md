# DOC-03: Protocolo de Verificación y Reinicio Eléctrico de Routers y ONT

**Categoría:** Soporte Nivel 1 / Procedimientos  
**Fabricante / Origen:** ConectaTec ISP / Dirección de Operaciones de Red  
**Versión / Vigencia:** v4.0 - Octubre 2026  

## Descripción General
Procedimiento estándar para la purga de memoria volátil, resolución de microbloqueos de firmware y restablecimiento seguro de sesión de red en equipos terminales.

## Procedimiento Operativo Paso a Paso
### Paso 1: Verificación previa del estado de los cables
Antes de desconectar la energía, confirme que el cable amarillo de fibra óptica no esté tirante ni doblado en ángulo menor a 90 grados. No toque la punta del conector óptico.

### Paso 2: Desconexión segura del adaptador eléctrico
Retire el conector cilíndrico de poder de la parte trasera de la ONT o router, o desconecte el transformador de la toma de pared.

### Paso 3: Período de reposo de condensadores (Regla de los 30 segundos)
Espere exactamente 30 segundos continuos con el equipo desconectado. Este lapso descarga los condensadores y vacía la tabla ARP y la memoria RAM del equipo.

### Paso 4: Reconexión y secuencia de arranque
Vuelva a conectar el adaptador de corriente. Espere entre 90 y 120 segundos mientras el procesador carga el firmware y negocia la sincronización PON.

### Paso 5: Comprobación de navegación
Una vez que los LEDs Power, PON y WLAN estén fijos, verifique la navegación abriendo un navegador en modo incógnito hacia un sitio externo.

## Matriz de Diagnóstico Rápido

| Fase | Tiempo Estimado | Comportamiento Esperado | Criterio de Validación |
| --- | --- | --- | --- |
| Desconexión | 30 segundos | Todos los LEDs apagados | Descarga total de energía residual. |
| Secuencia Boot | 60 segundos | Parpadeo secuencial de LEDs | Carga de firmware y tablas locales. |
| Sincronización | 45 segundos | LED PON fijo verde | Autenticación correcta en OLT. |
| Prueba WAN | 15 segundos | Ping exitoso a 8.8.8.8 | Servicio de navegación restablecido. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
