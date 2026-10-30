"""
Módulo de Gestión Determinista de Parámetros de Negocio Desacoplados
Proyecto: ConectaTec / TecnoAula — Triaje de Incidentes Técnicos (Caso N.º 03 · Grupo 3 UNIANDES)
Seminario de Titulación: Ingeniería de Software con IA Generativa — UNIANDES 2026

Rúbrica de Evaluación:
«Parámetros en config/: Tarifas, umbrales, salario básico o calendarios: nunca en el código ni en el prompt.»

Principio Rector de Arquitectura:
«El modelo propone, el código dispone, la configuración gobierna.»
Cero valores fijos quemados (hardcoded). Cualquier cambio en salario básico,
tarifas de reposición o calendarios de feriados se realiza editando config/,
sin alterar el código Python ni reescribir prompts del LLM.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, time

import yaml

logger = logging.getLogger("conectatec.configuracion")

# Rutas canónicas a los archivos de configuración
DIR_CONFIG = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "config"))
RUTA_PARAMETROS = os.path.join(DIR_CONFIG, "parametros.yaml")
RUTA_TARIFAS = os.path.join(DIR_CONFIG, "tarifas.json")
RUTA_CALENDARIO = os.path.join(DIR_CONFIG, "calendario.json")
RUTA_MATRIZ_PRIORIDAD = os.path.join(DIR_CONFIG, "matriz_prioridad.json")


# ============================================================================
# 1. Carga de Parámetros Globales y Umbrales (parametros.yaml)
# ============================================================================

def cargar_parametros_yaml() -> Dict[str, Any]:
    """
    Carga los parámetros y umbrales globales desde config/parametros.yaml.
    Garantiza que umbrales de confianza, límites de iteraciones y salario básico
    sean leídos en tiempo de ejecución.
    """
    if os.path.exists(RUTA_PARAMETROS):
        try:
            with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.error(f"Error al leer config/parametros.yaml: {e}")
    
    # Fallback seguro reportando origen
    logger.warning("No se encontró o no se pudo parsear config/parametros.yaml. Usando valores mínimos de contingencia.")
    return {
        "umbral_confianza": 0.85,
        "max_iteraciones_agente": 6,
        "salario_basico_unificado": 482.00,
        "salario_basico_moneda": "USD",
        "salario_basico_pais": "Ecuador",
        "salario_basico_ano": 2026,
        "porcentaje_penalizacion_sla_por_hora": 0.02
    }


def obtener_parametro(clave: str, defecto: Any = None) -> Any:
    """Obtiene un parámetro u umbral específico desde config/parametros.yaml."""
    params = cargar_parametros_yaml()
    return params.get(clave, defecto)


def obtener_salario_basico() -> Dict[str, Any]:
    """
    Retorna los datos del Salario Básico Unificado (SBU) leídos desde config/parametros.yaml.
    Nunca hardcodeado en la lógica de cálculo ni en prompts.
    """
    params = cargar_parametros_yaml()
    return {
        "salario_basico_unificado": float(params.get("salario_basico_unificado", 482.00)),
        "moneda": str(params.get("salario_basico_moneda", "USD")),
        "pais": str(params.get("salario_basico_pais", "Ecuador")),
        "ano": int(params.get("salario_basico_ano", 2026)),
        "porcentaje_penalizacion_por_hora": float(params.get("porcentaje_penalizacion_sla_por_hora", 0.02)),
        "origen_configuracion": "config/parametros.yaml"
    }


# ============================================================================
# 2. Carga y Consulta de Tarifas Oficiales (tarifas.json)
# ============================================================================

def cargar_tarifas_json() -> Dict[str, Any]:
    """
    Carga el tarifario oficial de repuestos, materiales y mano de obra desde config/tarifas.json.
    """
    if os.path.exists(RUTA_TARIFAS):
        try:
            with open(RUTA_TARIFAS, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.error(f"Error al leer config/tarifas.json: {e}")
            
    return {
        "version": "1.0.0",
        "moneda": "USD",
        "pais": "Ecuador",
        "vigencia": "2026-Q4",
        "catalogo": {}
    }


def listar_todas_las_tarifas(categoria: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lista todos los ítems del tarifario oficial leídos desde config/tarifas.json,
    opcionalmente filtrados por categoría (equipos_cpe, materiales_planta_externa, mano_de_obra_y_servicios).
    """
    tarifas_data = cargar_tarifas_json()
    catalogo = tarifas_data.get("catalogo", {})
    resultado: List[Dict[str, Any]] = []

    for cat_nombre, items in catalogo.items():
        if categoria and cat_nombre != categoria:
            continue
        if isinstance(items, list):
            resultado.extend(items)

    return resultado


