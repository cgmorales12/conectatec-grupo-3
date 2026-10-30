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
            st.error("⚠️ **Descripción Demasiado Corta:** La descripción de la incidencia debe contener al menos 10 caracteres para que la IA realice el triaje.")
        else:
            payload = {
                "nombre_cliente": nombre,
                "email_cliente": email,
                "codigo_abonado": codigo if codigo else None,
                "descripcion_problema": descripcion
            }
            try:
                # Indicador visual de espera mientras el backend procesa el triaje
                with st.spinner("⏳ Analizando incidencia con IA y consultando manuales técnicos (RAG)... Por favor espere..."):
                    res = requests.post(f"{API_BASE_URL}/v1/tickets/clasificar", json=payload, timeout=20)
                
                if res.status_code == 201:
                    t = res.json()
                    st.success(f"⚡ **Ticket Creado Exitosamente:** Código `{t['ticket_codigo']}` | Prioridad: **{t['prioridad']}** | SLA: **{t['sla_minutos']} min**")
                    if t.get("metadatos_ia", {}).get("conmutado"):
                        proveedor_respaldo = t["metadatos_ia"]["proveedor"]
                        st.warning(f"🟠 **Respaldo Activo:** Atendido mediante contingencia ({proveedor_respaldo}) por indisponibilidad del modelo primario.")
                    st.rerun()
                else:
                    # Deserializar y presentar errores comprensibles según RFC 9457
                    try:
                        err_data = res.json()
                        detalle = err_data.get("detail", res.text)
                        titulo = err_data.get("title", "Error en la Solicitud")
                    except Exception:
                        detalle = res.text
                        titulo = "Error en la Solicitud"

                    if res.status_code == 422:
                        st.error(f"⚠️ **Datos de Entrada Inválidos (RFC 9457 · 422):** {detalle}")
                        st.info("💡 **Acción Sugerida:** Revise los campos del formulario y asegúrese de detallar los síntomas técnicos.")
                    elif res.status_code == 429:
                        st.warning(f"⏳ **Límite de Consultas Alcanzado (RFC 6585 · 429):** {detalle}")
                        st.info("💡 **Acción Sugerida:** Espere unos segundos para que se recarguen las fichas de su sesión de trabajo.")
                    elif res.status_code in [500, 503]:
                        st.error(f"🚨 **Servicio Temporalmente No Disponible ({res.status_code}):** {detalle}")
                        st.info("💡 **Acción Sugerida:** El sistema activará el conmutador offline en el siguiente reintento.")
                    else:
                        st.error(f"⚠️ **{titulo} ({res.status_code}):** {detalle}")

            except requests.exceptions.ConnectionError:
                st.error(f"🔌 **Error de Conexión:** No fue posible establecer comunicación con el backend FastAPI en `{API_BASE_URL}`.")
                st.info("💡 **Acción Sugerida:** Verifique que el servidor backend esté iniciado ejecutando: `uvicorn app.main:app --reload --port 8000`.")
            except Exception as e:
                st.error(f"⚠️ **Error Inesperado:** {str(e)}")

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

    # Barra de Filtros por Metadatos (RAG & ITIL 4)
    with st.expander("🔍 Filtros de Visualización por Metadatos (RAG & ITIL 4)", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1, 1, 1])
        with f_col1:
            q_buscar = st.text_input("Búsqueda Rápida", placeholder="Síntoma, cliente o ticket...", key="filtro_q")
        with f_col2:
            cat_seleccionada = st.selectbox("Categoría", ["Todas", "Fibra", "Wi-Fi", "Velocidad", "Hardware", "Cuentas", "Facturación", "Fuera de Alcance"], key="filtro_cat")
        with f_col3:
            prio_seleccionada = st.selectbox("Prioridad", ["Todas", "Alta", "Media", "Baja"], key="filtro_prio")
        with f_col4:
            fuente_seleccionada = st.selectbox(
                "Fuente RAG",
                ["Todas", "DOC-01", "DOC-02", "DOC-03", "DOC-04", "DOC-05", "DOC-06", "DOC-07", "DOC-08", "DOC-09", "DOC-10", "DOC-11", "DOC-12", "DOC-13", "DOC-14"],
                key="filtro_fuente"
            )

    # Aplicar filtros de metadatos sobre la lista de tickets
    tickets_filtrados = []
    for t in tickets:
        if q_buscar:
            q = q_buscar.lower().strip()
            texto_t = f"{t.get('ticket_codigo', '')} {t.get('nombre_cliente', '')} {t.get('descripcion_problema', '')} {t.get('categoria', '')}".lower()
            if q not in texto_t:
                continue
        if cat_seleccionada != "Todas":
            if cat_seleccionada.lower() not in t.get("categoria", "").lower():
                continue
        if prio_seleccionada != "Todas":
            if t.get("prioridad", "").lower() != prio_seleccionada.lower():
                continue
        if fuente_seleccionada != "Todas":
            tiene_fuente = any(c.get("documento_id", "").lower() == fuente_seleccionada.lower() for c in t.get("citas", []))
            if not tiene_fuente:
                continue
        tickets_filtrados.append(t)

    st.caption(f"📊 Mostrando **{len(tickets_filtrados)}** de **{len(tickets)}** tickets según los filtros de metadatos seleccionados.")

    def renderizar_tarjeta_ticket(t):
        """Renderiza una tarjeta de ticket con sus fuentes técnicas y citas obligatorias RAG."""
        with st.container(border=True):
            st.caption(f"🏷️ **{t['ticket_codigo']}** · Prioridad: **{t['prioridad']}** (SLA {t['sla_minutos']}m)")
            st.markdown(f"**Cliente:** {t['nombre_cliente']}")
            st.markdown(f"*{t['descripcion_problema']}*")
            
            # Cita obligatoria de fuente RAG
            if t.get("citas") and len(t["citas"]) > 0:
                c = t["citas"][0]
                st.markdown(f"📖 **Cita RAG:** `{c.get('documento_id')}` · {c.get('paso_exacto')}")
                st.caption(f"**Fuente:** {c.get('titulo_documento', 'Manual Oficial')} ({c.get('vigencia', '2026-V1')})")
                st.info(f"«{c.get('fragmento_aplicado', '')}»")
                if c.get("url"):
                    st.markdown(f"[🔗 Consultar Fuente Técnica Oficial]({c['url']})")
            elif "Fuera de Alcance" in t.get("categoria", ""):
                st.caption("⚪ *Sin cita técnica: Solicitud No Técnica / Fuera de Alcance (Regla de Silencio)*")
            elif t.get("requiere_revision_humana"):
                st.warning("⚠️ *Caso derivado a Nivel 2 humano (Umbral de confianza o contingencia).*")

            # Indicadores Human-in-the-Loop (HITL · OWASP LLM08)
            if t.get("confirmado_por"):
                st.success(f"🛡️ **Aprobado HITL por:** {t['confirmado_por']}")
            if t.get("notificacion_enviada"):
                st.info("✉️ **Notificación Oficial Remitida al Abonado**")
            if t.get("cuadrilla_despachada"):
                st.warning(f"👷 **Cuadrilla Despachada:** `{t.get('orden_despacho_id', 'ODT-FIBRA')}`")

            st.caption(f"IA: {t.get('metadatos_ia', {}).get('proveedor', 'gemini')} | Cat: {t.get('categoria', '')}")

            # Botones interactivos HITL
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("✉️ Notificar", key=f"btn_notif_{t['id']}", help="Confirmación humana antes de enviar notificación"):
                    try:
                        res_p = requests.get(f"{API_BASE_URL}/v1/tickets/{t['id']}/proponer-envio", timeout=2)
                        if res_p.status_code == 200:
                            data_env = res_p.json()
                            requests.post(f"{API_BASE_URL}/v1/tickets/{t['id']}/confirmar-envio", json={
                                "ticket_id": t["id"],
                                "destinatario_email": data_env["destinatario_email"],
                                "asunto": data_env["asunto_propuesto"],
                                "mensaje_final": data_env["mensaje_propuesto"],
                                "operador_confirmador": "Operador TIC Streamlit"
                            }, timeout=2)
                            st.toast("✉️ Notificación autorizada y enviada al abonado.")
                            st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")
            with b_col2:
                if t["estado"] != "escalado_cuadrilla":
                    if st.button("🚨 Cuadrilla", key=f"btn_cuad_{t['id']}", help="Confirmación humana antes de derivar a cuadrilla física"):
                        try:
                            res_c = requests.get(f"{API_BASE_URL}/v1/tickets/{t['id']}/proponer-derivacion", timeout=2)
                            if res_c.status_code == 200:
                                data_der = res_c.json()
                                requests.post(f"{API_BASE_URL}/v1/tickets/{t['id']}/confirmar-derivacion", json={
                                    "ticket_id": t["id"],
                                    "cuadrilla_asignada": data_der["cuadrilla_sugerida"],
                                    "sector": data_der["sector"],
                                    "motivo": data_der["motivo_derivacion"],
                                    "operador_confirmador": "Operador TIC Streamlit",
                                    "autoriza_despacho_presencial": True
                                }, timeout=2)
                                st.toast("👷 Despacho de cuadrilla confirmado.")
                                st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")

    col_nuevo, col_atencion, col_cuadrilla, col_resuelto = st.columns(4)

    with col_nuevo:
        st.markdown("### 🆕 Nuevos")
        col_t = [x for x in tickets_filtrados if x["estado"] == "nuevo"]
        if not col_t:
            st.caption("Sin tickets en esta columna")
        for t in col_t:
            renderizar_tarjeta_ticket(t)

    with col_atencion:
        st.markdown("### ⚙️ En Atención")
        col_t = [x for x in tickets_filtrados if x["estado"] == "en_atencion"]
        if not col_t:
            st.caption("Sin tickets en esta columna")
        for t in col_t:
            renderizar_tarjeta_ticket(t)

    with col_cuadrilla:
        st.markdown("### 🚚 Cuadrilla")
        col_t = [x for x in tickets_filtrados if x["estado"] == "escalado_cuadrilla"]
        if not col_t:
            st.caption("Sin tickets en esta columna")
        for t in col_t:
            renderizar_tarjeta_ticket(t)

    with col_resuelto:
        st.markdown("### ✅ Resueltos")
        col_t = [x for x in tickets_filtrados if x["estado"] == "resuelto"]
        if not col_t:
            st.caption("Sin tickets en esta columna")
        for t in col_t:
            renderizar_tarjeta_ticket(t)
