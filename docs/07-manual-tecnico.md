# Manual Técnico y de Despliegue · ConectaTec
**Caso N.º 03 · Grupo 3 UNIANDES | Backend FastAPI, RAG ChromaDB, SQLite y Resiliencia**

---

## 1. Requisitos del Sistema
- **Sistema Operativo:** Windows 10/11, Linux (Ubuntu 22.04+) o macOS.
- **Python:** Versión 3.10 o superior (verificado con Python 3.14).
- **Herramientas:** Git, navegador web moderno.

---

## 2. Instalación y Despliegue Paso a Paso

### 2.1. Clonar el Repositorio
```bash
git clone https://github.com/cgmorales12/conectatec-mvp.git
cd conectatec-mvp
```

### 2.2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2.3. Configurar Variables de Entorno
Copie el archivo de ejemplo `.env.example` hacia `.env`:
```bash
cp .env.example .env
```
Edite `.env` y coloque sus credenciales:
```env
GEMINI_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
ENVIRONMENT=development
```
*(Nota: Si no configura claves de API, el sistema activa automáticamente el conmutador heurístico offline para pruebas 100% funcionales sin internet).*

### 2.4. Iniciar el Servidor de Backend y Frontend
Ejecute el servidor de desarrollo de FastAPI con Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

Acceso a servicios:
- **Tablero Kanban Web:** `http://localhost:8000/tablero`
- **Documentación Interactiva Swagger:** `http://localhost:8000/docs`
- **Documentación Redoc:** `http://localhost:8000/redoc`
- **Chequeo de Salud:** `http://localhost:8000/v1/salud`

---

## 3. Arquitectura del Backend y Estructura de Módulos

```text
app/
├── main.py          # Configuración de FastAPI, middleware Token Bucket y manejadores RFC 9457
├── schemas.py       # DTOs y validación con Pydantic V2 (extra="forbid")
├── database.py      # Repositorio SQLite parametrizado con consultas seguras '?'
├── routers/
│   ├── tickets.py   # Endpoints de clasificación, consulta y cambio de estado
│   └── salud.py     # Endpoints de diagnóstico operativo
├── services/
│   ├── llm.py       # Gateway con conmutación por error Gemini -> Groq y anonimizador LOPDP
│   └── rag.py       # Motor de búsqueda semántica y citas de los 15 manuales
└── tools/
    └── priorizar.py # Cálculo determinista de prioridad ITIL (config/matriz_prioridad.json)
```

---

## 4. Endpoints de la API REST

### 4.1. `POST /v1/tickets/clasificar`
- **Descripción:** Recibe el reporte, extrae impacto/urgencia con IA, calcula prioridad ITIL y busca citas en manuales RAG.
- **Código de Respuesta:** `201 Created`
- **Contrato de Error:** `422 Unprocessable Entity` con `application/problem+json` (RFC 9457) si el texto tiene menos de 10 caracteres.

### 4.2. `GET /v1/tickets`
- **Descripción:** Retorna la lista completa de tickets registrados con sus metadatos de IA y citas documentales.
- **Código de Respuesta:** `200 OK`

### 4.3. `PATCH /v1/tickets/{id}/estado`
- **Descripción:** Actualiza el estado Kanban de un ticket (`nuevo`, `en_atencion`, `escalado_cuadrilla`, `resuelto`).
- **Código de Respuesta:** `200 OK`

---

## 5. Ejecución de Pruebas Unitarias Automatizadas con Mocks
El proyecto incluye pruebas que validan los contratos, la matriz ITIL, la anonimización LOPDP y la resiliencia sin necesidad de internet:
```bash
pytest -v tests/test_endpoints.py
```
