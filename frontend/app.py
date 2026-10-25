"""
Frontend Streamlit - ConectaTec (Caso 03 · Grupo 3 UNIANDES)
Tablero Kanban de Tickets y Formulario de Soporte Técnico
Ejecutar con: streamlit run frontend/app.py
"""

import streamlit as st
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ConectaTec · Tablero de Triaje ISP",
    page_icon="⚡",
    layout="wide"
)

# Cabecera Institucional
st.title("⚡ ConectaTec · Triaje Inteligente de Soporte ISP")
st.caption("Caso N.º 03 · Grupo 3 UNIANDES | Christian Morales · Fernando Ribera · Geoconda Iguasnia")

# Verificación de salud y estado del proveedor LLM
try:
    res_salud = requests.get(f"{API_BASE_URL}/v1/salud", timeout=2)
    if res_salud.status_code == 200:
        st.success("🟢 Backend FastAPI Conectado | Base de Datos: SQLite | IA: Gemini 1.5 Flash (Respaldo: Groq)")
    else:
        st.warning("🟠 Backend en línea pero con advertencia de estado.")
except Exception:
    st.error("🔴 Backend desconectado. Asegúrate de ejecutar: uvicorn app.main:app --reload")

# Layout de dos columnas
col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.subheader("📝 Ingreso de Reporte")
    with st.form("form_reporte"):
        nombre = st.text_input("Nombre del Abonado", placeholder="Ej. Juan Perez")
        email = st.text_input("Correo Electrónico", placeholder="juan.perez@example.com")
        codigo = st.text_input("Código de Cliente (Opcional)", placeholder="CLI-1024")
        descripcion = st.text_area(
            "Descripción del Problema",
            placeholder="Describa la falla, luces del router o problema de navegación...",
            height=120
        )
        enviado = st.form_submit_button("⚡ Clasificar con IA y Crear Ticket", use_container_width=True)

    if enviado:
        if len(descripcion.strip()) < 10:
            st.error("La descripción debe tener al menos 10 caracteres.")
        else:
            payload = {
                "nombre_cliente": nombre,
                "email_cliente": email,
                "codigo_abonado": codigo if codigo else None,
                "descripcion_problema": descripcion
            }
            try:
                res = requests.post(f"{API_BASE_URL}/v1/tickets/clasificar", json=payload, timeout=20)
                if res.status_code == 201:
                    t = res.json()
                    st.success(f"Ticket creado: **{t['ticket_codigo']}** | Prioridad: **{t['prioridad']}**")
                    if t["metadatos_ia"]["conmutado"]:
                        st.warning("🟠 Atendido por Respaldo Groq (Gemini no disponible).")
                    st.rerun()
                else:
                    st.error(f"Error ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"Error de comunicación con API: {e}")

with col_der:
    st.subheader("📋 Tablero Kanban de Incidentes (ITIL 4)")
    
    # Obtener tickets desde la API
    tickets = []
    try:
        res_t = requests.get(f"{API_BASE_URL}/v1/tickets", timeout=3)
        if res_t.status_code == 200:
            tickets = res_t.json().get("tickets", [])
    except Exception:
        pass

    col_nuevo, col_atencion, col_cuadrilla, col_resuelto = st.columns(4)

    with col_nuevo:
        st.markdown("### 🆕 Nuevos")
        for t in [x for x in tickets if x["estado"] == "nuevo"]:
            with st.container(border=True):
                st.caption(f"{t['ticket_codigo']} · {t['prioridad']}")
                st.write(f"**{t['nombre_cliente']}**")
                st.write(t["descripcion_problema"])
                st.info(f"SLA: {t['sla_minutos']}m | Cat: {t['categoria']}")

    with col_atencion:
        st.markdown("### ⚙️ En Atención")
        for t in [x for x in tickets if x["estado"] == "en_atencion"]:
            with st.container(border=True):
                st.caption(f"{t['ticket_codigo']} · {t['prioridad']}")
                st.write(f"**{t['nombre_cliente']}**")
                st.write(t["descripcion_problema"])

    with col_cuadrilla:
        st.markdown("### 🚚 Cuadrilla")
        for t in [x for x in tickets if x["estado"] == "escalado_cuadrilla"]:
            with st.container(border=True):
                st.caption(f"🚨 {t['ticket_codigo']} · {t['prioridad']}")
                st.write(f"**{t['nombre_cliente']}**")
                st.error("Requiere visita presencial con fusionadora.")

    with col_resuelto:
        st.markdown("### ✅ Resueltos")
        for t in [x for x in tickets if x["estado"] == "resuelto"]:
            with st.container(border=True):
                st.caption(f"✓ {t['ticket_codigo']}")
                st.write(f"**{t['nombre_cliente']}**")
                st.success("Incidencia cerrada exitosamente.")
