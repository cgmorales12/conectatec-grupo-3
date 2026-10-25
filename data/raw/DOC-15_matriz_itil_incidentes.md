# DOC-15: Matriz ITIL de Clasificación de Incidentes, Impacto, Urgencia y SLA

**Categoría:** Gestión de Servicios TI / ITIL v4  
**Fabricante / Origen:** AXELOS ITIL v4 Foundation / ConectaTec Operations  
**Versión / Vigencia:** v5.0 - Octubre 2026  

## Descripción General
Matriz oficial determinista para la priorización matemática de solicitudes técnicas según el cruce de Impacto y Urgencia, con tiempos SLA vinculantes.

## Procedimiento Operativo Paso a Paso
### Paso 1: Determinación del Impacto Institucional
El impacto mide el alcance o daño del problema. Es Alto si afecta a empresas, instituciones educativas o zonas enteras; Medio si afecta a un hogar completo; Bajo si afecta a un solo equipo.

### Paso 2: Determinación de la Urgencia del Reporte
La urgencia mide la rapidez necesaria para actuar. Es Alta si hay corte total del servicio o evento crítico en curso; Media si hay lentitud o degradación; Baja si es una consulta informativa.

### Paso 3: Cruce matricial determinista en código Python
El sistema toma el Impacto y la Urgencia extraídos por el modelo y aplica la tabla determinista sin intervención estocástica de la IA para obtener la Prioridad.

### Paso 4: Asignación de tiempo máximo de resolución (SLA)
A cada prioridad se le asigna un tiempo máximo de atención: Prioridad Alta = 2 horas; Prioridad Media = 6 horas; Prioridad Baja = 24 horas.

### Paso 5: Monitoreo y alarma de vencimiento de SLA
El sistema supervisa los tiempos en el tablero Kanban. Si un ticket de Prioridad Alta no es atendido en 60 minutos, se emite una notificación de advertencia al supervisor.

## Matriz de Diagnóstico Rápido

| Impacto | Urgencia | Prioridad Resultante | Tiempo SLA Máximo | Nivel de Atención |
| --- | --- | --- | --- | --- |
| Alto (Zona/Empresa) | Alta (Corte Total) | ALTA | 2 Horas | Cuadrilla Inmediata / NOC Nivel 2 |
| Alto (Zona/Empresa) | Media (Lentitud) | MEDIA | 6 Horas | Optimización de Enlace |
| Alto (Zona/Empresa) | Baja (Consulta) | BAJA | 24 Horas | Mesa de Ayuda Nivel 1 |
| Medio (Hogar) | Alta (Corte Total) | ALTA | 4 Horas | Soporte Presencial Nivel 2 |
| Medio (Hogar) | Media (Lentitud) | MEDIA | 8 Horas | Soporte Remoto Nivel 1 |
| Bajo (1 Dispositivo) | Baja (Consulta) | BAJA | 24 Horas | Autoatención / Bot IA |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
