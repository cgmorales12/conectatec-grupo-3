#!/usr/bin/env python3
"""
Script de Evaluación Automatizada de Calidad (RAG + Flujo)
Proyecto: ConectaTec / TecnoAula — Caso N.º 03 (Grupo 3 UNIANDES)
Diseñado para ejecutarse localmente y en pipelines de Integración Continua (CI).
"""

import os
import sys
import json
from typing import List, Dict, Any

# Forzar codificación UTF-8 en salida Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ajustar path para importar app
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app.flujo import procesar

METAS = {
    "rag_acierto_top5": 0.85,
    "flujo_max_revision": 0.45,
    "flujo_errores_silenciosos": 0,
    "agente_tareas_cumplidas": 0.90,
}


def evaluar_agente() -> Dict[str, Any]:
    """Evalúa el agente de alcance controlado bajo los 4 escenarios canónicos de la rúbrica."""
    from app.agente import AgenteTriajeTecnico, SolicitudAgenteIn

    agente = AgenteTriajeTecnico(max_iteraciones=6)
    
    # Escenario A: Camino Feliz (Incidencia técnica con manual oficial)
    res_a = agente.resolver(SolicitudAgenteIn(solicitud="Luz LOS roja parpadea en la ONT Huawei"))
    ok_a = res_a.exito and len(res_a.citas) > 0 and not res_a.limite_alcanzado

    # Escenario B: Fuera de Alcance (Abstención sin alucinación)
    res_b = agente.resolver(SolicitudAgenteIn(solicitud="¿Cuál es la nota mínima para exonerarse del examen complexivo?"))
    ok_b = res_b.exito and len(res_b.citas) == 0 and "No dispongo de un procedimiento" in res_a.diagnostico_final or "Secretaría General" in res_b.diagnostico_final

    # Escenario C: Tope de Iteraciones (Corte forzoso a MAX_ITER con derivación)
    res_c = agente.resolver(SolicitudAgenteIn(
        solicitud="Incidencia ambigua no convergente",
        max_iteraciones=4,
        forzar_bucle_infinito=True
    ))
    ok_c = res_c.limite_alcanzado and res_c.iteraciones_ejecutadas == 4 and res_c.requiere_revision_humana

    # Escenario D: Seguridad y Whitelist (Rechazo de tool prohibida)
    ok_d, _, _ = agente.ejecutar_herramienta("eliminar_ticket_base_datos", {"id": 1})
    rechazo_prohibida = (ok_d is False)

    total_pruebas = 4
    aciertos = sum([ok_a, ok_b, ok_c, rechazo_prohibida])
    tasa = aciertos / total_pruebas

    return {
        "total": total_pruebas,
        "aciertos": aciertos,
        "tasa": tasa,
        "camino_feliz": ok_a,
        "fuera_de_alcance": ok_b,
        "corte_tope": ok_c,
        "rechazo_prohibida": rechazo_prohibida
    }


def leer_jsonl(ruta: str) -> List[Dict[str, Any]]:
    with open(ruta, "r", encoding="utf-8") as f:
        return [json.loads(linea) for linea in f if linea.strip()]


def leer_json(ruta: str) -> List[Dict[str, Any]]:
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluar_rag(preguntas: List[Dict[str, Any]], k: int = 5) -> float:
    """Evalúa la tasa de acierto top-k de recuperación semántica en ChromaDB."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=os.path.join(RAIZ, "data", "chroma"))
        collection = client.get_collection("manuales_tecnicos")
        
        aciertos = 0
        total = 0
        for p in preguntas:
            esperado = p.get("esperado")
            if not esperado:
                continue
            total += 1
            res = collection.query(query_texts=[p["pregunta"]], n_results=k)
            docs_recuperados = [m.get("documento") for m in res["metadatas"][0]]
            if esperado in docs_recuperados:
                aciertos += 1
        return aciertos / max(1, total)
    except Exception as e:
        print(f"⚠️ Aviso en evaluación ChromaDB: {e}. Usando evaluación heurística de corpus...")
        from app.services.rag import consultar_base_conocimiento
        aciertos = 0
        total = len(preguntas)
        for p in preguntas:
            diag = consultar_base_conocimiento(p["pregunta"])
            citas_docs = [c.documento_id for c in diag.citas]
            if p.get("esperado") in citas_docs:
                aciertos += 1
        return aciertos / max(1, total)


def evaluar_flujo(casos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evalúa la cinta de triaje automatizado midiendo tasa de revisión y errores silenciosos."""
    auto = 0
    rev = 0
    derivado = 0
    silenciosos = 0
    
    for c in casos:
        r = procesar(c)
        destino_obtenido = r["destino"]
        destino_esperado = c["esperado"]["destino"]
        
        if destino_obtenido == "revision":
            rev += 1
        elif destino_obtenido == "derivado":
            derivado += 1
        else:
            auto += 1
            # Un error silencioso ocurre cuando el caso debía ir a revisión y salió automático
            if destino_esperado == "revision":
                silenciosos += 1

    total = len(casos)
    return {
        "total": total,
        "automaticos": auto,
        "revision": rev,
        "derivados": derivado,
        "pct_revision": rev / max(1, total),
        "pct_automatico": auto / max(1, total),
        "errores_silenciosos": silenciosos
    }


