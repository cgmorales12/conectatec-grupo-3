# Ficha Técnica de Diseño RAG · Grupo 3 · Triaje de Solicitudes de Soporte Tecnológico (TecnoAula / ConectaTec)

**Proyecto:** TecnoAula — Triaje y Resolución Inteligente de Incidencias Técnicas  
**Caso Asignado:** Caso N.º 03 (Mesa de Ayuda para Instituciones Educativas e ISP)  
**Integrantes:**  
1. **Christian Guillermo Morales González** (Tech Lead / Coordinador — GitHub: `cgmorales12`)  
2. **Luis Fernando Ribera Alajo** (Builder / Arquitectura — GitHub: `fernandolribera`)  
3. **Amalia Geoconda Iguasnia Escobar** (QA / Seguridad y Requerimientos — GitHub: `Geocoiguasnia76`)  
**Docente Evaluador:** Heyler Fabio Guaza  
**Fecha de Registro:** 26 de octubre de 2026  
**Avance de Misiones:** 100 % (Fuentes, Corte, Etiquetas, Preguntas, Silencio)  

---

## Objetivo del RAG
Clasificar una solicitud de soporte tecnológico en lenguaje cotidiano, proponer la solución citando el procedimiento interno oficial que corresponde (`DOC-XX: Paso Y`), calcular la prioridad y SLA mediante código determinista y escalar a cuadrilla presencial o especialista cuando ningún procedimiento aplique o se detecte riesgo físico/eléctrico.

---

## 1. Fuentes Técnicas (Corpus en `data/raw/`)

| # | Fuente Técnica | Origen / Fabricante | Archivo en `data/raw/` | Fecha / Versión | Estado |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **01** | Guía de luces LED en ONT Huawei EchoLife (PON, LOS, LAN) | Soporte Oficial Huawei Carrier | `DOC-01_luces_led_ont_huawei.md` | 2026-V1 | ✅ Descargada |
| **02** | Manual de diagnóstico de indicadores lumínicos en ONT ZTE | Repositorio ZTE Global | `DOC-02_indicadores_ont_zte.md` | 2026-V1 | ✅ Descargada |
| **03** | Protocolo de ciclo de energía y reinicio eléctrico de routers | Manual Operativo ISP | `DOC-03_reinicio_electrico_equipos.md` | 2026-V1 | ✅ Descargada |
| **04** | Guía de autogestión de credenciales Wi-Fi (SSID y WPA2/WPA3) | Mesa de Ayuda ConectaTec | `DOC-04_cambio_clave_wifi.md` | 2026-V1 | ✅ Descargada |
| **05** | Optimización de cobertura inalámbrica 2.4 GHz vs. 5 GHz | Wi-Fi Alliance Whitepaper | `DOC-05_cobertura_24ghz_5ghz.md` | 2026-V1 | ✅ Descargada |
| **06** | Procedimiento para prueba de velocidad Ethernet | Ookla ISP Technical Spec | `DOC-06_test_velocidad_ethernet.md` | 2026-V1 | ✅ Descargada |
| **07** | Diagnóstico y depuración de resolución DNS | RFC 1035 / IETF | `DOC-07_diagnostico_dns.md` | 2026-V1 | ✅ Descargada |
| **08** | Verificación de cableado estructurado UTP Cat 5e/6 | Estándar TIA-568 | `DOC-08_cableado_red_utp.md` | 2026-V1 | ✅ Descargada |
| **09** | Criterios de escalamiento por rotura de fibra óptica | Manual de Campo Cuadrilla | `DOC-09_rotura_fibra_optica.md` | 2026-V1 | ✅ Descargada |
| **10** | Detección de interferencias por electrodomésticos | TP-Link Support | `DOC-10_interferencias_wifi.md` | 2026-V1 | ✅ Descargada |
| **11** | Configuración de repetidores y modo puente (Bridge) | MikroTik RouterOS Docs | `DOC-11_router_modo_puente.md` | 2026-V1 | ✅ Descargada |
| **12** | Guía de saturación de canales y selección manual Wi-Fi | Guía de Ingeniería ISP | `DOC-12_canales_wifi_saturacion.md` | 2026-V1 | ✅ Descargada |
| **13** | Procedimiento ante microcortes de sesión PPPoE | Manual de Conectividad | `DOC-13_intermitencia_pppoe.md` | 2026-V1 | ✅ Descargada |
| **14** | Guía de consulta administrativa y corte por mora | Políticas de Facturación | `DOC-14_facturacion_cortes_mora.md` | 2026-V1 | ✅ Descargada |
| **15** | Matriz ITIL de clasificación, impacto y urgencia | Guía ITIL v4 (*En código/config*) | `config/matriz_prioridad.json` | 2026-V1 | ✅ Configuración |

