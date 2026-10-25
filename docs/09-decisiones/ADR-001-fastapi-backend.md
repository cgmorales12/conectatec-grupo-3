# ADR-001: Selección de FastAPI como Framework de Backend
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
El sistema ConectaTec requiere exponer una API REST segura, modular y de alto rendimiento para recibir solicitudes de soporte, comunicarse con modelos generativos (Gemini/Groq) y servir datos al tablero Kanban.

## Decisión
Seleccionar **FastAPI** (Python 3.10+) junto a Uvicorn y Pydantic V2 como la infraestructura del perímetro de backend.

## Justificación
1. **Validación Estricta:** Integración con Pydantic V2 (`extra="forbid"`) para blindar el sistema contra inyecciones de campos en el payload.
2. **Concurrencia con AnyIO:** Permite definir endpoints de inferencia con `def` delegados automáticamente al pool de 40 hilos de AnyIO, evitando que una llamada lenta al modelo bloquee a otros usuarios.
3. **Documentación Automática:** Generación instantánea de especificaciones OpenAPI y Swagger UI en `/docs`.
4. **Respuestas de Error Uniformes:** Facilidad para implementar manejadores de errores bajo el estándar RFC 9457 (`application/problem+json`).

## Consecuencias
- Desacoplamiento total entre frontend y lógica de negocio.
- Los clientes web y móviles consumen contratos tipados y estables.
