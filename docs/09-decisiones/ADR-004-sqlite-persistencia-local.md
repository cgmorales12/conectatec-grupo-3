# ADR-004: Adopción de SQLite Parametrizado como Motor de Persistencia
**Estado:** Aceptado  
**Fecha:** Octubre 2026  
**Autores:** Christian Morales, Luis Fernando Ribera, Amalia Geoconda Iguasnia  

## Contexto
El MVP debe ser evaluado por docentes y jurados que clonarán el repositorio y requerirán ejecutar el sistema inmediatamente sin instalar servidores de bases de datos complejos como PostgreSQL o MySQL.

## Decisión
Utilizar **SQLite** (`data/conectatec.db`) embebido en Python con consultas SQL estrictamente parametrizadas (`?`).

## Justificación
1. **Cero Fricción de Despliegue:** Funciona en cualquier sistema operativo sin dependencias externas ni puertos de red adicionales.
2. **Seguridad contra Inyecciones SQL (OWASP):** Al utilizar parámetros posicionales (`?`) en la biblioteca estándar `sqlite3`, ninguna entrada del usuario se concatena en sentencias SQL.
3. **Portabilidad:** La base de datos es un único archivo que puede respaldarse o inspeccionarse fácilmente durante las pruebas automatizadas.

## Consecuencias
- Adecuado para concurrencia moderada del MVP. Para escalamiento masivo futuro a miles de transacciones concurrentes por segundo, la capa del repositorio permite migrar a PostgreSQL modificando únicamente la cadena de conexión.
