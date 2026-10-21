# Inventario de Fuentes Técnicas: ConectaTec

## 1. Identificación y Alcance del Corpus
* **Proyecto:** ConectaTec - Triaje Inteligente de Incidentes ISP
* **Caso de Estudio:** Caso N.º 03 (Grupo 3)
* **Objetivo del Corpus:** Proveer la base de conocimiento técnica oficial para alimentar el sistema RAG (Semana 3), garantizando que las respuestas de diagnóstico de primer nivel provengan exclusivamente de manuales de soporte validados y vigentes, con citas explícitas a los procedimientos operativos.

---

## 2. Criterios de Selección y Curaduría de Fuentes
1. **Oficialidad:** Solo se admiten manuales de fabricantes de equipos de red homologados (Huawei, ZTE, TP-Link, MikroTik) y directrices de proveedores de servicios de Internet (ISP) vigentes.
2. **Formato:** Documentos estructurados en Markdown (`.md`) y texto plano (`.txt`) almacenados localmente en `data/raw/` para su posterior ingesta y vectorización en ChromaDB.
3. **Estrategia de Fragmentación (Chunking):** La fragmentación se realiza por **sección operativa o procedimiento completo** (manteniendo encabezados `##` y pasos numerados, entre 300 y 600 tokens con solapamiento de 50 tokens), evitando el corte arbitrario por número fijo de caracteres que rompa la coherencia de un paso técnico.

---

## 3. Matriz de Fuentes Oficiales (Corpus de Conocimiento)

| ID | Documento / Guía Técnica | Origen Oficial / Fabricante | URL de Referencia | Vigencia | Formato | Estrategia de Fragmentación Prevista |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DOC-01** | Guía de interpretación de luces LED en ONT Huawei EchoLife (PON, LOS, LAN, Power) | Soporte Oficial Huawei Carrier | https://support.huawei.com/carrier/ | 2026 | `.md` | Por estado de luz LED (LOS roja, PON verde intermitente, etc.) |
| **DOC-02** | Manual de diagnóstico de indicadores lumínicos en ONT ZTE F660/F670 | Repositorio Técnico ZTE Global | https://support.zte.com.cn/ | 2026 | `.md` | Por patrón de luces y código de error visual |
| **DOC-03** | Protocolo de verificación y reinicio eléctrico de routers y ONT | Manual de Procedimientos ISP | https://conectatec.local/docs/reinicio-equipos | 2026 | `.md` | Procedimiento de ciclo de energía (pasos 1 a 5) |
| **DOC-04** | Guía de autogestión de credenciales Wi-Fi (SSID y clave WPA2/WPA3) | Mesa de Ayuda ISP ConectaTec | https://conectatec.local/docs/cambio-clave-wifi | 2026 | `.md` | Por fabricante de router y acceso a 192.168.1.1 |
| **DOC-05** | Optimización de cobertura inalámbrica: bandas 2.4 GHz vs. 5 GHz | Whitepaper Técnico Wi-Fi Alliance | https://www.wi-fi.org/discover-wi-fi | 2026 | `.md` | Por tema (interferencia de canal, distancia, banda de frecuencia) |
| **DOC-06** | Procedimiento oficial para prueba de velocidad de navegación (Test Ethernet) | Especificación Técnica Ookla ISP | https://www.speedtest.net/about/knowledge | 2026 | `.md` | Pasos de preparación del test (desconectar dispositivos, cable directo) |
| **DOC-07** | Diagnóstico y depuración de resolución de nombres DNS | Guía Técnica IETF / RFC 1035 | https://datatracker.ietf.org/doc/html/rfc1035 | 2026 | `.md` | Por comando operativo (`nslookup`, `ipconfig /flushdns`, cambio a 8.8.8.8) |
| **DOC-08** | Verificación de cableado de red de cobre (UTP Categoría 5e / 6) | Manual de Cableado Estructurado TIA-568 | https://tiaonline.org/ | 2026 | `.md` | Detección de daño en conector RJ-45 y degradación a 100 Mbps |
| **DOC-09** | Criterios de escalamiento por atenuación y rotura de acometida de fibra óptica | Manual de Campo Cuadrilla ISP | https://conectatec.local/docs/rotura-fibra | 2026 | `.md` | Procedimiento de escalamiento inmediato y validación de luz LOS |
| **DOC-10** | Detección de interferencias por electrodomésticos y atenuación estructural | Guía de Soporte Inalámbrico TP-Link | https://www.tp-link.com/support/faq/ | 2026 | `.md` | Por factor de interferencia (microondas, paredes de hormigón, espejos) |
| **DOC-11** | Protocolo de configuración de router neutro o repetidor Wi-Fi en modo puente | Soporte Técnico MikroTik RouterOS | https://help.mikrotik.com/docs/ | 2026 | `.md` | Por modo de operación (Access Point vs. Extender / Bridge) |
| **DOC-12** | Guía de detección de saturación de canal Wi-Fi y selección manual de canales | Repositorio de Ingeniería ISP | https://conectatec.local/docs/canales-wifi | 2026 | `.md` | Por espectro de frecuencia (canales 1, 6, 11 en 2.4 GHz y canales DFS en 5 GHz) |
| **DOC-13** | Procedimiento ante microcortes o caídas intermitentes de sesión PPPoE | Manual de Conectividad ISP | https://conectatec.local/docs/intermitencia-pppoe | 2026 | `.md` | Por diagnóstico de negociación de enlace y registro de logs de sesión |
| **DOC-14** | Guía de consulta de estado comercial, corte por mora y canales de pago | Políticas de Servicio al Cliente ISP | https://conectatec.local/docs/facturacion-cortes | 2026 | `.md` | Por estado administrativo de cuenta y reactivación automática de servicio |
| **DOC-15** | Matriz ITIL de clasificación de incidentes, impacto y urgencia | Guía de Gestión de Servicios ITIL v4 | https://www.axelos.com/certifications/itil-service-management | 2026 | `.md` | Tabla matricial completa de cruce Impacto vs. Urgencia |

---

## 4. Estructura de Almacenamiento en el Repositorio
Los textos de los documentos listados se depositan en el directorio `data/raw/` del proyecto, siguiendo la nomenclatura:
```text
data/raw/
├── DOC-01-huawei-ont-luces.md
├── DOC-02-zte-ont-indicadores.md
├── DOC-03-reinicio-electrico.md
├── DOC-04-cambio-clave-wifi.md
├── DOC-05-cobertura-24-5ghz.md
├── DOC-06-test-velocidad-cableado.md
├── DOC-07-resolucion-dns.md
├── DOC-08-cableado-utp-rj45.md
├── DOC-09-rotura-fibra-escalamiento.md
├── DOC-10-interferencias-wifi.md
├── DOC-11-modo-puente-repetidores.md
├── DOC-12-canales-inalambricos.md
├── DOC-13-intermitencia-pppoe.md
├── DOC-14-corte-comercial-facturacion.md
└── DOC-15-matriz-itil-prioridades.md
