# DOC-08: Verificación de Cableado de Red de Cobre (UTP Categoría 5e / 6)

**Categoría:** Infraestructura Física / Cableado  
**Fabricante / Origen:** TIA/EIA-568-C.2 / ConectaTec Infraestructura  
**Versión / Vigencia:** v2.0 - Octubre 2026  

## Descripción General
Identificación de degradación de velocidad a 100 Mbps (Fast Ethernet) provocada por daños en pines de conectores RJ-45, dobleces o cables UTP de categoría deficiente.

## Procedimiento Operativo Paso a Paso
### Paso 1: Inspección visual del cable y conectores RJ-45
Examine los extremos del cable de red. La pestaña plástica de retención no debe estar rota y los 8 pines dorados deben estar alineados sin óxido.

### Paso 2: Comprobación de la categoría impresa en el forro
Verifique el texto impreso en el cable. Debe indicar 'UTP CAT.5E' (soporta hasta 1000 Mbps a corta distancia) o 'UTP CAT.6' (óptimo para Gigabit). Los cables Categoría 5 antigua solo dan 100 Mbps.

### Paso 3: Detección del síntoma de degradación a 100 Mbps
Si un cliente con plan de 200 Mbps o más solo recibe 94-95 Mbps en el test de velocidad, significa que uno de los 8 hilos del cable UTP está roto y el puerto conmutó a 100 Mbps.

### Paso 4: Prueba con cable de parcheo (Patch Cord) alternativo
Sustituya el cable sospechoso por un cable nuevo certificado Categoría 6 de 1 o 2 metros y repita la comprobación en el adaptador de red.

### Paso 5: Normas de crimpado estándar T568B
En caso de rehacer los conectores, verifique el código de colores oficial: Blanco-Naranja, Naranja, Blanco-Verde, Azul, Blanco-Azul, Verde, Blanco-Marrón, Marrón.

## Matriz de Diagnóstico Rápido

| Categoría UTP | Velocidad Máxima | Frecuencia | Uso Recomendado |
| --- | --- | --- | --- |
| Categoría 5 | 100 Mbps | 100 MHz | Obsoleto. Reemplazar de inmediato. |
| Categoría 5e | 1000 Mbps (1 Gbps) | 100 MHz | Mínimo aceptable para planes de hasta 300 Mbps. |
| Categoría 6 | 1000 Mbps / 10 Gbps | 250 MHz | Estándar oficial ConectaTec para todos los clientes. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
