# ADR-003: Cálculo Determinista de Prioridad ITIL y Tiempos SLA
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
En gestión de servicios de TI (ITIL v4), los acuerdos de nivel de servicio (SLA) y la prioridad de despacho tienen implicaciones contractuales y financieras. Confiar este cálculo a la generación estocástica de un LLM provocaría inconsistencias y alucinaciones.

## Decisión
Separar taxativamente las responsabilidades:
1. **El LLM propone:** Extrae del lenguaje natural únicamente el nivel de `Impacto` (Alto/Medio/Bajo) y `Urgencia` (Alta/Media/Baja).
2. **El Código dispone:** Una función pura en Python (`app/tools/priorizar.py`) lee la matriz oficial en `config/matriz_prioridad.json` y calcula la Prioridad y los minutos SLA de forma 100% matemática.

## Justificación
1. **Cero Alucinaciones:** Garantiza que un corte masivo siempre reciba Prioridad Alta y 2 horas SLA.
2. **Ahorro de Tokens:** El cálculo matemático no consume tokens ni añade latencia de inferencia.
3. **Mantenibilidad:** Si los SLAs cambian, solo se edita el archivo JSON sin reentrenar ni reescribir prompts.

## Consecuencias
- Cumplimiento estricto del principio de arquitectura: *«El modelo propone, el código dispone»*.
