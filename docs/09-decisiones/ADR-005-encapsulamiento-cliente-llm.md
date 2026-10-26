# ADR-005: Encapsulamiento del Cliente LLM y Desacoplamiento de Endpoints
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
Si los controladores de FastAPI importaran directamente los SDKs de Google (`google.generativeai`) o Groq (`groq`), cualquier cambio de proveedor, versión o ajuste de parámetros obligaría a reescribir y recompilar los endpoints HTTP.

## Decisión
Encapsular toda la lógica de inferencia, autenticación, manejo de reintentos y conversión de esquemas dentro de la clase `ClienteLLM` en `app/services/llm.py`, aplicando los patrones **Gateway** y **Strategy**.

## Justificación
1. **Invarianza de Endpoints:** Los routers solo conocen métodos de alto nivel (`clasificar()`, `chat_stream()`, `analizar()`).
2. **Conmutación en Caliente:** El proveedor puede cambiarse mediante variable de entorno (`PROVEEDOR_LLM_ACTIVO`) o en tiempo de ejecución con `cambiar_proveedor()`.
3. **Centralización de Políticas:** Las reglas de timeout, cuota y formateo residen en un único punto del sistema.

## Consecuencias
- Los endpoints HTTP se mantienen limpios, enfocados únicamente en la validación HTTP y orquestación de servicios.