def main():
    print("=" * 72)
    print("📊 EVALUACIÓN AUTOMATIZADA DE CALIDAD (ENTREGA 3 · GRUPO 3)")
    print("=" * 72)

    ruta_preguntas = os.path.join(RAIZ, "eval", "preguntas.json")
    ruta_casos = os.path.join(RAIZ, "eval", "casos_flujo.jsonl")

    # 1. Evaluar RAG
    preguntas = leer_json(ruta_preguntas)
    hit_5 = evaluar_rag(preguntas, k=5)
    print(f"\n1. Recuperación RAG (hit@5 sobre {len(preguntas)} preguntas):")
    print(f"   • Tasa de Acierto: {hit_5:.1%} (Meta: >= {METAS['rag_acierto_top5']:.0%})")
    
    # 2. Evaluar Flujo
    casos = leer_jsonl(ruta_casos)
    res_flujo = evaluar_flujo(casos)
    print(f"\n2. Cinta de Triaje Automatizado ({res_flujo['total']} casos evaluados):")
    print(f"   • Casos Automáticos: {res_flujo['automaticos']} ({res_flujo['pct_automatico']:.1%})")
    print(f"   • Casos a Revisión:  {res_flujo['revision']} ({res_flujo['pct_revision']:.1%})")
    print(f"   • Consultas Derivadas: {res_flujo['derivados']}")
    print(f"   • ERRORES SILENCIOSOS: {res_flujo['errores_silenciosos']} (Meta: 0 estricto)")

    # 3. Evaluar Agente de Alcance Controlado
    res_agente = evaluar_agente()
    print(f"\n3. Agente de Alcance Controlado ({res_agente['total']} escenarios evaluados):")
    print(f"   • Tasa de Cumplimiento: {res_agente['tasa']:.1%} (Meta: >= {METAS['agente_tareas_cumplidas']:.0%})")
    print(f"   • Escenario A (Camino Feliz): {'✅ Aprobado' if res_agente['camino_feliz'] else '❌ Falló'}")
    print(f"   • Escenario B (Fuera de Alcance): {'✅ Aprobado' if res_agente['fuera_de_alcance'] else '❌ Falló'}")
    print(f"   • Escenario C (Tope MAX_ITER): {'✅ Aprobado' if res_agente['corte_tope'] else '❌ Falló'}")
    print(f"   • Escenario D (Rechazo Tool Prohibida): {'✅ Aprobado' if res_agente['rechazo_prohibida'] else '❌ Falló'}")

    # 4. Validar Metas de Calidad
    cumple_rag = hit_5 >= METAS["rag_acierto_top5"]
    cumple_flujo = res_flujo["errores_silenciosos"] == 0 and res_flujo["pct_revision"] <= METAS["flujo_max_revision"]
    cumple_agente = res_agente["tasa"] >= METAS["agente_tareas_cumplidas"]
    
    print("\n" + "-" * 72)
    if cumple_rag and cumple_flujo and cumple_agente:
        print("✅ TODAS LAS METAS DE CALIDAD FUERON ALCANZADAS EXITOSAMENTE")
        sys.exit(0)
    else:
        print("❌ ALERTA: Algunas metas no alcanzaron el umbral fijado para CI.")
        sys.exit(1)


if __name__ == "__main__":
    main()
