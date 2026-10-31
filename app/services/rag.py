from __future__ import annotations
"""
Servicio RAG: Búsqueda Semántica sobre los 15 Manuales Técnicos Oficiales en ChromaDB
Cumple: Cita con precisión el ID del documento y el paso operativo exacto desde la base vectorial persistente.
Autor: Luis Fernando Ribera Alajo (Builder / Arquitectura — GitHub: fernandolribera)
Revisión de Seguridad: Amalia Geoconda Iguasnia Escobar (QA / Seguridad — GitHub: Geocoiguasnia76)
"""

import os
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from app.schemas import CitaRAG, DiagnosticoRAG

logger = logging.getLogger("conectatec.rag")

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")

# Mapeo de términos clave para recuperación de respaldo determinista (fallback)
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

# Términos que disparan orden de trabajo presencial (cuadrilla de planta externa)
TERMINOS_DESPACHO_PRESENCIAL = [
    "los roja", "luz roja", "corte de fibra", "rotura", "mordido",
    "fibra rota", "los parpadea", "cable colgando", "cable en el piso",
    "humo blanco", "plástico quemado", "rack quemado", "splitter", "atenuacion severa"
]

# Términos para el protocolo oficial de abstención (misión de silencio determinista)
TERMINOS_ABSTENCION_EXTERNA = [
    "complexivo", "comedor", "matrícula", "matricula", "almuerzo",
    "llueve", "clima", "nómina", "nomina", "sueldo", "hackear", "hack",
    "menu ejecutivo", "menú ejecutivo", "materia", "profesor", "aula magna"
]

_cliente_chroma = None
_coleccion_chroma = None
_intento_inicializacion_chroma = False


def _obtener_coleccion_chroma():
    """Inicializa y retorna la colección persistente de ChromaDB."""
    global _cliente_chroma, _coleccion_chroma, _intento_inicializacion_chroma
    if _coleccion_chroma is not None:
        return _coleccion_chroma
    if _intento_inicializacion_chroma and _coleccion_chroma is None:
        return None

    _intento_inicializacion_chroma = True
    try:
        import chromadb
        if os.path.exists(CHROMA_DIR):
            _cliente_chroma = chromadb.PersistentClient(path=CHROMA_DIR)
            cols = [c.name for c in _cliente_chroma.list_collections()]
            nombre_col = "manuales_tecnicos" if "manuales_tecnicos" in cols else (cols[0] if cols else None)
            if nombre_col:
                _coleccion_chroma = _cliente_chroma.get_collection(nombre_col)
                logger.info("ChromaDB conectado con éxito a la colección '%s' (%d fragmentos).", nombre_col, _coleccion_chroma.count())
    except Exception as exc:
        logger.warning("No se pudo conectar a ChromaDB (%s). Se usará motor semántico de respaldo.", exc)
        _coleccion_chroma = None

    return _coleccion_chroma


def _obtener_contenido_manual(doc_id: str) -> Optional[str]:
    """Lee el archivo Markdown del manual correspondiente en data/raw si existe."""
    if not os.path.exists(RAW_DIR):
        return None
    for f in os.listdir(RAW_DIR):
        if f.startswith(doc_id) and f.endswith(".md"):
            with open(os.path.join(RAW_DIR, f), "r", encoding="utf-8") as archivo:
                return archivo.read()
    return None


