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

---

## 6. Verificación de Ciberseguridad: Cero Secretos en Git
En estricto cumplimiento con las directivas de ciberseguridad, OWASP LLM 2025 (LLM06: Divulgación de Información Sensible) y el Art. 23 de la Ley Orgánica de Protección de Datos Personales (LOPDP Ecuador):

1. **Claves Exclusivamente en Variables de Entorno:**
   Ninguna credencial (`GEMINI_API_KEY`, `GROQ_API_KEY`) reside en el código fuente o en base de datos. El cliente `ClienteLLM` las extrae dinámicamente en tiempo de ejecución a través de `os.environ` mediante `python-dotenv`.

2. **Blindaje en `.gitignore`:**
   El archivo `.gitignore` excluye taxativamente:
   ```gitignore
   .env
   .env.*
   *.env
   .env.local
   !.env.example
   ```

3. **Verificación en Todo el Historial de Git:**
   Se comprobó que el archivo `.env` **nunca ha aparecido en ningún commit ni árbol de la historia de Git**:
   ```bash
   git log --all --full-history --oneline -- ".env"
   # Salida esperada: (vacío / 0 commits)
   git ls-files .env
   # Salida esperada: (vacío / no rastreado)
   ```

4. **Plantilla Pública Segura (`.env.example`):**
   El repositorio únicamente distribuye `.env.example` con variables vacías o marcadores de posición (`tu_clave_de_gemini_aqui`), garantizando cero fuga de secretos.

5. **Script Determinista de Auditoría:**
   Se incluye una herramienta CLI para que cualquier evaluador valide el perímetro de seguridad en 1 segundo:
   ```bash
   python scripts/auditar_cero_secretos.py
   ```
