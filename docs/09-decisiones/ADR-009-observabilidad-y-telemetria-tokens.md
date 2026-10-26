# ADR-009: Observabilidad, Telemetría y Contabilidad de Tokens por Solicitud
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
El uso de modelos de lenguaje en producción exige visibilidad total sobre los costos operativos (FinOps de IA), el volumen de tokens consumidos y las latencias de respuesta para detectar cuellos de botella y optimizar prompts.

## Decisión
1. Medir y registrar en logs estructurados los **tokens de entrada, tokens de salida, tokens totales y el tiempo de respuesta en milisegundos** por cada solicitud de inferencia.
2. Exponer el endpoint de telemetría `GET /v1/metricas/solicitudes` con métricas agregadas (promedios, máximos y distribución por proveedor).
3. Mostrar en la interfaz web (Frontend) un distintivo visual (*Badge*) en tiempo real indicando los tokens consumidos y la latencia exacta de cada operación.

## Justificación
1. **Transparencia Financiera y Operativa:** Permite auditar el ahorro de tokens logrado mediante la ingeniería de prompts y context caching.
2. **Supervisión Continua:** Los operadores visualizan de inmediato qué solicitudes demandan mayor tiempo de procesamiento.

## Consecuencias
- Trazabilidad y auditoría completas sin penalizar el rendimiento del backend.
