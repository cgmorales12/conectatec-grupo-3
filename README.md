# ConectaTec · Triaje Inteligente de Incidentes ISP
**Caso N.º 03 · Grupo 3 — Seminario de Titulación en Ingeniería de Software con IA Generativa**  
**Universidad Regional Autónoma de Los Andes (UNIANDES) — Octubre 2026**  
**Docente Evaluador:** Ing. Heyler Fabio Guaza  

---

## 👥 Integrantes del Grupo 3
1. **Christian Guillermo Morales González** (Tech Lead / Coordinador — GitHub: `cgmorales12`)
2. **Luis Fernando Ribera Alajo** (Builder / Arquitectura — GitHub: `fernandolribera`)
3. **Amalia Geoconda Iguasnia Escobar** (QA / Seguridad y Requerimientos — GitHub: `Geocoiguasnia76`)

---

## 🚀 1. Descripción del Proyecto y Problema Real
**ConectaTec** es una plataforma web inteligente diseñada para automatizar la recepción, diagnóstico de primer nivel y priorización de averías de telecomunicaciones para abonados y operadores de mesa de ayuda en proveedores de servicios de internet (ISP).

### Principio Rector de Arquitectura
> ***«El modelo propone, el código dispone.»***  
> El Modelo de Lenguaje (LLM) es probabilístico y falible. La extracción de impacto y urgencia se delega a la IA con validación estricta en esquemas Pydantic V2 (`extra="forbid"`), pero **la prioridad matemática y el tiempo máximo de resolución (SLA) los calcula de forma determinista una función pura en Python** leyendo `config/matriz_prioridad.json`. El LLM nunca calcula la prioridad ni inventa tiempos contractuales.

---

## 🛠️ 2. Arquitectura del MVP (Semana 2)

```text
CONECTATEC-MVP/
├── app/
│   ├── main.py              # Punto de entrada FastAPI, middleware Token Bucket y manejadores RFC 9457
│   ├── schemas.py           # Contratos DTO con Pydantic V2 (extra="forbid")
│   ├── database.py          # Repositorio SQLite parametrizado con consultas seguras '?'
│   ├── routers/
│   │   ├── tickets.py       # Endpoints de clasificación, listado y cambio de estados Kanban
│   │   ├── salud.py         # Diagnóstico operativo (/v1/salud)
│   │   ├── auth.py          # Autenticación y roles de personal técnico TIC
│   │   └── manuales.py      # Gestión documental de la base de conocimiento
│   ├── services/
│   │   ├── llm.py           # Gateway con failover: Gemini 1.5 Flash -> Groq Llama 3.3 -> Motor Local
│   │   ├── rag.py           # Búsqueda semántica con citas verificables (DOC-XX y paso exacto)
│   │   └── auth.py          # Control de acceso y tokens JWT
│   └── tools/
│       └── priorizar.py     # Cálculo determinista de prioridad ITIL (config/matriz_prioridad.json)
├── config/
│   └── matriz_prioridad.json# Matriz ITIL de Impacto x Urgencia y tiempos SLA
├── data/
│   ├── raw/                 # 15 manuales técnicos oficiales en formato Markdown (.md)
│   ├── pdf/                 # 15 manuales técnicos oficiales en formato PDF (.pdf)
│   └── conectatec.db        # Base de datos persistente SQLite
├── docs/                    # Documentación técnica, académica y evidencias
│   ├── 01-propuesta.md      # Propuesta formal del proyecto
│   ├── 02-requisitos.md     # Historias de usuario INVEST con Gherkin BDD
│   ├── 03-arquitectura.md   # Modelo C4 y diagramas Mermaid
│   ├── 04-fuentes.md        # Inventario de los 15 manuales técnicos oficiales
│   ├── 05-preguntas-frecuentes.md # Levantamiento de 15 casos reales de soporte
│   ├── 05-prompts.md        # Catálogo de prompts bajo método R.E.C.E.T.A.
│   ├── 06-manual-usuario.md # Manual de uso del sistema
│   ├── 07-manual-tecnico.md # Manual técnico y de despliegue
│   ├── 09-decisiones/       # Registros de Decisiones de Arquitectura (ADR-001 a 004)
│   ├── 10-perimetro-seguridad-y-defensas-llm.md # Auditoría OWASP LLM 2025 y LOPDP
│   └── evidencias/
│       ├── semana-1/        # Evidencias y decisiones de la Semana 1
│       └── semana-2/        # Evidencias, failover y pruebas unitarias de la Semana 2
├── frontend/
│   └── index.html           # Tablero Kanban interactivo, formulario y simulador en vivo
├── tests/
│   └── test_endpoints.py    # Suite de 12 pruebas unitarias con Mocks (100% offline)
├── .env.example             # Plantilla de variables de entorno con claves vacías
├── .gitignore               # Configuración estricta de exclusión de secretos y temporales
└── requirements.txt         # Dependencias fijadas por versión
```

---

## ⚡ 3. Instalación y Puesta en Marcha en Local

### 3.1. Requisitos Previos
- Python 3.10 o superior (verificado con Python 3.14).
- Git instalado.

### 3.2. Clonar el Repositorio
```bash
git clone https://github.com/cgmorales12/conectatec-mvp.git
cd conectatec-mvp
```

### 3.3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3.4. Configurar Variables de Entorno
Copiar la plantilla de entorno:
```bash
cp .env.example .env
```
*(Nota: Si no se configuran claves de API, el sistema activa automáticamente el conmutador heurístico local offline para pruebas 100% funcionales).*

### 3.5. Iniciar la Aplicación
```bash
uvicorn app.main:app --reload --port 8000
```

