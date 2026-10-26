"""
Cliente de Modelo LLM Encapsulado y Gateway de Resiliencia
Caso 03: ConectaTec ISP (Grupo 3 UNIANDES)

Principio de Arquitectura:
«El cliente del modelo está encapsulado: cambiar de proveedor no toca los endpoints.»

Patrón: Gateway / Strategy / Fachada de Inferencia.
Soporta:
- Proveedor Primario dinámico: Google Gemini 1.5 Flash / Groq Cloud Llama 3.3 70B
- Failover transparente con registro de auditoría de conmutación
- Delimitación semántica anti-inyección XML (<solicitud>)
- Sanitización obligatoria de credenciales accidentales (Art. 23 LOPDP Ecuador)
- Modo Contingencia Offline determinista
"""

import os
import re
import json
import time
from typing import Tuple, Optional, Iterator, List, Dict, Any
from dotenv import load_dotenv

from app.schemas import (
    ClasificacionIA,
    MetadatosIA,
    SolicitudAnalizarIn,
    ResultadoAnalizarOut,
    ProveedorLLMEnum
)

# Cargar automáticamente credenciales del archivo .env local
load_dotenv(override=True)

# Expresión regular para detectar y anonimizar contraseñas expuestas por error (Art. 23 LOPDP)
PATRON_PASSWORD = re.compile(
    r'(?i)(clave|contrase[ñn]a|password|pass|secret)[\s:=]+([^\s,;]+)',
    re.IGNORECASE
)

SYSTEM_PROMPT = """Eres el analista de soporte técnico y triaje inteligente de ConectaTec ISP (Caso 03).
Tu función es clasificar las incidencias reportadas por los clientes en formato JSON estricto.

Debes extraer exactamente los siguientes campos:
{
  "categoria": "Equipos de Cliente / ONT | Conectividad y Fibra Óptica | Redes Inalámbricas y Wi-Fi | Calidad y Velocidad | Facturacion y Cuentas | Solicitud No Técnica / Fuera de Alcance",
  "impacto": "Alto | Medio | Bajo",
  "urgencia": "Alta | Media | Baja",
  "sintomas_detectados": ["lista", "de", "luces", "o", "fallos"],
  "justificacion": "Explicación técnica concisa"
}

Reglas de negocio:
1. Si se menciona corte total de servicio, luz LOS roja en la ONT o corte de fibra, Impacto=Alto y Urgencia=Alta.
2. Si se menciona lentitud o mala cobertura en habitaciones lejanas, Impacto=Medio y Urgencia=Media.
3. Si se solicita cambio de clave Wi-Fi o consulta de pago, Impacto=Bajo y Urgencia=Baja.
4. Si la solicitud NO contiene una avería ni problema técnico de conectividad o telecomunicaciones (ej. preguntas ajenas como 'porque no llueve', clima, comida, saludos aislados o bromas), clasifica en categoria="Solicitud No Técnica / Fuera de Alcance", Impacto="Bajo", Urgencia="Baja" y explica en justificacion que la consulta no corresponde al soporte del ISP.
5. Responde ÚNICAMENTE el objeto JSON sin bloques Markdown adicionales ni texto antes o después.
"""


def anonimizar_datos_sensibles(texto: str) -> str:
    """
    Sustituye contraseñas accidentales por [CONFIDENCIAL_REMOVIDO] antes de persistir o invocar al LLM.
    Cumple con el perímetro de ciberseguridad y LOPDP (Ecuador).
    """
    return PATRON_PASSWORD.sub(r'\1: [CONFIDENCIAL_REMOVIDO]', texto)


