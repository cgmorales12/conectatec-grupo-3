# ADR-008: Manejo Resiliente de Errores de Proveedor (HTTP 429, Timeout y Respuesta Vacía)
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
Las llamadas a APIs de LLM pueden experimentar rechazos por saturación de cuota (HTTP 429), cuelgues de red que no retornan en minutos, o respuestas vacías producto de bloqueos de seguridad del proveedor.

## Decisión
Implementar un mecanismo de contención tripartito en `ClienteLLM`:
1. **Espera Exponencial ante HTTP 429:** Reintentos con intervalos calculados por $\text{Espera} = 0.5\text{s} \times 2^{\text{intento}}$ (0.5s, 1.0s, 2.0s).
2. **Control de Timeout:** Interrupción tajante si la llamada excede los 12.0 segundos, conmutando de inmediato al modelo secundario.
3. **Validación de Contenido Vacío:** Intercepción de respuestas `None`, cadenas vacías o bloqueos de seguridad (`ErrorRespuestaVaciaLLM`), activando la conmutación a Groq o al clasificador local determinista.

## Justificación
1. **Resistencia ante Saturación:** Absorbe fluctuaciones transitorias de cuota sin fallar de cara al usuario.
2. **Experiencia de Usuario Fluida:** El usuario nunca queda bloqueado indefinidamente ante una caída de Gemini.

## Consecuencias
- El sistema mantiene su disponibilidad incluso bajo condiciones de caos de red o límites de cuota alcanzados.