Acceso a servicios en el navegador:
- **Tablero Kanban Web:** [http://localhost:8000/tablero](http://localhost:8000/tablero)
- **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Diagnóstico Operativo:** [http://localhost:8000/v1/salud](http://localhost:8000/v1/salud)
- **Proveedor LLM Encapsulado:** [http://localhost:8000/v1/llm/proveedor](http://localhost:8000/v1/llm/proveedor)

### 3.6. Endpoints Principales del Sistema
- `POST /chat`: Endpoint conversacional interactivo con **Streaming en tiempo real** (`StreamingResponse` token a token).
- `POST /clasificar`: Inferencia técnica y triaje determinista retornando JSON validado con esquemas estrictos Pydantic V2.
- `POST /analizar`: Diagnóstico de averías y severidad estructurado con Pydantic V2 (`extra="forbid"`).
- `GET /v1/llm/proveedor`: Introspección del proveedor activo en el **Cliente LLM Encapsulado** (cambiar de proveedor no toca los endpoints).

---

## 🧩 4. Cliente LLM Encapsulado (`app/services/llm.py`)
> ***«El cliente del modelo está encapsulado: cambiar de proveedor no toca los endpoints.»***

La clase `ClienteLLM` centraliza toda la interacción con modelos de lenguaje externo (Google Gemini 1.5 Flash, Groq Cloud Llama 3.3 y conmutador determinista offline).
- **Desacoplamiento total:** Los endpoints consumen `cliente_llm.clasificar()`, `cliente_llm.chat_stream()` y `cliente_llm.analizar()`.
- **Conmutación transparente:** Cambiar de proveedor mediante `PROVEEDOR_LLM_ACTIVO=groq` en `.env` o `cliente_llm.cambiar_proveedor()` opera internamente sin alterar ningún endpoint de FastAPI ni sus contratos Pydantic.

---

## 🧪 5. Ejecución de Pruebas Automatizadas

El proyecto cuenta con una suite de **17 pruebas unitarias automatizadas con Mocks** que validan la priorización ITIL, la sanitización LOPDP, la conmutación por error, el streaming conversacional y el encapsulamiento del cliente LLM sin requerir conexión a internet ni gastar saldo de API:

```bash
python -m pytest tests/ -v
```

---

## 🛡️ 6. Ciberseguridad y Privacidad (OWASP LLM 2025 y LOPDP)
- **Anonimización previa de contraseñas (Art. 23 LOPDP):** Detección automática por Regex y reemplazo por `[CONFIDENCIAL_REMOVIDO]`.
- **Aislamiento semántico (OWASP LLM01):** Delimitación estricta de la entrada del usuario mediante etiquetas `<solicitud>...</solicitud>`.
- **Contratos Pydantic V2 cerrados (OWASP LLM05):** Parámetro `extra="forbid"` para neutralizar salidas maliciosas o inyecciones de campos.
- **Limitador de tasa Token Bucket (OWASP LLM04):** Capacidad de 15 fichas por IP con respuesta HTTP 429 (`Retry-After`) según RFC 6585.
- **Simulador de Caída de la IA y Ataque en vivo:** Demostración de contraste entre el Modo Vulnerable (sin defensas) y el Sistema Seguro ConectaTec.

---

## 📋 7. Estado de Cumplimiento de Entregables (Semanas 1 y 2)

| Fase | Entregable Oficial | Ubicación en el Repositorio | Estado |
| :---: | :--- | :--- | :---: |
| **Semana 1** | Propuesta del Proyecto | `docs/01-propuesta.md` | ✅ Completo |
| **Semana 1** | Ingeniería de Requisitos (8 HU + Gherkin) | `docs/02-requisitos.md` | ✅ Completo |
| **Semana 1** | Diseño de Arquitectura (C4 + Mermaid) | `docs/03-arquitectura.md` | ✅ Completo |
| **Semana 1** | Inventario del Corpus (15 Manuales) | `docs/04-fuentes.md` | ✅ Completo |
| **Semana 1** | Levantamiento Real (15 Casos de Estudio) | `docs/05-preguntas-frecuentes.md` | ✅ Completo |
| **Semana 1** | Evidencias y Práctica de Clase | `docs/evidencias/semana-1/README.md` | ✅ Completo |
| **Semana 2** | Backend FastAPI con Salida Estructurada | `app/main.py`, `app/schemas.py`, `app/routers/` | ✅ Completo |
| **Semana 2** | Endpoint Principal POST /chat y /clasificar | `POST /chat` (Streaming) y `POST /clasificar` (Pydantic) | ✅ Completo |
| **Semana 2** | Cliente del Modelo Encapsulado | `app/services/llm.py` (ClienteLLM desacoplado) | ✅ Completo |
| **Semana 2** | Módulo de Servicio LLM con Failover | `app/services/llm.py` | ✅ Completo |
| **Semana 2** | Catálogo de Prompts (Método R.E.C.E.T.A.) | `docs/05-prompts.md` | ✅ Completo |
| **Semana 2** | Frontend Funcional (Tablero Kanban de Tickets) | `frontend/index.html` | ✅ Completo |
| **Semana 2** | Cero Secretos en Git (`.env` en `.gitignore`) | `.gitignore`, `.env.example` | ✅ Completo |
| **Semana 2** | Pruebas Unitarias Automatizadas con Mocks | `tests/test_endpoints.py` (17 tests pasando) | ✅ Completo |
| **Semana 2** | Evidencias Técnicas de la Semana 2 | `docs/evidencias/semana-2/README.md` | ✅ Completo |