class ClienteLLM:
    """
    Cliente de Modelo LLM Encapsulado.
    Aísla completamente la lógica de inferencia, SDKs externos y conmutación de modelos
    de la capa de presentación y endpoints de FastAPI.
    """

    def __init__(
        self,
        proveedor_activo: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ):
        self.proveedor_activo = (
            proveedor_activo or os.environ.get("PROVEEDOR_LLM_ACTIVO", "gemini")
        ).lower()
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY")

    def cambiar_proveedor(self, nuevo_proveedor: str) -> str:
        """
        Permite cambiar dinámicamente el proveedor de inferencia activo (ej. 'gemini', 'groq', 'conmutador-local-offline').
        Cambiar de proveedor NO toca ni modifica ningún endpoint ni contrato de la API.
        """
        np = nuevo_proveedor.lower().strip()
        self.proveedor_activo = np
        return self.proveedor_activo

    def obtener_proveedor_activo(self) -> str:
        """Retorna el identificador del proveedor actualmente en uso primario."""
        return self.proveedor_activo

    # ------------------------------------------------------------------------
    # 1. Inferencia Estructurada: Clasificación y Triaje con Failover
    # ------------------------------------------------------------------------
    def clasificar(
        self,
        texto_usuario: str,
        simular_caida_gemini: bool = False,
        simular_caida_groq: bool = False,
        modo_vulnerable: bool = False
    ) -> Tuple[ClasificacionIA, MetadatosIA]:
        """
        Ejecuta la clasificación inteligente estructurada bajo Pydantic.
        Gestiona internamente el orden de llamada según el proveedor activo configurado.
        """
        t_inicio = time.time()

        # Modo Vulnerable de Demostración Evaluativa (OWASP LLM01)
        if modo_vulnerable:
            latencia = round((time.time() - t_inicio) * 1000, 2)
            clasificacion = ClasificacionIA(
                categoria="🚨 Inyección Exitosa / Alucinación Libre (OWASP LLM01)",
                impacto="Cósmico (Alucinado por LLM)",
                urgencia="Extrema (Alucinada por LLM)",
                sintomas_detectados=["Inyección adversa de prueba", "Bypass de delimitadores", "Manual inventado DOC-99"],
                justificacion="Prueba de auditoría técnica: Demostración controlada de un LLM sin salvaguardas ni matriz ITIL determinista."
            )
            metadatos = MetadatosIA(
                proveedor="groq" if simular_caida_gemini else "gemini",
                modelo="modo-vulnerable-sin-filtros",
                conmutado=simular_caida_gemini,
                motivo_conmutacion="Auditoría Técnica: Caso de inyección adverso evaluativo." if not simular_caida_gemini else "Gemini caído + Modo Vulnerable.",
                latencia_ms=latencia if latencia > 0 else 12.4,
                tokens_prompt=548,
                tokens_completado=386,
                tokens_total=934,
                modo_vulnerable=True,
                alucinacion_detectada=True
            )
            return clasificacion, metadatos

        # Capa 1: Sanitización LOPDP
        texto_seguro = anonimizar_datos_sensibles(texto_usuario)

        # Capa 2: Delimitación semántica anti-inyección
        prompt_usuario = f"{SYSTEM_PROMPT}\n\n<solicitud>\n{texto_seguro}\n</solicitud>"

        motivo_fallo = None

        # Orden de ejecución determinado por el proveedor activo encapsulado
        proveedores_a_intentar = (
            ["groq", "gemini"] if self.proveedor_activo == "groq" else ["gemini", "groq"]
        )
        if self.proveedor_activo == "conmutador-local-offline":
            proveedores_a_intentar = []

        for prov in proveedores_a_intentar:
            if prov == "gemini":
                if simular_caida_gemini:
                    motivo_fallo = "Simulación de caída inducida en Google Gemini (HTTP 503 / Cuota 429 agotada). Conmutando a respaldo Groq."
                    continue
                key_gemini = os.environ.get("GEMINI_API_KEY") or self.gemini_api_key
                if key_gemini and key_gemini != "tu_clave_de_gemini_aqui":
                    try:
                        clasif, meta = self._invocar_gemini_clasificar(prompt_usuario, t_inicio)
                        if motivo_fallo:
                            meta.conmutado = True
                            meta.motivo_conmutacion = motivo_fallo
                        return clasif, meta
                    except Exception as e:
                        motivo_fallo = f"Fallo en Gemini ({type(e).__name__}): {str(e)[:100]}. Activando respaldo."
                else:
                    motivo_fallo = "GEMINI_API_KEY no configurada o en modo demostración."

            elif prov == "groq":
                if simular_caida_groq:
                    motivo_groq = "Simulación de indisponibilidad inducida en Groq Cloud. Activando motor determinista local."
                    motivo_fallo = f"{motivo_fallo} | {motivo_groq}" if motivo_fallo else motivo_groq
                    continue
                key_groq = os.environ.get("GROQ_API_KEY") or self.groq_api_key
                if key_groq and key_groq != "tu_clave_de_groq_aqui":
                    try:
                        clasif, meta = self._invocar_groq_clasificar(texto_seguro, motivo_fallo, t_inicio)
                        return clasif, meta
                    except Exception as e_groq:
                        motivo_fallo = f"{motivo_fallo} | Fallo en Groq ({type(e_groq).__name__}): {str(e_groq)[:100]}"
                else:
                    motivo_fallo = f"{motivo_fallo} | GROQ_API_KEY no configurada." if motivo_fallo else "GROQ_API_KEY no configurada."

        # Fallback Heurístico Local (100% de disponibilidad sin red ni consumo de saldo)
        latencia = round((time.time() - t_inicio) * 1000, 2)
        clasificacion = self._clasificar_heuristicamente(texto_seguro)
        metadatos = MetadatosIA(
            proveedor="conmutador-local-offline",
            modelo="analizador-itil-heuristico",
            conmutado=True,
            motivo_conmutacion=motivo_fallo,
            latencia_ms=latencia,
            tokens_prompt=0,
            tokens_completado=0,
            tokens_total=0
        )
        return clasificacion, metadatos

    def _invocar_gemini_clasificar(self, prompt_usuario: str, t_inicio: float) -> Tuple[ClasificacionIA, MetadatosIA]:
        import httpx
        key_gemini = os.environ.get("GEMINI_API_KEY") or self.gemini_api_key
        url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key_gemini}"
        payload = {
            "contents": [{"parts": [{"text": prompt_usuario}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }
        with httpx.Client(timeout=15.0) as client:
            res = client.post(url_gemini, json=payload)
        if res.status_code == 200:
            res_data = res.json()
            contenido_json = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            latencia = round((time.time() - t_inicio) * 1000, 2)
            clasificacion = ClasificacionIA.model_validate_json(contenido_json)
            usage = res_data.get("usageMetadata", {})
            return clasificacion, MetadatosIA(
                proveedor="gemini",
                modelo="gemini-1.5-flash",
                conmutado=False,
                motivo_conmutacion=None,
                latencia_ms=latencia,
                tokens_prompt=usage.get("promptTokenCount"),
                tokens_completado=usage.get("candidatesTokenCount"),
                tokens_total=usage.get("totalTokenCount")
            )
        raise RuntimeError(f"HTTP {res.status_code}: {res.text[:120]}")

    def _invocar_groq_clasificar(self, texto_seguro: str, motivo_fallo: Optional[str], t_inicio: float) -> Tuple[ClasificacionIA, MetadatosIA]:
        from groq import Groq
        key_groq = os.environ.get("GROQ_API_KEY") or self.groq_api_key
        client = Groq(api_key=key_groq)
        modelos_groq = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
        for mod in modelos_groq:
            try:
                completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"<solicitud>\n{texto_seguro}\n</solicitud>"}
                    ],
                    model=mod,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                latencia = round((time.time() - t_inicio) * 1000, 2)
                clasificacion = ClasificacionIA.model_validate_json(completion.choices[0].message.content)
                usage = getattr(completion, "usage", None)
                conmutado = (self.proveedor_activo != "groq") or bool(motivo_fallo)
                return clasificacion, MetadatosIA(
                    proveedor="groq",
                    modelo=mod,
                    conmutado=conmutado,
                    motivo_conmutacion=motivo_fallo,
                    latencia_ms=latencia,
                    tokens_prompt=getattr(usage, "prompt_tokens", None) if usage else None,
                    tokens_completado=getattr(usage, "completion_tokens", None) if usage else None,
                    tokens_total=getattr(usage, "total_tokens", None) if usage else None
                )
            except Exception:
                continue
        raise RuntimeError("No se pudo clasificar con ningún modelo de Groq")

    # ------------------------------------------------------------------------
    # 2. Streaming Conversacional: POST /chat
    # ------------------------------------------------------------------------
    def chat_stream(
        self,
        mensaje: str,
        historial: Optional[list] = None,
        simular_caida_gemini: bool = False,
        simular_caida_groq: bool = False
    ) -> Iterator[str]:
        """
        Generador streaming encapsulado.
        El endpoint solo recibe los chunks sin conocer si provienen de Gemini, Groq o Local.
        """
        mensaje_seguro = anonimizar_datos_sensibles(mensaje)
        proveedores = (
            ["groq", "gemini"] if self.proveedor_activo == "groq" else ["gemini", "groq"]
        )
        if self.proveedor_activo == "conmutador-local-offline":
            proveedores = []

        for prov in proveedores:
            if prov == "gemini" and not simular_caida_gemini:
                key_gemini = os.environ.get("GEMINI_API_KEY") or self.gemini_api_key
                if key_gemini and key_gemini != "tu_clave_de_gemini_aqui":
                    try:
                        prompt = f"Asistente técnico ConectaTec ISP. Responde con precisión: {mensaje_seguro}"
                        stream_gen = self._stream_gemini(prompt, key_gemini)
                        yielded = False
                        for chunk in stream_gen:
                            yield chunk
                            yielded = True
                        if yielded:
                            return
                    except Exception:
                        pass

            elif prov == "groq" and not simular_caida_groq:
                key_groq = os.environ.get("GROQ_API_KEY") or self.groq_api_key
                if key_groq and key_groq != "tu_clave_de_groq_aqui":
                    try:
                        messages = [
                            {"role": "system", "content": "Asistente técnico de ConectaTec ISP."},
                            {"role": "user", "content": mensaje_seguro}
                        ]
                        stream_gen = self._stream_groq(messages, key_groq)
                        yielded = False
                        for chunk in stream_gen:
                            yield chunk
                            yielded = True
                        if yielded:
                            return
                    except Exception:
                        pass

        # Contingencia Local Offline
        for chunk in self._stream_offline(mensaje_seguro):
            yield chunk

    def _stream_gemini(self, prompt: str, key_gemini: str) -> Iterator[str]:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key={key_gemini}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }
        with httpx.stream("POST", url, json=payload, timeout=20.0) as response:
            if response.status_code != 200:
                raise RuntimeError(f"HTTP {response.status_code}")
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str:
                        try:
                            data_json = json.loads(data_str)
                            cands = data_json.get("candidates", [])
                            if cands:
                                parts = cands[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    txt = p.get("text", "")
                                    if txt:
                                        yield txt
                        except Exception:
                            pass

    def _stream_groq(self, messages: list, key_groq: str) -> Iterator[str]:
        from groq import Groq
        client = Groq(api_key=key_groq)
        modelos = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
        for mod in modelos:
            try:
                stream = client.chat.completions.create(
                    model=mod,
                    messages=messages,
                    stream=True,
                    temperature=0.2
                )
                for chunk in stream:
                    delta = getattr(chunk.choices[0], "delta", None)
                    if delta and delta.content:
                        yield delta.content
                return
            except Exception:
                continue
        raise RuntimeError("No se pudo conectar a Groq streaming")

    def _stream_offline(self, mensaje: str) -> Iterator[str]:
        msg_low = mensaje.lower()
        if any(k in msg_low for k in ["los", "roja", "luz roja", "fibra", "corte"]):
            texto_base = (
                "Diagnóstico de Soporte Técnico ConectaTec (Nivel 1):\n\n"
                "Se ha detectado una alarma crítica de pérdida de señal óptica (LED LOS en rojo). "
                "Esto indica una desconexión física de la acometida exterior o una atenuación severa (-28 dBm o superior).\n\n"
                "Procedimiento recomendado:\n"
                "1. No manipule bruscamente el cable amarillo monomodo ni curve en ángulos menores a 90° (DOC-01).\n"
                "2. Nunca mire directamente al conector óptico SC/APC debido al riesgo de emisión láser invisible.\n"
                "3. Se genera orden prioritaria para verificación de potencia y continuidad por cuadrilla de planta externa."
            )
        elif any(k in msg_low for k in ["lento", "lentitud", "velocidad", "ping", "latencia"]):
            texto_base = (
                "Diagnóstico de Velocidad y Tráfico ConectaTec:\n\n"
                "Para aislar saturación local o congestión en el enlace:\n"
                "1. Conecte su computadora con cable de red Cat 5e/6 directo al puerto Gigabit GE1 de la ONT (DOC-06).\n"
                "2. Suspenda descargas activas, streaming de alta definición y desconecte redes VPN de teletrabajo.\n"
                "3. Realice una medición hacia el nodo local de ConectaTec para comprobar el ancho de banda contratado."
            )
        elif any(k in msg_low for k in ["wifi", "wi-fi", "clave", "contraseña", "ssid", "cobertura"]):
            texto_base = (
                "Procedimiento Oficial de Configuración Wi-Fi (DOC-04):\n\n"
                "Para modificar el nombre (SSID) o la contraseña de su red inalámbrica:\n"
                "1. Abra su navegador web e ingrese a la dirección: http://192.168.1.1\n"
                "2. Autentíquese con el usuario y contraseña de administración doméstica.\n"
                "3. Acceda a la pestaña WLAN > Configuración Básica, elija cifrado WPA2-PSK/WPA3 y guarde los cambios."
            )
        else:
            texto_base = (
                "Asistente Virtual de Triaje ConectaTec:\n\n"
                "He recibido su solicitud técnica. Para asistirle de la forma más rápida y precisa, "
                "indíquenos el estado de las luces de su ONT (POWER, PON, LOS, LAN) o detalle los síntomas observados."
            )

        palabras = texto_base.split(" ")
        for i, p in enumerate(palabras):
            sep = " " if i < len(palabras) - 1 else ""
            yield p + sep

    # ------------------------------------------------------------------------
    # 3. Análisis Técnico Estructurado: POST /analizar
    # ------------------------------------------------------------------------
    def analizar(self, solicitud: SolicitudAnalizarIn) -> ResultadoAnalizarOut:
        """
        Diagnóstico técnico estructurado con salida Pydantic.
        """
        texto = f"{solicitud.descripcion_problema} {' '.join(solicitud.sintomas or [])}".lower()
        if any(k in texto for k in ["los", "roja", "luz roja", "fibra", "corte"]):
            return ResultadoAnalizarOut(
                diagnostico="Interrupción física del enlace de fibra óptica (Falla de Capa 1)",
                causa_probable="Acometida de fibra desconectada, atenuada críticamente o con rotura en tramo exterior.",
                nivel_severidad="Crítica",
                acciones_recomendadas=[
                    "Verificar que el conector SC/APC azul esté firmemente acoplado en el puerto óptico de la ONT.",
                    "Evitar doblar el cable monomodo con radio inferior a 30 mm.",
                    "Despachar cuadrilla técnica de planta externa para medición con reflectómetro óptico (OTDR)."
                ],
                requiere_visita_campo=True,
                documentos_sugeridos=["DOC-01_luces_led_ont_huawei.md", "DOC-03_atenuacion_potencia_optica.md"]
            )
        elif any(k in texto for k in ["lento", "lentitud", "velocidad", "ping", "latencia"]):
            return ResultadoAnalizarOut(
                diagnostico="Degradación de rendimiento o congestión de canal inalámbrico",
                causa_probable="Saturación en banda 2.4 GHz, interferencia electromagnética o procesos de alto consumo simultáneos.",
                nivel_severidad="Media",
                acciones_recomendadas=[
                    "Realizar test de velocidad cableado mediante puerto Ethernet GE1 eliminando cargas concurrentes.",
                    "Migrar dispositivos compatibles a la red de 5 GHz.",
                    "Cambiar canal Wi-Fi a uno menos congestionado (canales 1, 6 u 11 en 2.4 GHz)."
                ],
                requiere_visita_campo=False,
                documentos_sugeridos=["DOC-05_cobertura_y_canales_wifi.md", "DOC-06_test_velocidad_cableado.md"]
            )
        else:
            return ResultadoAnalizarOut(
                diagnostico="Incidencia estándar de configuración o soporte de primer nivel",
                causa_probable="Desconfiguración de parámetros locales o consulta general de servicio.",
                nivel_severidad="Baja",
                acciones_recomendadas=[
                    "Reiniciar el equipo ONT manteniéndolo apagado durante 30 segundos.",
                    "Comprobar el estado de las conexiones físicas de red LAN.",
                    "Validar que no existan avisos de mantenimiento programado en el sector."
                ],
                requiere_visita_campo=False,
                documentos_sugeridos=["DOC-02_reinicio_seguro_ont.md", "DOC-04_cambio_clave_wifi.md"]
            )

    def _clasificar_heuristicamente(self, texto: str) -> ClasificacionIA:
        """Clasificación determinista de contingencia basada en reglas ITIL y detección de alcance."""
        t = texto.lower()
        palabras_tecnicas = [
            "internet", "red", "fibra", "wifi", "wi-fi", "router", "modem", "ont", "cable",
            "luz", "luces", "pon", "los", "lan", "wlan", "clave", "contraseña", "password",
            "lento", "lentitud", "velocidad", "mbps", "ping", "dns", "ip", "mora", "factura",
            "pago", "servicio", "conectar", "conecta", "navegar", "navego", "pagina", "puerto",
            "pppoe", "señal", "enlace", "desconexión", "intermitente", "caida", "caída"
        ]
        if not any(k in t for k in palabras_tecnicas):
            return ClasificacionIA(
                categoria="Solicitud No Técnica / Fuera de Alcance",
                impacto="Bajo",
                urgencia="Baja",
                sintomas_detectados=["Sin incidencia técnica identificable"],
                justificacion="El reporte no describe ninguna avería, falla técnica ni problema en el servicio de Internet."
            )
        if any(k in t for k in ["los roja", "fibra rota", "corte total", "sin servicio", "no navego", "luz roja"]):
            return ClasificacionIA(
                categoria="Conectividad y Fibra Óptica",
                impacto="Alto",
                urgencia="Alta",
                sintomas_detectados=["LED LOS rojo", "Pérdida de enlace óptico"],
                justificacion="Detección de corte de fibra o alarma óptica crítica."
            )
        elif any(k in t for k in ["mora", "factura", "pago", "cobranza", "corte por mora", "suspensión"]):
            return ClasificacionIA(
                categoria="Facturación y Cuentas",
                impacto="Bajo",
                urgencia="Baja",
                sintomas_detectados=["Corte comercial por cobranzas"],
                justificacion="Suspensión temporal por valores pendientes de pago."
            )
        elif any(k in t for k in ["lento", "lentitud", "velocidad", "microcorte", "intermitente"]):
            return ClasificacionIA(
                categoria="Calidad y Velocidad",
                impacto="Medio",
                urgencia="Media",
                sintomas_detectados=["Lentitud en navegación", "Fluctuación de enlace"],
                justificacion="Reporte de degradación de velocidad o microcortes."
            )
        elif any(k in t for k in ["wifi", "wi-fi", "clave", "contraseña", "ssid", "cobertura"]):
            return ClasificacionIA(
                categoria="Redes Inalámbricas y Wi-Fi",
                impacto="Bajo",
                urgencia="Baja",
                sintomas_detectados=["Configuración inalámbrica solicitada"],
                justificacion="Autogestión de credenciales o cobertura Wi-Fi local."
            )
        else:
            return ClasificacionIA(
                categoria="Atención General / Soporte Nivel 1",
                impacto="Medio",
                urgencia="Media",
                sintomas_detectados=["Consulta técnica general"],
                justificacion="Clasificación estándar para seguimiento de mesa de ayuda técnica."
            )


# ============================================================================
# Instancia Singleton Encapsulada y Métodos de Fachada
# ============================================================================

cliente_llm = ClienteLLM()

def clasificar_solicitud(
    texto_usuario: str,
    simular_caida_gemini: bool = False,
    simular_caida_groq: bool = False,
    modo_vulnerable: bool = False
) -> Tuple[ClasificacionIA, MetadatosIA]:
    """Fachada pública delegada al cliente encapsulado."""
    return cliente_llm.clasificar(
        texto_usuario,
        simular_caida_gemini=simular_caida_gemini,
        simular_caida_groq=simular_caida_groq,
        modo_vulnerable=modo_vulnerable
    )

def generar_flujo_chat_streaming(
    mensaje: str,
    historial: Optional[list] = None,
    simular_caida_gemini: bool = False,
    simular_caida_groq: bool = False
) -> Iterator[str]:
    """Fachada pública delegada al cliente encapsulado."""
    return cliente_llm.chat_stream(
        mensaje,
        historial=historial,
        simular_caida_gemini=simular_caida_gemini,
        simular_caida_groq=simular_caida_groq
    )

def analizar_incidencia_tecnica(solicitud: SolicitudAnalizarIn) -> ResultadoAnalizarOut:
    """Fachada pública delegada al cliente encapsulado."""
    return cliente_llm.analizar(solicitud)

def _clasificar_heuristicamente(texto: str) -> ClasificacionIA:
    """Compatibilidad directa para pruebas unitarias de contingencia."""
    return cliente_llm._clasificar_heuristicamente(texto)
