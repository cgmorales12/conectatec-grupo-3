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
    """Crea la tabla de tickets si no existe."""
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
            latencia_ms REAL
        )
    """)
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
            conmutado, motivo_conmutacion, latencia_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        datos["metadatos_ia"].get("latencia_ms")
    ))
    
    nuevo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return nuevo_id

def listar_tickets() -> List[Dict[str, Any]]:
    """Recupera todos los tickets registrados en la base de datos."""
    conn = _obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    tickets = []
    for r in rows:
        t = dict(r)
        t["citas"] = json.loads(t["citas_json"])
        t["requiere_revision_humana"] = bool(t["requiere_revision_humana"])
        t["metadatos_ia"] = {
            "proveedor": t["proveedor_ia"],
            "modelo": t["modelo_ia"],
            "conmutado": bool(t["conmutado"]),
            "motivo_conmutacion": t["motivo_conmutacion"],
            "latencia_ms": t["latencia_ms"]
        }
        tickets.append(t)
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
