# ADR-006: Versionado e Ingeniería de Prompts con Directivas de Abstención
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
Los modelos generativos tienden a inventar procedimientos técnicos inexistentes cuando el usuario consulta por temas fuera de alcance, lo cual puede provocar daños en equipos o configuraciones erróneas.

## Decisión
1. Mantener tres versiones formales de prompts (`system_v1.md`, `system_v2.md`, `system_v3.md`) en `app/prompts/`.
2. Implementar una **directiva estricta de abstención**: el prompt ordena taxativamente responder con `"requiere_revision_humana": true` y abstenerse de formular diagnósticos si la solicitud no pertenece al ámbito del ISP o carece de información suficiente.
3. Aislar los datos del usuario mediante delimitadores semánticos XML (`<solicitud>{texto}</solicitud>`).

## Justificación
1. **Mitigación de Alucinaciones:** Evaluación comparativa en `docs/05-prompts.md` demostró 100% de precisión y cero invenciones en la versión 3.
2. **Protección contra Inyección de Prompts (OWASP LLM01):** La delimitación XML previene que instrucciones del usuario secuestren el comportamiento del sistema.

## Consecuencias
- Mayor seguridad operativa y consistencia en los contratos de salida JSON.
