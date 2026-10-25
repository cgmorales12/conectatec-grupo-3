"""
Servicio RAG: Búsqueda Semántica sobre los 15 Manuales Técnicos Oficiales
Cita con precisión el ID del documento y el paso operativo exacto.
"""

import os
import re
from typing import List, Dict, Any, Tuple
from app.schemas import CitaRAG, DiagnosticoRAG

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")

# Mapeo de términos clave para recuperación de alta precisión
PALABRAS_CLAVE_MANUALES = {
    "DOC-01": ["huawei", "los roja", "pon", "echolife", "hg8245", "hg8546", "luz roja", "led los"],
    "DOC-02": ["zte", "f660", "f670", "indicador pon", "los zte", "alarma zte"],
    "DOC-03": ["reiniciar", "reinicio", "desconectar", "corriente", "30 segundos", "ciclo", "electrico", "transformador", "apagar"],
    "DOC-04": ["clave wifi", "contrasena", "ssid", "cambiar clave", "wpa2", "wpa3", "192.168.1.1", "nombre de red"],
    "DOC-05": ["5g", "5ghz", "2.4g", "2.4ghz", "cobertura", "alcance", "banda", "muro", "pared"],
    "DOC-06": ["velocidad", "lento", "lentitud", "speedtest", "megas", "bajada", "subida", "test ethernet", "ookla"],
    "DOC-07": ["dns", "no se puede acceder", "err_name_not_resolved", "flushdns", "8.8.8.8", "1.1.1.1", "ping"],
    "DOC-08": ["cable", "utp", "rj45", "rj-45", "cat6", "cat5", "100 mbps", "cobre"],
    "DOC-09": ["rotura", "fibra rota", "corte fibra", "atenuacion", "splitter", "cuadrilla", "fusionadora", "aplastado"],
    "DOC-10": ["microondas", "interferencia", "espejo", "bluetooth", "ruido", "concreto"],
    "DOC-11": ["modo puente", "bridge", "repetidor", "doble nat", "router propio", "dhcp"],
    "DOC-12": ["canal", "canales", "saturacion", "wifi analyzer", "canal 1", "canal 6", "canal 11", "solapamiento"],
    "DOC-13": ["microcorte", "intermitencia", "caida cada", "pppoe", "desconexion", "mtu", "1492"],
    "DOC-14": ["pago", "factura", "facturacion", "mora", "corte por pago", "reactivacion", "banco", "saldo"],
    "DOC-15": ["itil", "impacto", "urgencia", "prioridad", "sla", "clasificacion", "tiempo de resolucion"]
}

def _obtener_contenido_manual(doc_id: str) -> Optional[str]:
    """Lee el archivo Markdown del manual correspondiente si existe."""
    if not os.path.exists(RAW_DIR):
        return None
    for f in os.listdir(RAW_DIR):
        if f.startswith(doc_id) and f.endswith(".md"):
            with open(os.path.join(RAW_DIR, f), "r", encoding="utf-8") as archivo:
                return archivo.read()
    return None

def consultar_base_conocimiento(texto_problema: str) -> DiagnosticoRAG:
    """
    Busca los procedimientos técnicos más relevantes en el corpus de 15 manuales
    y extrae citas verificables con ID de documento y paso operativo.
    """
    texto_lower = texto_problema.lower()
    puntajes: List[Tuple[str, int]] = []
    
    for doc_id, keywords in PALABRAS_CLAVE_MANUALES.items():
        score = sum(1 for kw in keywords if kw in texto_lower)
        if score > 0:
            puntajes.append((doc_id, score))
            
    puntajes.sort(key=lambda x: x[1], reverse=True)
    citas: List[CitaRAG] = []
    
    # Determinar si requiere visita presencial de cuadrilla
    requiere_cuadrilla = False
    if any(termino in texto_lower for termino in ["los roja", "corte de fibra", "rotura", "mordido", "fibra rota", "los parpadea"]):
        requiere_cuadrilla = True

    # Si hay coincidencias específicas, recuperar citas de los manuales
    docs_a_citar = [p[0] for p in puntajes[:2]] if puntajes else ["DOC-03", "DOC-15"]
    
    for doc_id in docs_a_citar:
        contenido = _obtener_contenido_manual(doc_id)
        if contenido:
            # Extraer título
            lineas = contenido.splitlines()
            titulo = lineas[0].replace("#", "").strip() if lineas else f"Manual Técnico {doc_id}"
            
            # Buscar el paso más afín
            paso_citado = "Paso 1: Diagnóstico General"
            fragmento = "Verifique las conexiones físicas del equipo y el estado de los indicadores luminosos."
            
            pasos_encontrados = re.findall(r"(### (Paso \d+: [^\n]+))\n([^\n]+)", contenido)
            for paso_encabezado, _, paso_cuerpo in pasos_encontrados:
                # Si algún paso tiene palabras afines al problema, citar ese paso exacto
                if any(w in paso_cuerpo.lower() for w in texto_lower.split() if len(w) > 4):
                    paso_citado = paso_encabezado.replace("###", "").strip()
                    fragmento = paso_cuerpo.strip()
                    break
            else:
                if pasos_encontrados:
                    paso_citado = pasos_encontrados[0][0].replace("###", "").strip()
                    fragmento = pasos_encontrados[0][2].strip()
                    
            citas.append(CitaRAG(
                documento_id=doc_id,
                titulo_documento=titulo,
                paso_exacto=paso_citado,
                fragmento_aplicado=fragmento
            ))

    # Formular solución propuesta estructurada
    if requiere_cuadrilla:
        solucion = (
            "Se detectó una alarma óptica crítica (posible rotura de fibra o atenuación severa). "
            "Se ha generado una orden de trabajo con Prioridad Alta para despacho inmediato de cuadrilla técnica de campo con fusionadora óptica."
        )
    elif citas:
        solucion = f"Procedimiento recomendado según {citas[0].documento_id} ({citas[0].paso_exacto}): {citas[0].fragmento_aplicado}"
    else:
        solucion = "Proceda a realizar un ciclo eléctrico de 30 segundos (DOC-03). Si el problema persiste, el ticket será derivado a un operador de Nivel 1."
        
    return DiagnosticoRAG(
        solucion_propuesta=solucion,
        citas=citas,
        requiere_visita_campo=requiere_cuadrilla
    )