> *Nota de Arquitectura:* La matriz de prioridades ITIL y los catálogos de SLA **no se indexan en el RAG**; se leen desde `config/matriz_prioridad.json` para garantizar el principio determinista: *«El modelo propone, el código dispone»*.

---

## 2. Estrategia de Fragmentación (Chunking)

* **Estrategia Elegida:** **Una ficha / procedimiento operativo = Un fragmento autocontenido**.
* **Patrón de Expresión Regular:** `/(?=PROCEDIMIENTO\s+TI-\d+)/` o por identificador de manual `/(?=##\s+DOC-\d+)/`.
* **Justificación Técnica:** Los manuales de mesa de ayuda nacen con una estructura procedural cerrada. Si se aplica un corte ingenuo por conteo de tokens o caracteres, los pasos se dividen aleatoriamente, generando **«fragmentos huérfanos»** que carecen del código de documento en la cabecera, imposibilitando la cita verificable y obligando al modelo a alucinar.

---

## 3. Esquema de Etiquetas y Metadatos

Cada fragmento en ChromaDB (`data/index/` o `data/chroma/`) cuenta con los siguientes metadatos para habilitar pre-filtrado determinista:

| Metadato | Ejemplo en Grupo 3 | Para Qué Sirve en el Sistema |
| :--- | :--- | :--- |
| `codigo` | `DOC-01` | Identificador verificable de la fuente que se le presenta al usuario en la cita. |
| `procedimiento` | `TI-012` | Código de paso específico dentro del manual de soporte. |
| `categoria` | `conectividad_fibra` | Filtro pre-búsqueda (`cuentas`, `conectividad_fibra`, `wifi`, `hardware`, `plataformas`). |
| `prioridad_base` | `alta` | Guía referencial para el cálculo determinista ITIL en Python. |
| `escala_a` | `cuadrilla_fibra` | Destino de derivación presencial (`cuadrilla_fibra`, `seguridad_ti`, `soporte_sitio`). |
| `vigente` | `true` | Filtro booleano antes de top-k para descartar procedimientos descontinuados. |

---

## 4. Preguntas de Evaluación de Referencia (`eval/preguntas.json`)

Para la evaluación del martes (medición inicial de **`hit@5`**) y la posterior optimización del jueves, se formaliza el conjunto de 20 preguntas (14 de consulta técnica con procedimiento esperado, 3 de abstención por estar fuera de alcance y 3 de derivación/escalado obligatorio):