def buscar_solucion(
    categoria: Optional[str] = None,
    texto: str = "",
    top_k: int = 3,
    simular_caida_rag: bool = False
) -> DiagnosticoRAG:
    """
    Herramienta oficial de búsqueda de soluciones técnicas sobre los 15 manuales.
    Consulta directamente la colección vectorial persistente de ChromaDB ('manuales_tecnicos').
    
    Parámetros:
        categoria: Categoría ITIL opcional para filtrado guiado.
        texto: Texto descriptivo de la incidencia técnica.
        top_k: Número de fragmentos más afines a recuperar (por defecto 3).
        simular_caida_rag: Bandera de Chaos Engineering para contingencia.
    """
    if simular_caida_rag:
        logger.info("[CHAOS ENGINEERING] Simulación de desconexión inducida del corpus RAG.")
        return DiagnosticoRAG(
            solucion_propuesta=(
                "⚠️ [CONTINGENCIA RAG ACTIVADA] El repositorio documental de los 15 manuales técnicos "
                "se encuentra temporalmente fuera de línea por simulación de fallo. No es posible brindar autoatención guiada de Nivel 1. "
                "El incidente ha sido derivado a Nivel 2 para diagnóstico y atención directa por personal técnico humano."
            ),
            citas=[],
            requiere_visita_campo=False
        )

    texto_lower = (texto or "").lower().strip()

    # 1. Regla de Silencio Determinista y Abstención (Zero-Hallucination)
    # 1.1 Solicitudes maliciosas o de vulneración de seguridad: Abstención obligatoria inmediata
    es_adversarial = any(h in texto_lower for h in ["hackear", "hack", "crackear", "vulnerar", "piratear", "sniffear"])

    # 1.2 Detecta consultas ajenas a la infraestructura técnica de telecomunicaciones / campus
    terminos_ti = ["los", "ont", "router", "fibra", "wifi", "wi-fi", "cable", "red", "ethernet", "internet", "pon", "dns", "lan"]
    tiene_termino_ti = any(t in texto_lower for t in terminos_ti)
    es_fuera_de_alcance = (any(w in texto_lower for w in TERMINOS_ABSTENCION_EXTERNA) and not tiene_termino_ti) or es_adversarial

    if es_fuera_de_alcance or (len(texto_lower) < 4 and not tiene_termino_ti):
        return DiagnosticoRAG(
            solucion_propuesta=(
                "No dispongo de un procedimiento técnico registrado para esta situación en los 15 manuales oficiales de ConectaTec. "
                "La consulta no describe ninguna avería técnica ni falla en la infraestructura de Internet o telecomunicaciones. "
                "No se requiere despacho de cuadrilla ni manipulación de equipos. "
                "Orientación al usuario: Si su solicitud corresponde a trámites administrativos o académicos (como notas, matrículas o certificaciones), "
                "por favor acuda a Secretaría General o al portal institucional de autoservicio. "
                "Si experimenta problemas de conectividad o luces anómalas en el módem/ONT (POWER, PON, LOS, LAN), por favor descríbalos detalladamente."
            ),
            citas=[],
            requiere_visita_campo=False
        )

    # 2. Evaluación de Alarma Crítica Física (Despacho presencial)
    requiere_cuadrilla = (
        any(termino in texto_lower for termino in TERMINOS_DESPACHO_PRESENCIAL) or
        ("los" in texto_lower and "roj" in texto_lower) or
        ("los" in texto_lower and "parpade" in texto_lower)
    )

    # 3. Consulta a la Colección Vectorial Persistente de ChromaDB
    coleccion = _obtener_coleccion_chroma()
    citas: List[CitaRAG] = []
    docs_recuperados = []

    if coleccion is not None:
        try:
            # Query semántico directo a ChromaDB
            filtro_where = {"categoria": categoria} if categoria else None
            res_chroma = None
            try:
                if filtro_where:
                    res_chroma = coleccion.query(query_texts=[texto], n_results=max(top_k, 3), where=filtro_where)
            except Exception:
                res_chroma = None

            if not res_chroma or not res_chroma.get("ids") or len(res_chroma["ids"][0]) == 0:
                res_chroma = coleccion.query(query_texts=[texto], n_results=max(top_k, 3))

            if res_chroma and res_chroma.get("metadatas") and len(res_chroma["metadatas"][0]) > 0:
                metas = res_chroma["metadatas"][0]
                docs = res_chroma["documents"][0]
                dists = res_chroma.get("distances", [[0.0] * len(metas)])[0]

                for meta, doc_texto, dist in zip(metas, docs, dists):
                    doc_id = meta.get("documento", "DOC-01")
                    if doc_id not in docs_recuperados:
                        docs_recuperados.append(doc_id)
                        
                        titulo_doc = f"Manual Oficial {doc_id}"
                        # Extraer título real si está disponible
                        contenido_raw = _obtener_contenido_manual(doc_id)
                        if contenido_raw:
                            lineas = contenido_raw.splitlines()
                            if lineas:
                                titulo_doc = lineas[0].replace("#", "").strip()

                        paso = meta.get("sección") or meta.get("procedimiento") or "Paso 1: Diagnóstico General"
                        url_canon = meta.get("url") or f"https://soporte.conectatec.edu.ec/manuales/{doc_id.lower()}"
                        vigencia = meta.get("vigencia") or "v3.2 - Octubre 2026"
                        
                        # Limpiar fragmento
                        frag = doc_texto.strip()
                        if "—" in frag:
                            frag = frag.split("—", 1)[-1].strip()

                        citas.append(CitaRAG(
                            documento_id=doc_id,
                            titulo_documento=titulo_doc,
                            paso_exacto=paso,
                            fragmento_aplicado=frag[:300],
                            vigencia=vigencia,
                            url=url_canon
                        ))
                    if len(citas) >= top_k:
                        break
        except Exception as err_query:
            logger.warning("Falla al consultar ChromaDB: %s. Ejecutando fallback determinista.", err_query)
            citas = []

    # 4. Fallback Determinista sobre data/raw (por si ChromaDB no estuviera disponible)
    if not citas:
        puntajes: List[Tuple[str, int]] = []
        for doc_id, keywords in PALABRAS_CLAVE_MANUALES.items():
            score = sum(1 for kw in keywords if kw in texto_lower)
            if score > 0:
                puntajes.append((doc_id, score))
        puntajes.sort(key=lambda x: x[1], reverse=True)

        docs_a_citar = [p[0] for p in puntajes[:top_k]] if puntajes else (["DOC-01"] if requiere_cuadrilla else [])

        if not docs_a_citar and not requiere_cuadrilla:
            return DiagnosticoRAG(
                solucion_propuesta=(
                    "No dispongo de un procedimiento técnico registrado para esta situación en los 15 manuales oficiales de ConectaTec. "
                    "La consulta no describe ninguna avería técnica ni falla en la infraestructura de Internet o telecomunicaciones. "
                    "No se requiere despacho de cuadrilla ni manipulación de equipos. "
                    "Orientación al usuario: Si su solicitud corresponde a trámites administrativos o académicos (como notas, matrículas o certificaciones), "
                    "por favor acuda a Secretaría General o al portal institucional de autoservicio. "
                    "Si experimenta problemas de conectividad o luces anómalas en el módem/ONT (POWER, PON, LOS, LAN), por favor descríbalos detalladamente."
                ),
                citas=[],
                requiere_visita_campo=False
            )

        for doc_id in docs_a_citar:
            contenido = _obtener_contenido_manual(doc_id)
            if contenido:
                lineas = contenido.splitlines()
                titulo = lineas[0].replace("#", "").strip() if lineas else f"Manual Técnico {doc_id}"
                paso_citado = "Paso 1: Diagnóstico General"
                fragmento = "Verifique las conexiones físicas del equipo y el estado de los indicadores luminosos."

                pasos_encontrados = re.findall(r"(### (Paso \d+: [^\n]+))\n([^\n]+)", contenido)
                for paso_encabezado, _, paso_cuerpo in pasos_encontrados:
                    if any(w in paso_cuerpo.lower() for w in texto_lower.split() if len(w) > 4):
                        paso_citado = paso_encabezado.replace("###", "").strip()
                        fragmento = paso_cuerpo.strip()
                        break
                else:
                    if pasos_encontrados:
                        paso_citado = pasos_encontrados[0][0].replace("###", "").strip()
                        fragmento = pasos_encontrados[0][2].strip()

                vig_match = re.search(r"\*\*(?:Versión\s*/\s*Vigencia|Vigencia):\*\*\s*(.+)", contenido)
                vigencia = vig_match.group(1).strip() if vig_match else "v3.2 - Octubre 2026"
                url_canon = f"https://soporte.conectatec.edu.ec/manuales/{doc_id.lower()}"

                citas.append(CitaRAG(
                    documento_id=doc_id,
                    titulo_documento=titulo,
                    paso_exacto=paso_citado,
                    fragmento_aplicado=fragmento,
                    vigencia=vigencia,
                    url=url_canon
                ))

    # 5. Formular Solución Propuesta Determinista
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


def consultar_base_conocimiento(texto_problema: str, simular_caida_rag: bool = False) -> DiagnosticoRAG:
    """
    Función de compatibilidad: busca en ChromaDB sobre los 15 manuales técnicos oficiales.
    """
    return buscar_solucion(categoria=None, texto=texto_problema, top_k=3, simular_caida_rag=simular_caida_rag)
