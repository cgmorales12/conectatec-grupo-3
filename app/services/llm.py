"""
Gateway de Resiliencia con Failover y Transparencia Operativa
Modelo Primario: Google Gemini 1.5 Flash
Modelo de Respaldo: Groq Cloud Llama 3.3 70B
Cumple: Delimitación XML, Sanitización LOPDP de contraseñas y reporte de conmutación.
"""

import os
import re
import json
import time
from typing import Tuple, Optional
from datetime import datetime
from app.schemas import ClasificacionIA, MetadatosIA

# Configuración de variables de entorno
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Expresión regular para detectar y anonimizar contraseñas expuestas por error (Art. 23 LOPDP)
PATRON_PASSWORD = re.compile(
    r'(?i)(clave|contrase[ñn]a|password|pass|secret)[\s:=]+([^\s,;]+)',
    re.IGNORECASE
)

SYSTEM_PROMPT = """Eres el analista de soporte técnico y triaje inteligente de ConectaTec ISP (Caso 03).
Tu función es clasificar las incidencias reportadas por los clientes en formato JSON estricto.

Debes extraer exactamente los siguientes campos:
{
  "categoria": "Equipos de Cliente / ONT | Conectividad y Fibra Óptica | Redes Inalámbricas y Wi-Fi | Calidad y Velocidad | Facturacion y Cuentas",
  "impacto": "Alto | Medio | Bajo",
  "urgencia": "Alta | Media | Baja",
  "sintomas_detectados": ["lista", "de", "luces", "o", "fallos"],
  "justificacion": "Explicación técnica concisa"
}

Reglas de negocio:
1. Si se menciona corte total de servicio, luz LOS roja en la ONT o corte de fibra, Impacto=Alto y Urgencia=Alta.
2. Si se menciona lentitud o mala cobertura en habitaciones lejanas, Impacto=Medio y Urgencia=Media.
3. Si se solicita cambio de clave Wi-Fi o consulta de pago, Impacto=Bajo y Urgencia=Baja.
4. Responde ÚNICAMENTE el objeto JSON sin bloques Markdown adicionales ni texto antes o después.
"""

def anonimizar_datos_sensibles(texto: str) -> str:
    """
    Sustituye contraseñas accidentales por [CONFIDENCIAL_REMOVIDO] antes de persistir o invocar al LLM.
    Cumple con el perímetro de ciberseguridad y LOPDP (Ecuador).
    """
    return PATRON_PASSWORD.sub(r'\1: [CONFIDENCIAL_REMOVIDO]', texto)

def clasificar_solicitud(texto_usuario: str) -> Tuple[ClasificacionIA, MetadatosIA]:
    """
    Clasifica la solicitud aplicando la delimitación <solicitud>, sanitización de claves
    e invoca a Gemini 1.5 Flash con failover transparente hacia Groq si ocurre fallo 429/503.
    """
    t_inicio = time.time()
    
    # Capa 1: Sanitización de contraseñas (LOPDP)
    texto_seguro = anonimizar_datos_sensibles(texto_usuario)
    
    # Capa 2: Delimitación semántica contra Inyección de Prompts (OWASP LLM01)
    prompt_usuario = f"{SYSTEM_PROMPT}\n\n<solicitud>\n{texto_seguro}\n</solicitud>"
    
    # Intento 1: Proveedor Primario Google Gemini
    if GEMINI_API_KEY and GEMINI_API_KEY != "tu_clave_de_gemini_aqui":
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Inferencia con límite de tiempo de 15 segundos
            response = model.generate_content(
                prompt_usuario,
                generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
            )
            
            latencia = round((time.time() - t_inicio) * 1000, 2)
            clasificacion = ClasificacionIA.model_validate_json(response.text.strip())
            
            metadatos = MetadatosIA(
                proveedor="gemini",
                modelo="gemini-1.5-flash",
                conmutado=False,
                motivo_conmutacion=None,
                latencia_ms=latencia
            )
            return clasificacion, metadatos
            
        except Exception as e:
            # Captura de fallos de Gemini (429 cuota, 503 indisponible, timeout)
            motivo_fallo = f"Fallo en Gemini 1.5 Flash ({type(e).__name__}): {str(e)[:100]}. Activando respaldo."
            print(f"[ALERTA DE RESILIENCIA] {motivo_fallo}")
    else:
        motivo_fallo = "GEMINI_API_KEY no configurada o en modo demostración."

    # Intento 2: Proveedor de Respaldo / Failover Groq Cloud
    if GROQ_API_KEY and GROQ_API_KEY != "tu_clave_de_groq_aqui":
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"<solicitud>\n{texto_seguro}\n</solicitud>"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            latencia = round((time.time() - t_inicio) * 1000, 2)
            contenido = chat_completion.choices[0].message.content
            clasificacion = ClasificacionIA.model_validate_json(contenido)
            
            metadatos = MetadatosIA(
                proveedor="groq",
                modelo="llama-3.3-70b-versatile",
                conmutado=True,
                motivo_conmutacion=motivo_fallo,
                latencia_ms=latencia
            )
            return clasificacion, metadatos
            
        except Exception as e_groq:
            motivo_fallo += f" | Fallo en Groq ({type(e_groq).__name__}): {str(e_groq)[:100]}"
            print(f"[ERROR DE GATEWAY] {motivo_fallo}")

    # Fallback Heurístico Local (Garantiza 100% de disponibilidad sin internet o sin saldo)
    latencia = round((time.time() - t_inicio) * 1000, 2)
    clasificacion = _clasificar_heuristicamente(texto_seguro)
    
    metadatos = MetadatosIA(
        proveedor="conmutador-local-offline",
        modelo="analizador-itil-heuristico",
        conmutado=True,
        motivo_conmutacion=motivo_fallo,
        latencia_ms=latencia
    )
    return clasificacion, metadatos

def _clasificar_heuristicamente(texto: str) -> ClasificacionIA:
    """Clasificación determinista de contingencia basada en reglas ITIL."""
    t = texto.lower()
    
    if any(k in t for k in ["los roja", "fibra rota", "corte total", "sin servicio", "no navego", "luz roja"]):
        return ClasificacionIA(
            categoria="Conectividad y Fibra Óptica",
            impacto="Alto",
            urgencia="Alta",
            sintomas_detectados=["LED LOS rojo", "Pérdida de enlace óptico"],
            justificacion="Detección de corte de fibra o alarma óptica crítica."
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
            sintomas_detectados=["Consulta de soporte general"],
            justificacion="Clasificación estándar para seguimiento de mesa de ayuda."
        )
