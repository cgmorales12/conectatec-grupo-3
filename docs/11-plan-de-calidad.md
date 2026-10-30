# Plan de Calidad y Evaluación Automatizada (Entrega 3)

**Proyecto:** ConectaTec / TecnoAula — Triaje y Resolución Inteligente de Incidencias Técnicas  
**Caso Asignado:** Caso N.º 03 (Mesa de Ayuda para Instituciones Educativas e ISP)  
**Grupo de Desarrollo N.º 03:**  
* **Christian Guillermo Morales González** (Tech Lead / Coordinador — GitHub: `cgmorales12`)  
* **Luis Fernando Ribera Alajo** (Builder / Arquitectura — GitHub: `fernandolribera`)  
* **Amalia Geoconda Iguasnia Escobar** (QA / Seguridad y Requerimientos — GitHub: `Geocoiguasnia76`)  
**Docente Evaluador:** Heyler Fabio Guaza  
**Fecha:** 29 de octubre de 2026 (Semana 3 · Clase 4)  

---

## 1. Evaluación Básica del RAG

La base de conocimiento oficial se compone de 15 manuales técnicos en `data/raw/` indexados de forma reproducible en ChromaDB mediante `scripts/ingest.py`.

| Métrica | Cómo se Mide | Meta | Resultado Obtenido |
| :--- | :--- | :---: | :---: |
| **Acierto de Recuperación (`hit@5`)** | La fuente correcta (`DOC-01` a `DOC-15`) aparece entre los primeros 5 resultados recuperados sobre el banco de 20 preguntas en `eval/preguntas.json`. | $\ge 85\%$ | **100.0%** ✅ |
| **Fidelidad y Citas Verificables** | Respuestas que citan el ID del manual y el paso operativo exacto (`DOC-XX: Paso Y`). | $\ge 90\%$ | **100.0%** ✅ |
| **Silencio y Abstención Correcta** | Preguntas fuera de alcance (no técnicas o de materias ajenas) donde el sistema se abstiene deterministamente de alucinar. | $100\%$ | **100.0%** ✅ |

---

## 2. Evaluación Básica del Agente de Alcance Controlado

El agente opera bajo el patrón ReAct gobernado por código backend determinista.

* **Escenarios Evaluados:**
  1. *Camino Feliz (A):* Diagnóstico técnico guiado y resolución de primer nivel con citas del manual.
  2. *Fuera de Alcance (B):* Solicitud no técnica rechazada deterministamente.
  3. *Tope de Iteraciones (C):* Corte forzoso al alcanzar `MAX_ITER = 6`, respondiendo HTTP 200 con `requiere_revision_humana: true`.
  4. *Inyección en Documento (D):* Intento de manipulación (*Goal Hijacking*) bloqueado por esquemas Pydantic y delimitadores XML.
* **Metas de Cumplimiento:**
  * Meta de tareas cumplidas: $\ge 90\%$.
  * Rechazos correctos ante herramientas prohibidas (`eliminar_ticket`): **100%**.

---

## 3. Evaluación del Flujo Automatizado (La Cinta)

Evaluado sobre el **conjunto dorado de 20 casos** en [`eval/casos_flujo.jsonl`](../eval/casos_flujo.jsonl) ejecutado mediante [`eval/evaluar.py`](../eval/evaluar.py):

* **Umbral de Confianza:** $0.85$ (calibrado en [`config/parametros.yaml`](../config/parametros.yaml)).
* **Casos Automáticos:** $45.0\%$ (resolución inmediata con reglas deterministas).
* **Casos a Revisión Asistida:** $40.0\%$ (incidencias críticas P1, fallas físicas de fibra y casos dudosos con trabajo prellenado).
* **Consultas Derivadas a RAG:** $15.0\%$.
* **Errores Silenciosos Permitidos:** **0 (CERO ESTRICTO, no negociable)**. Resultado obtenido: **0 errores silenciosos**.

---

## 4. Calidad de Ingeniería de Software

| Práctica de Calidad | Herramienta / Estándar | Estado en el Proyecto |
| :--- | :--- | :---: |
| **Pruebas Unitarias Automatizadas** | `pytest tests/` con mocks aislados (0 costo de API) | ✅ 28/28 pruebas pasando |
| **Esquemas Estrictos de Entrada/Salida** | Pydantic V2 con `extra="forbid"` | ✅ 100% implementado |
| **Análisis de Vulnerabilidades (SAST)** | `bandit -r app/` | ✅ Aprobado |
| **Auditoría de Cero Secretos en Git** | `python scripts/auditar_cero_secretos.py` | ✅ Cero fugas (.env en .gitignore) |
| **Evaluación Continua en CI** | `python eval/evaluar.py` en GitHub Actions | ✅ Integrado |

---

## 5. Comandos de Verificación para el Evaluador

```bash
# 1. Ingesta y vectorización reproducible en ChromaDB
python scripts/ingest.py

# 2. Evaluación de calidad (RAG + Flujo automatizado)
python eval/evaluar.py

# 3. Suite completa de 28 pruebas unitarias
pytest -v tests/
```
