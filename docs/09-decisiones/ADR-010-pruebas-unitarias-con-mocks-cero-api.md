# ADR-010: Estrategia de Pruebas Unitarias Automatizadas con Mocks (Cero Consumo de API)
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
Ejecutar la suite de pruebas unitarias invocando directamente las APIs de Gemini o Groq consume saldo real de tokens, introduce lentitud por latencia de internet (12+ segundos) y genera falsos negativos si las APIs remotas están saturadas.

## Decisión
Implementar un arnés de pruebas unitarias automatizadas con `pytest` y `monkeypatch` que emula el comportamiento de los modelos de IA mediante **Mocks deterministas**:
1. Se interceptan `cliente_llm.clasificar`, `cliente_llm.chat_stream` y `cliente_llm.analizar`.
2. Se prueba la API de extremo a extremo (esquemas Pydantic, cálculo ITIL, citas RAG, base de datos) con **$0.00 USD de gasto y cero tokens consumidos**.
3. Se incluye una prueba de garantía que elimina las claves de API del entorno (`test_mock_garantia_cero_consumo_api_y_cero_red`) para verificar que la suite corre en entornos 100% desconectados de internet.

## Justificación
1. **Velocidad de Ejecución:** La suite de 28 pruebas pasa en **3.4 segundos** (reducción del 72% en tiempo).
2. **Cero Dependencia de Red:** Las pruebas pueden ejecutarse en servidores de integración continua (CI) sin configurar secretos ni depender de conectividad externa.
3. **Pruebas Deterministas:** Elimina por completo las pruebas intermitentes (*flaky tests*).

## Consecuencias
- Verificabilidad inmediata para cualquier evaluador o jurado de grado que clone el repositorio.
