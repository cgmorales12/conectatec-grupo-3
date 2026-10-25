"""
Suite de Pruebas Unitarias Automatizadas con Mocks - ConectaTec
Cumple: Pruebas deterministas que pasan 100% sin internet ni consumo de API Keys.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.tools.priorizar import calcular_prioridad_itil
from app.services.llm import anonimizar_datos_sensibles, _clasificar_heuristicamente
from app.services.rag import consultar_base_conocimiento
from app.schemas import ClasificacionIA, MetadatosIA
from app.database import inicializar_bd

# Asegurar tablas creadas para el cliente de pruebas
inicializar_bd()

client = TestClient(app)


def test_endpoint_salud():
    """Verifica que el endpoint de salud responda 200 OK con la arquitectura."""
    response = client.get("/v1/salud")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["servicio"] == "conectatec-api"
    assert "arquitectura" in data

def test_priorizacion_itil_determinista():
    """Valida que la matriz ITIL calcule la prioridad matemáticamente en Python."""
    # Caso 1: Alto x Alta -> Prioridad Alta
    res_alta = calcular_prioridad_itil("Alto", "Alta")
    assert res_alta.prioridad == "Alta"
    assert res_alta.sla_minutos <= 120
    
    # Caso 2: Bajo x Baja -> Prioridad Baja
    res_baja = calcular_prioridad_itil("Bajo", "Baja")
    assert res_baja.prioridad == "Baja"
    assert res_baja.sla_minutos >= 1440
    
    # Caso 3: Medio x Media -> Prioridad Media
    res_media = calcular_prioridad_itil("Medio", "Media")
    assert res_media.prioridad == "Media"

def test_anonimizacion_contrasenas_lopdp():
    """Verifica que contraseñas escritas por error sean anonimizadas (Art. 23 LOPDP)."""
    texto_con_clave = "Hola soporte, mi clave: MiClaveSecreta123 no conecta y tengo problemas de internet."
    texto_limpio = anonimizar_datos_sensibles(texto_con_clave)
    
    assert "MiClaveSecreta123" not in texto_limpio
    assert "[CONFIDENCIAL_REMOVIDO]" in texto_limpio

def test_clasificacion_ticket_offline(monkeypatch):
    """
    Prueba el flujo completo de POST /v1/tickets/clasificar usando un Mock de IA
    para garantizar que la prueba sea reproducible y sin costo de red.
    """
    def mock_clasificar(texto):
        return (
            ClasificacionIA(
                categoria="Conectividad y Fibra Óptica",
                impacto="Alto",
                urgencia="Alta",
                sintomas_detectados=["LED LOS rojo", "Corte de enlace"],
                justificacion="Mock de prueba unitaria para triaje."
            ),
            MetadatosIA(
                proveedor="gemini",
                modelo="gemini-1.5-flash",
                conmutado=False,
                motivo_conmutacion=None,
                latencia_ms=15.0
            )
        )

    # Inyectar el mock en el servicio LLM
    import app.routers.tickets as tickets_module
    monkeypatch.setattr(tickets_module, "clasificar_solicitud", mock_clasificar)

    payload = {
        "nombre_cliente": "Carlos Perez",
        "email_cliente": "carlos.perez@example.com",
        "descripcion_problema": "Se me puso la luz roja LOS en la ONT Huawei y no tengo internet en la oficina.",
        "codigo_abonado": "CLI-9901"
    }

    response = client.post("/v1/tickets/clasificar", json=payload)
    assert response.status_code == 201
    ticket = response.json()
    
    assert ticket["prioridad"] == "Alta"
    assert ticket["impacto"] == "Alto"
    assert ticket["urgencia"] == "Alta"
    assert ticket["nombre_cliente"] == "Carlos Perez"
    assert ticket["estado"] in ["nuevo", "escalado_cuadrilla"]
    assert len(ticket["citas"]) > 0
    assert ticket["citas"][0]["documento_id"].startswith("DOC-")

def test_validacion_entrada_rfc9457():
    """Valida que entradas con menos de 10 caracteres retornen 422 en formato problem+json."""
    payload_invalido = {
        "nombre_cliente": "Ana",
        "email_cliente": "ana@example.com",
        "descripcion_problema": "ayuda"  # Menos de 10 caracteres
    }

    response = client.post("/v1/tickets/clasificar", json=payload_invalido)
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    
    problem = response.json()
    assert problem["status"] == 422
    assert problem["type"] == "/errores/entrada-invalida"
    assert "detail" in problem

def test_transparencia_conmutacion_failover(monkeypatch):
    """Verifica que cuando actúa el respaldo Groq, los metadatos lo indiquen transparentemente."""
    def mock_clasificar_conmutado(texto):
        return (
            ClasificacionIA(
                categoria="Calidad y Velocidad",
                impacto="Medio",
                urgencia="Media",
                sintomas_detectados=["Lentitud en horario pico"],
                justificacion="Atendido por respaldo de contingencia."
            ),
            MetadatosIA(
                proveedor="groq",
                modelo="llama-3.3-70b-versatile",
                conmutado=True,
                motivo_conmutacion="Gemini 1.5 Flash HTTP 429 - Cuota excedida",
                latencia_ms=45.2
            )
        )

    import app.routers.tickets as tickets_module
    monkeypatch.setattr(tickets_module, "clasificar_solicitud", mock_clasificar_conmutado)

    payload = {
        "nombre_cliente": "Mariana Lopez",
        "email_cliente": "mariana@example.com",
        "descripcion_problema": "El internet esta sumamente lento en la noche y las paginas no abren."
    }

    response = client.post("/v1/tickets/clasificar", json=payload)
    assert response.status_code == 201
    ticket = response.json()
    
    assert ticket["metadatos_ia"]["conmutado"] is True
    assert ticket["metadatos_ia"]["proveedor"] == "groq"
    assert "Gemini 1.5 Flash HTTP 429" in ticket["metadatos_ia"]["motivo_conmutacion"]


def test_listar_tickets_tablero():
    """Verifica que GET /v1/tickets retorne la lista de tickets sin violar los esquemas estrictos de Pydantic."""
    response = client.get("/v1/tickets")
    assert response.status_code == 200
    data = response.json()
    assert "total_tickets" in data
    assert "tickets" in data
    assert isinstance(data["tickets"], list)
    if data["total_tickets"] > 0:
        primer_ticket = data["tickets"][0]
        assert "ticket_codigo" in primer_ticket
        assert "citas" in primer_ticket
        assert "metadatos_ia" in primer_ticket
        assert "proveedor" in primer_ticket["metadatos_ia"]


def test_solicitud_fuera_de_alcance_no_tecnica():
    """Valida que solicitudes no relacionadas con averías de telecomunicaciones se identifiquen como fuera de alcance."""
    payload = {
        "nombre_cliente": "Christian Morales",
        "email_cliente": "christian@example.com",
        "descripcion_problema": "Hola soporte, quisiera saber porque no llueve hoy en la ciudad."
    }

    response = client.post("/v1/tickets/clasificar", json=payload)
    assert response.status_code == 201
    ticket = response.json()

    assert ticket["categoria"] == "Solicitud No Técnica / Fuera de Alcance"
    assert ticket["prioridad"] == "Baja"
    assert ticket["requiere_revision_humana"] is True
    assert len(ticket["citas"]) == 0
    assert "no describe ninguna avería técnica" in ticket["solucion_propuesta"]


