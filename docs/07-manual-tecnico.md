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

---

## 7. Observabilidad y Log por Solicitud (Tokens Consumidos y Tiempo de Respuesta)

Para cumplir con los estándares de trazabilidad, auditoría técnica y la rúbrica del Seminario de Titulación (*«Log por solicitud: Tokens consumidos y tiempo de respuesta»*):

### 7.1. Middleware de Observabilidad HTTP (`app/main.py`)
Todas las solicitudes entrantes y salientes son interceptadas por `middleware_observabilidad_solicitudes`:
1. **Medición de Latencia con Precisión:** Calcula el tiempo total de ciclo de vida de la petición con `time.perf_counter()`, inyectando la cabecera HTTP estándar:
   ```http
   X-Response-Time-Ms: 42.18
   X-Request-ID: req-b4a1c0d2
   ```
2. **Buffer Circular en Memoria:** Mantiene en cola de longitud fija (`deque(maxlen=300)`) las métricas agregadas de solicitudes para consulta en tiempo real.
3. **Registro Estructurado en Consola:**
   - Para solicitudes generales:
     `📊 [SOLICITUD HTTP] GET /tablero -> 200 | Tiempo: 2.15ms | ReqID: req-3c5f2a1b`
   - Para solicitudes con inferencia IA:
     `📊 [SOLICITUD HTTP] POST /clasificar -> 201 | Tiempo: 18.5ms | ReqID: req-7e8d9c1a | IA: gemini:gemini-1.5-flash | Tokens: in=142, out=58, total=200`

### 7.2. Log de Inferencia en el Cliente Encapsulado (`app/services/llm.py`)
Cada invocación a los proveedores externos registra el desglose específico de consumo de tokens:
```text
🪙 [INFERENCIA LLM] Proveedor: gemini | Modelo: gemini-1.5-flash | Latencia: 420.5ms | Tokens: in=152, out=64, total=216
🪙 [INFERENCIA LLM] Proveedor: groq | Modelo: llama-3.3-70b-versatile | Latencia: 280.1ms | Tokens: in=165, out=59, total=224
🪙 [INFERENCIA LLM] Proveedor: conmutador-local-offline | Modelo: analizador-itil-heuristico | Latencia: 1.2ms | Tokens: in=0, out=0, total=0 (Motor Heurístico Determinista)
```

### 7.3. Endpoint de Telemetría: `GET /v1/metricas/solicitudes`
Expone en formato JSON el resumen consolidado de operaciones y consumo acumulado:
```json
{
  "total_solicitudes": 48,
  "tiempo_promedio_ms": 35.42,
  "total_tokens_consumidos": 3840,
  "total_tokens_prompt": 2720,
  "total_tokens_completado": 1120,
  "solicitudes_recientes": [
    {
      "req_id": "req-9f2d1e0a",
      "timestamp": "2026-10-25T20:55:00.000000Z",
      "metodo": "POST",
      "ruta": "/clasificar",
      "status_code": 201,
      "tiempo_respuesta_ms": 19.3,
      "proveedor": "gemini",
      "modelo": "gemini-1.5-flash",
      "tokens_prompt": 145,
      "tokens_completado": 55,
      "tokens_total": 200
    }
  ]
}
```

### 7.4. Visualización en Interfaz de Usuario (`frontend/index.html`)
El badge superior de estado y el modal de explicabilidad XAI reflejan en vivo la latencia y los tokens consumidos:
- **Badge superior:** `🟢 Proveedor: Google Gemini (gemini-1.5-flash) · ⏱️ 42ms · 🪙 200 tokens`
- **Modal de Explicabilidad (XAI):** Muestra el desglose de tokens de entrada (prompt), salida (JSON estructurado) y total.