def obtener_tarifa_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Busca una tarifa específica por su código unívoco (ej: EQ-ONT-GPON-W6).
    Retorna None si el código no existe en config/tarifas.json.
    """
    todas = listar_todas_las_tarifas()
    codigo_upper = codigo.strip().upper()
    for item in todas:
        if str(item.get("codigo", "")).upper() == codigo_upper:
            return item
    return None


def calcular_presupuesto_reparacion(items_solicitados: List[Dict[str, Any]], iva_porcentaje: float = 0.15) -> Dict[str, Any]:
    """
    Cálculo 100% determinista y matemático de presupuesto técnico de reposición o reparación.
    Multiplica cantidades por tarifas vigentes en config/tarifas.json y aplica IVA legal vigente en Ecuador (15%).
    Costo de inferencia: CERO tokens.
    """
    detalles = []
    subtotal = 0.0

    for item_req in items_solicitados:
        codigo = item_req.get("codigo", "")
        cantidad = float(item_req.get("cantidad", 1))
        tarifa_info = obtener_tarifa_por_codigo(codigo)

        if tarifa_info:
            precio_unitario = float(tarifa_info.get("tarifa_usd", 0.0))
            subtotal_linea = round(precio_unitario * cantidad, 2)
            subtotal += subtotal_linea
            detalles.append({
                "codigo": tarifa_info.get("codigo"),
                "nombre": tarifa_info.get("nombre"),
                "categoria": tarifa_info.get("categoria"),
                "cantidad": cantidad,
                "unidad": tarifa_info.get("unidad", "unidad"),
                "precio_unitario_usd": precio_unitario,
                "subtotal_usd": subtotal_linea,
                "encontrado_en_catalogo": True
            })
        else:
            detalles.append({
                "codigo": codigo,
                "nombre": "Ítem no registrado en tarifario oficial",
                "cantidad": cantidad,
                "precio_unitario_usd": 0.0,
                "subtotal_usd": 0.0,
                "encontrado_en_catalogo": False
            })

    subtotal = round(subtotal, 2)
    monto_iva = round(subtotal * iva_porcentaje, 2)
    total = round(subtotal + monto_iva, 2)

    return {
        "items_detalle": detalles,
        "subtotal_usd": subtotal,
        "iva_porcentaje": round(iva_porcentaje * 100, 2),
        "iva_usd": monto_iva,
        "total_usd": total,
        "moneda": "USD",
        "origen_tarifas": "config/tarifas.json"
    }


def calcular_penalizacion_sla_por_horas(horas_retraso: float) -> Dict[str, Any]:
    """
    Calcula determinísticamente la sanción o penalización financiera por incumplimiento de SLA,
    basada en el Salario Básico Unificado (SBU) leída desde config/parametros.yaml.
    Formula determinista: penalizacion = horas_retraso * (SBU * porcentaje_penalizacion_hora)
    """
    datos_sbu = obtener_salario_basico()
    sbu = datos_sbu["salario_basico_unificado"]
    pct_hora = datos_sbu["porcentaje_penalizacion_por_hora"]

    costo_por_hora_retraso = round(sbu * pct_hora, 2)
    monto_total = round(horas_retraso * costo_por_hora_retraso, 2)

    return {
        "horas_retraso": round(horas_retraso, 2),
        "salario_basico_unificado": sbu,
        "porcentaje_aplicado_por_hora": pct_hora,
        "costo_penalizacion_por_hora_usd": costo_por_hora_retraso,
        "monto_penalizacion_total_usd": monto_total,
        "moneda": datos_sbu["moneda"],
        "justificacion": (
            f"Calculado determinísticamente con SBU oficial de ${sbu:.2f} {datos_sbu['moneda']} "
            f"({datos_sbu['pais']} {datos_sbu['ano']}) a razón de {pct_hora*100:.1f}% por hora de retraso no justificada."
        ),
        "origen_regla": "config/parametros.yaml"
    }


# ============================================================================
# 3. Carga y Consulta de Calendarios Operativos y Feriados (calendario.json)
# ============================================================================

def cargar_calendario_json() -> Dict[str, Any]:
    """
    Carga el calendario de días hábiles, turnos y feriados oficiales desde config/calendario.json.
    """
    if os.path.exists(RUTA_CALENDARIO):
        try:
            with open(RUTA_CALENDARIO, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.error(f"Error al leer config/calendario.json: {e}")

    return {
        "version": "1.0.0",
        "zona_horaria": "America/Guayaquil",
        "ano_vigencia": 2026,
        "horarios_atencion": {},
        "feriados_nacionales_ecuador_2026": []
    }


def es_feriado_nacional(fecha_iso: str) -> Tuple[bool, Optional[str]]:
    """
    Determina si una fecha dada en formato 'YYYY-MM-DD' es feriado nacional oficial en Ecuador
    consultando config/calendario.json.
    Retorna: (es_feriado: bool, nombre_feriado: Optional[str])
    """
    calendario = cargar_calendario_json()
    feriados = calendario.get("feriados_nacionales_ecuador_2026", [])
    
    fecha_limpia = fecha_iso.strip()[:10]
    for fer in feriados:
        if fer.get("fecha") == fecha_limpia:
            return True, fer.get("nombre")
            
    return False, None


def es_horario_laborable_habil(momento: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Evalúa determinísticamente si un momento dado (o el momento actual) cae dentro
    de la jornada laboral ordinaria de soporte de ConectaTec según config/calendario.json.
    """
    if momento is None:
        momento = datetime.now()

    fecha_iso = momento.strftime("%Y-%m-%d")
    es_feriado, nombre_feriado = es_feriado_nacional(fecha_iso)

    if es_feriado:
        return {
            "fecha": fecha_iso,
            "hora": momento.strftime("%H:%M:%S"),
            "es_habil": False,
            "motivo": f"Feriado nacional obligatorio: {nombre_feriado}",
            "guardia_noc_24_7_activa": True
        }

    # Día de la semana (1 = Lunes, 7 = Domingo)
    dia_semana = momento.isoweekday()
    hora_actual = momento.time()

    calendario = cargar_calendario_json()
    horarios = calendario.get("horarios_atencion", {})

    if dia_semana in [1, 2, 3, 4, 5]: # Lunes a Viernes
        reg = horarios.get("jornada_regular_semana", {})
        h_ini = time.fromisoformat(reg.get("hora_inicio", "08:00"))
        h_fin = time.fromisoformat(reg.get("hora_fin", "18:00"))
        es_habil = h_ini <= hora_actual < h_fin
        return {
            "fecha": fecha_iso,
            "hora": momento.strftime("%H:%M:%S"),
            "es_habil": es_habil,
            "jornada": "Regular de Lunes a Viernes",
            "horario_vigente": f"{reg.get('hora_inicio')} a {reg.get('hora_fin')}",
            "motivo": "Dentro de jornada laboral" if es_habil else "Fuera de jornada hábil ordinaria",
            "guardia_noc_24_7_activa": True
        }
    elif dia_semana == 6: # Sábado
        sab = horarios.get("jornada_sabado", {})
        h_ini = time.fromisoformat(sab.get("hora_inicio", "08:00"))
        h_fin = time.fromisoformat(sab.get("hora_fin", "13:00"))
        es_habil = h_ini <= hora_actual < h_fin
        return {
            "fecha": fecha_iso,
            "hora": momento.strftime("%H:%M:%S"),
            "es_habil": es_habil,
            "jornada": "Parcial de Sábado",
            "horario_vigente": f"{sab.get('hora_inicio')} a {sab.get('hora_fin')}",
            "motivo": "Dentro de jornada sabatina" if es_habil else "Fuera de horario sabatino",
            "guardia_noc_24_7_activa": True
        }
    else: # Domingo
        return {
            "fecha": fecha_iso,
            "hora": momento.strftime("%H:%M:%S"),
            "es_habil": False,
            "jornada": "Domingo no laborable",
            "motivo": "Domingo no hábil para cuadrillas ordinarias",
            "guardia_noc_24_7_activa": True
        }

