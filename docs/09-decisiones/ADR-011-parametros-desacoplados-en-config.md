# ADR-011: Parámetros de Negocio Desacoplados en config/ (Tarifas, Umbrales, Salario Básico y Calendarios)
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  
**Docente Evaluador:** Heyler Fabio Guaza (Ing. Informático · Mg. en Ciberseguridad · OPD · Abogado)  
**Proyecto:** ConectaTec / TecnoAula — Triaje de Incidentes Técnicos (Caso N.º 03 · Grupo 3 UNIANDES)  

---

## 1. Contexto y Problema
En el despliegue de sistemas inteligentes para soporte técnico de ISP e instituciones educativas, confluyen normativas laborales, regulatorias y comerciales:
1. **Salario Básico Unificado (SBU):** En Ecuador, el SBU es decretado anualmente por el Ministerio del Trabajo ($482.00 USD para 2026) y sirve de base legal para cuantificar sanciones contractuales por indisponibilidad de servicio o incumplimiento de Acuerdos de Nivel de Servicio (SLA).
2. **Tarifario de Equipamiento y Mano de Obra:** Los costos de reposición de terminales de red (ONT GPON Wi-Fi 6, routers Mesh, cordones de fibra SC/APC, cable drop monomodo) y las tarifas de hora técnica presencial están sujetos a fluctuaciones comerciales y aprobaciones de ARCOTEL.
3. **Calendario y Turnos de Soporte:** La Ley de Feriados del Ecuador y el Código del Trabajo fijan descansos obligatorios que suspenden el cómputo de horas hábiles para incidentes ordinarios (P2, P3, P4), mientras que las averías críticas (P1 masivos) se atienden en guardia ininterrumpida 24/7 los 365 días del año.
4. **Umbrales Operativos de IA:** Los umbrales de confianza para clasificación automática (0.85), corte de similitud vectorial (0.70) y topes de iteración de agentes (6) requieren calibración continua.

**El Riesgo de Diseño:** Si estos parámetros se quemaran como números fijos en el código Python (`hardcoded`) o dentro de las instrucciones de los *prompts* del LLM:
* Cualquier cambio ministerial o comercial forzaría modificar código, redesplegar la aplicación y reescribir prompts.
* Se invalidaría el *Context Caching* de la API de Gemini (que exige prefijos fijos idénticos $\ge 4.096$ tokens).
* Se expondría al sistema a alucinaciones de precios o manipulación mediante inyecciones de prompt (OWASP LLM01 / LLM06).

---

## 2. Decisión de Arquitectura
Adoptar el principio extendido:
> ***«El modelo propone, el código dispone, la configuración gobierna.»***

Se desacoplan **taxativamente** todos los valores cuantitativos y calendarios fuera del código y fuera de los prompts, ubicándolos en el directorio `config/`:

| Archivo de Configuración | Tipo | Parámetros que Gobierna |
| :--- | :---: | :--- |
| `config/parametros.yaml` | YAML | Umbral de confianza (0.85), límite ReAct (6), corte RAG (0.70), Salario Básico Unificado ($482.00 USD), % penalización SLA por hora (2%), rate limiting (10 req / 6s). |
| `config/tarifas.json` | JSON | Tarifario de equipos CPE (ONT $45, Router Mesh $38.50), materiales de planta externa (drop $0.45/m, UTP $0.65/m), mano de obra ($15/h hábil, $22.50/h extra, fusión $8). |
| `config/calendario.json` | JSON | Zona horaria (`America/Guayaquil`), turnos ordinarios (Lunes-Viernes 08:00-18:00, Sábados 08:00-13:00), turnos NOC 24/7, y 11 feriados nacionales de Ecuador 2026. |
| `config/matriz_prioridad.json` | JSON | Matriz ITIL v4 de Impacto x Urgencia y minutos SLA contractuales (15m, 60m, 240m, 480m). |

### 2.1. Reglas Inviolables
1. **Nunca en el Prompt:** Ningún prompt del catálogo (`app/prompts/`) contiene cifras en dólares ni salarios básicos ni horas fijas quemadas. El LLM solo analiza síntomas, impacto y urgencia; jamás calcula precios ni presupuestos.
2. **Nunca en el Código:** Ninguna función de cálculo matemático posee números mágicos de precios o salarios. Todas leen dinámicamente mediante `app/tools/configuracion.py`.
3. **Herramientas Deterministas del Agente:** El agente de alcance controlado dispone de las herramientas `consultar_tarifas_repuestos` y `consultar_calendario_soporte`, con esquemas Pydantic V2 (`extra="forbid"`) y ejecución puramente algorítmica (0 tokens consumidos).

---

## 3. Justificación Técnica y Beneficios

1. **Mantenibilidad y Resiliencia Legal:**
   Si el Ministerio del Trabajo actualiza el Salario Básico Unificado o si se aprueba un nuevo feriado nacional, el operador solo edita `config/parametros.yaml` o `config/calendario.json`. El cambio entra en vigencia de inmediato sin recompilar ni alterar una sola línea de código Python.
2. **Cero Alucinaciones en Presupuestos y Multas:**
   El cálculo de presupuestos de reparación y penalidades por demora de cuadrilla es 100% aritmético (multiplicación y suma de ítems con IVA del 15% según ley ecuatoriana). Cero tokens gastados, cero variabilidad estocástica.
3. **Mitigación OWASP LLM01 y LLM06:**
   Un usuario malicioso que intente convencer al asistente mediante inyección de prompt de que "un reemplazo de ONT cuesta $0.01" o que "hoy es feriado" es neutralizado porque el LLM no tiene autoridad para decidir tarifas ni calendarios.
4. **Cumplimiento del Context Caching de Gemini:**
   Los prompts permanecen inmutables y compactos, permitiendo que la API de Google Gemini reutilice el prefijo en caché con -75% de costo y -50% de latencia.

---

## 4. Consecuencias
- **Positivas:**
  - Desacoplamiento total verificado mediante pruebas unitarias automatizadas.
  - Auditoría transparente de los orígenes de cada cálculo (`config/tarifas.json`, `config/parametros.yaml`, `config/calendario.json`).
  - Cumplimiento integral del criterio de rúbrica del Seminario de Titulación UNIANDES.
- **Negativas:**
  - Requiere validar la sintaxis de los archivos JSON/YAML al inicio de la aplicación para prevenir fallos por formato incorrecto. Mitigado mediante validadores y valores de contingencia con advertencias en log.

