"""
Capa de Persistencia: Repositorio SQLite Parametrizado
Cumple: Cero inyecciones SQL mediante consultas con marcador '?' (OWASP)
"""

import sqlite3
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DB_DIR, "conectatec.db")

def _obtener_conexion():
    """Retorna una conexión activa a la base de datos SQLite."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    """Crea la tabla de tickets si no existe y aplica migraciones automáticas."""
    conn = _obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_codigo TEXT UNIQUE NOT NULL,
            fecha_creacion TEXT NOT NULL,
            nombre_cliente TEXT NOT NULL,
            email_cliente TEXT NOT NULL,
            descripcion_problema TEXT NOT NULL,
            categoria TEXT NOT NULL,
            impacto TEXT NOT NULL,
            urgencia TEXT NOT NULL,
            prioridad TEXT NOT NULL,
            sla_minutos INTEGER NOT NULL,
            descripcion_sla TEXT NOT NULL,
            solucion_propuesta TEXT NOT NULL,
            citas_json TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'nuevo',
            requiere_revision_humana INTEGER NOT NULL DEFAULT 0,
            proveedor_ia TEXT NOT NULL,
            modelo_ia TEXT NOT NULL,
            conmutado INTEGER NOT NULL DEFAULT 0,
            motivo_conmutacion TEXT,
            latencia_ms REAL,
            justificacion TEXT,
            sintomas_json TEXT
        )
    """)
    # Migración retrocompatible para tablas preexistentes
    columnas = [col[1] for col in cursor.execute("PRAGMA table_info(tickets)").fetchall()]
    if "justificacion" not in columnas:
        cursor.execute("ALTER TABLE tickets ADD COLUMN justificacion TEXT")
    if "sintomas_json" not in columnas:
        cursor.execute("ALTER TABLE tickets ADD COLUMN sintomas_json TEXT")
    conn.commit()
    conn.close()

# Asegurar inicialización al importar el módulo
inicializar_bd()


def guardar_ticket(datos: Dict[str, Any]) -> int:
    """Inserta un nuevo ticket en la base de datos de forma parametrizada."""
    conn = _obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tickets (
            ticket_codigo, fecha_creacion, nombre_cliente, email_cliente,
            descripcion_problema, categoria, impacto, urgencia, prioridad,
            sla_minutos, descripcion_sla, solucion_propuesta, citas_json,
            estado, requiere_revision_humana, proveedor_ia, modelo_ia,
            conmutado, motivo_conmutacion, latencia_ms, justificacion, sintomas_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos["ticket_codigo"],
        datos["fecha_creacion"],
        datos["nombre_cliente"],
        datos["email_cliente"],
        datos["descripcion_problema"],
        datos["categoria"],
        datos["impacto"],
        datos["urgencia"],
        datos["prioridad"],
        datos["sla_minutos"],
        datos["descripcion_sla"],
        datos["solucion_propuesta"],
        json.dumps(datos.get("citas", [])),
        datos.get("estado", "nuevo"),
        1 if datos.get("requiere_revision_humana") else 0,
        datos["metadatos_ia"]["proveedor"],
        datos["metadatos_ia"]["modelo"],
        1 if datos["metadatos_ia"]["conmutado"] else 0,
        datos["metadatos_ia"].get("motivo_conmutacion"),
        datos["metadatos_ia"].get("latencia_ms"),
        datos.get("justificacion"),
        json.dumps(datos.get("sintomas_detectados", []))
    ))
    
    nuevo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return nuevo_id

def listar_tickets() -> List[Dict[str, Any]]:
    """Recupera todos los tickets registrados en la base de datos excluyendo campos internos."""
    conn = _obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    tickets = []
    for r in rows:
        t_raw = dict(r)
        citas_data = json.loads(t_raw["citas_json"]) if t_raw.get("citas_json") else []
        sintomas_data = json.loads(t_raw["sintomas_json"]) if t_raw.get("sintomas_json") else []
        
        ticket_limpio = {
            "id": t_raw["id"],
            "ticket_codigo": t_raw["ticket_codigo"],
            "fecha_creacion": t_raw["fecha_creacion"],
            "nombre_cliente": t_raw["nombre_cliente"],
            "email_cliente": t_raw["email_cliente"],
            "descripcion_problema": t_raw["descripcion_problema"],
            "categoria": t_raw["categoria"],
            "impacto": t_raw["impacto"],
            "urgencia": t_raw["urgencia"],
            "prioridad": t_raw["prioridad"],
            "sla_minutos": t_raw["sla_minutos"],
            "descripcion_sla": t_raw["descripcion_sla"],
            "solucion_propuesta": t_raw["solucion_propuesta"],
            "citas": citas_data,
            "estado": t_raw["estado"],
            "requiere_revision_humana": bool(t_raw["requiere_revision_humana"]),
            "justificacion": t_raw.get("justificacion") or "Clasificación generada automáticamente según políticas y matriz ITIL.",
            "sintomas_detectados": sintomas_data,
            "metadatos_ia": {
                "proveedor": t_raw["proveedor_ia"],
                "modelo": t_raw["modelo_ia"],
                "conmutado": bool(t_raw["conmutado"]),
                "motivo_conmutacion": t_raw["motivo_conmutacion"],
                "latencia_ms": t_raw["latencia_ms"]
            }
        }
        tickets.append(ticket_limpio)
    return tickets

def actualizar_estado_ticket(ticket_id: int, nuevo_estado: str) -> bool:
    """Actualiza el estado de un ticket de forma parametrizada."""
    conn = _obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET estado = ? WHERE id = ?", (nuevo_estado, ticket_id))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()
    return afectados > 0