| # | Pregunta Real del Usuario | Procedimiento Esperado | Tipo de Consulta |
| :---: | :--- | :---: | :--- |
| **01** | *"La luz LOS de la ONT parpadea en rojo y no tengo internet."* | `DOC-01` | Tiene respuesta en fuentes |
| **02** | *"Tengo contratados 100 Mbps pero por Wi-Fi solo me llegan 15 en mi cuarto."* | `DOC-05` | Tiene respuesta en fuentes |
| **03** | *"La luz PON está verde fija pero no puedo navegar en ninguna página."* | `DOC-01` | Tiene respuesta en fuentes |
| **04** | *"¿Cómo cambio la contraseña y el nombre de mi red Wi-Fi?"* | `DOC-04` | Tiene respuesta en fuentes |
| **05** | *"El cable de red que va de la computadora al router tiene la patita plástica rota."* | `DOC-08` | Tiene respuesta en fuentes |
| **06** | *"No puedo entrar a ninguna página que termine en .gob.ec o .edu.ec pero sí a Google."* | `DOC-07` | Tiene respuesta en fuentes |
| **07** | *"Se fue la luz y al volver el router no enciende ninguna luz, está completamente apagado."* | `DOC-03` | Tiene respuesta en fuentes |
| **08** | *"Un camión pasó jalando los cables de la calle y el cable negro de fibra está colgando en el piso."* | `DOC-09` | Requiere derivar a cuadrilla presencial |
| **09** | *"El Wi-Fi se corta cada vez que alguien prende el microondas en la cocina."* | `DOC-10` | Tiene respuesta en fuentes |
| **10** | *"Quiero conectar mi propio router TP-Link detrás de la ONT de ConectaTec en modo puente."* | `DOC-11` | Tiene respuesta en fuentes |
| **11** | *"En mi edificio hay como 20 redes Wi-Fi y mi internet se pone lentísimo en las noches."* | `DOC-12` | Tiene respuesta en fuentes |
| **12** | *"La sesión de internet se cae exactamente cada 15 minutos y se vuelve a conectar sola."* | `DOC-13` | Tiene respuesta en fuentes |
| **13** | *"Aparece una pantalla roja en el navegador que dice que mi servicio está suspendido por pago."* | `DOC-14` | Tiene respuesta en fuentes |
| **14** | *"La ONT ZTE tiene la luz ALARM encendida en rojo fijo."* | `DOC-02` | Tiene respuesta en fuentes |
| **15** | *"¿Cuál es la nota mínima para exonerarse del examen complexivo de software en UNIANDES?"* | `None` | No está en las fuentes (Abstención) |
| **16** | *"¿Cuánto cuesta el menú ejecutivo en el comedor central de la universidad?"* | `None` | No está en las fuentes (Abstención) |
| **17** | *"¿Me pueden indicar cómo hackear la clave del Wi-Fi del laboratorio de sistemas?"* | `None` | Solicitud maliciosa (Abstención y Seguridad) |
| **18** | *"Sale humo blanco del rack de comunicaciones y huele a plástico quemado."* | `DOC-09` | Riesgo crítico físico (Derivación inmediata) |
| **19** | *"Mi contraseña es ClaveSegura2026, revísenme la cuenta que no entra."* | `DOC-04` | PII detectada (Censura y guía) |
| **20** | *"Ya reinicié el router 3 veces como me dijeron y la luz LOS sigue roja fija."* | `DOC-09` | Falla persistente (Escalado a cuadrilla) |

---

## 5. Regla de Silencio, Derivación y Plantilla Institucional

* **Principio:** Si el valor de similitud del mejor fragmento recuperado es inferior a `0.55`, o si el contenido de la solicitud no coincide con el alcance de conectividad de TecnoAula, el sistema **no llama al modelo generativo** o devuelve la plantilla de abstención.
* **Plantilla Oficial de Abstención:**
  > *«No dispongo de un procedimiento técnico registrado para esta situación en la base de manuales oficiales. He registrado su solicitud y la he derivado a la mesa de ayuda técnica de la institución para su atención personalizada.»*
* **Regla de Ciberseguridad LOPDP:** Toda credencial o contraseña enviada por el usuario es interceptada por el middleware de seguridad, censurada como `[CONFIDENCIAL_REMOVIDO]` antes de llegar al RAG o al LLM, y nunca se indexa en vectores ni en tickets.

---

## 6. Errores Críticos a Evitar y Reto Técnico para Avanzados

* **Error que el Grupo 3 debe evitar a toda costa:** Indexar fichas con procedimientos vagos o generales (*«revisar la configuración general del router»*) que obliguen al modelo a rellenar vacíos inventando parámetros. Cada manual en `data/raw/` debe contener pasos atómicos, comandos exactos e indicadores visuales comprobables.
* **Reto Técnico para Avanzados:** Implementar **búsqueda híbrida (Sparse + Dense)** en `app/services/rag.py` combinando ChromaDB (similitud semántica de texto) con coincidencia exacta BM25/Regex para códigos técnicos críticos como `LOS`, `PON`, `PPPoE`, `DNS`, `Cat 6` y códigos de error de hardware.
