# ADR-002: Gateway de Resiliencia con Failover Transparente Gemini a Groq
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
Las APIs de modelos de lenguaje en la nube sufren problemas de saturación, cuotas de peticiones por minuto (`HTTP 429`) y caídas de servicio (`HTTP 503`). Durante la defensa ante el tribunal o en producción, una falla de este tipo colapsaría el triaje.

## Decisión
Implementar un **Gateway de Resiliencia con Failover y Transparencia Operativa**:
- **Modelo Primario:** Google Gemini 1.5 Flash (ventana amplia y context caching).
- **Modelo de Respaldo:** Groq Cloud Llama 3.3 70B (latencia ultra baja y alta disponibilidad).
- **Fallback Local:** Clasificador heurístico por reglas si no hay internet.

## Justificación
1. **Disponibilidad Continua (99.9%):** Si Gemini devuelve 429, 503 o excede el timeout de 15 segundos, Groq atiende la solicitud en menos de 500 ms.
2. **Transparencia Operativa:** El contrato y la interfaz web muestran claramente si la solicitud fue conmutada (`conmutado: true`), reportando el motivo del fallo.
3. **Costo Cero en Contingencia:** Ambos modelos operan dentro de niveles gratuitos y optimizados.

## Consecuencias
- Mayor complejidad en el servicio de IA (`app/services/llm.py`), compensada con total robustez operativa durante la evaluación.
