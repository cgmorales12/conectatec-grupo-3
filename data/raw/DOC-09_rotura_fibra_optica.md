# DOC-09: Criterios de Escalamiento por Atenuación y Rotura de Acometida de Fibra Óptica

**Categoría:** Red Óptica / Escalamiento Campo  
**Fabricante / Origen:** ITU-T G.984 GPON / ConectaTec Planta Externa  
**Versión / Vigencia:** v3.5 - Octubre 2026  

## Descripción General
Protocolo para determinar cuándo una incidencia no es solucionable de forma remota y debe escalarse con prioridad Alta para despacho de cuadrilla con fusionadora óptica.

## Procedimiento Operativo Paso a Paso
### Paso 1: Detección de alarma óptica crítica
Si la ONT presenta el LED LOS en rojo permanente o parpadeante, y la potencia reportada por telemetría OLT es '-Infinity dBm', existe corte físico de la fibra.

### Paso 2: Inspección de la roseta óptica interior
Solicite al usuario verificar si el cable fino negro o amarillo que va desde la roseta de pared hasta la ONT fue mordido por mascotas, aplastado por muebles o desconectado.

### Paso 3: Consulta en sistema de monitoreo OLT
El operador del NOC verifica si el corte afecta a una sola ONT (rotura de acometida individual) o si afecta a varias ONTs del mismo puerto PON (rotura de cable troncal / NAP dañada).

### Paso 4: Registro y escalamiento en tablero de tickets
Si la rotura es confirmada, genere un ticket con Categoría 'Fibra Óptica', Impacto 'Medio' (o 'Alto' si es empresa), Urgencia 'Alta' y Prioridad 'Alta'.

### Paso 5: Asignación de cuadrilla de planta externa
Despache la orden de trabajo al técnico de cuadrilla con el metraje estimado y ubicación geográfica del divisor óptico (Splitter) correspondiente.

## Matriz de Diagnóstico Rápido

| Potencia Óptica (Rx) | Estado del Enlace | Nivel de Servicio | Acción Operativa |
| --- | --- | --- | --- |
| -15 a -24 dBm | Óptimo | 100% Calidad | Operación normal de enlace. |
| -25 a -27 dBm | Marginal | Degradación / Alerta | Programar mantenimiento preventivo. |
| Menor a -28 dBm | Crítico | Microcortes frecuentes | Escalar ticket a cuadrilla por atenuación. |
| -Infinity (LOS Rojo) | Corte Total | Sin Enlace Óptico | Escalamiento inmediato: cuadrilla de campo. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
