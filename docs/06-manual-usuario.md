# Manual de Usuario · ConectaTec
**Sistema de Triaje Inteligente de Incidentes ISP (Caso N.º 03 · Grupo 3 UNIANDES)**

---

## 1. Introducción
**ConectaTec** es una plataforma web inteligente diseñada para automatizar la recepción, diagnóstico de primer nivel y priorización de averías de internet para abonados y operadores de mesa de ayuda.

---

## 2. Acceso a la Plataforma Web
1. Abra su navegador web (Google Chrome, Firefox o Microsoft Edge).
2. Ingrese a la dirección local del sistema: `http://localhost:8000/tablero`
3. En la parte superior observará el distintivo en tiempo real del motor de inteligencia artificial:
   - `🟢 Proveedor: Gemini 1.5 Flash (Nominal)`: Operación estándar con el modelo de Google.
   - `🟠 Respaldo Activo: Groq Cloud (Llama 3.3)`: Conmutación automática por contingencia.

---

## 3. Ingreso de un Reporte de Avería (Abonado / Operador)

En el panel lateral izquierdo encontrará el formulario de ingreso:

```
┌──────────────────────────────────────────────┐
│       INGRESAR SOLICITUD DE SOPORTE          │
├──────────────────────────────────────────────┤
│ Nombre del Abonado:  [ Carlos Perez        ] │
│ Correo Electrónico:  [ carlos@empresa.com  ] │
│ Código de Cliente:   [ CLI-9981            ] │
│ Descripción:                                 │
│ [ Se puso la luz roja LOS en el router    ] │
│ [ y se cortó el internet hace 20 minutos.  ] │
├──────────────────────────────────────────────┤
│ [ ⚡ Clasificar con IA y Crear Ticket ]       │
└──────────────────────────────────────────────┘
```

### Pasos:
1. Complete los campos obligatorios: Nombre, Correo y Descripción del problema (mínimo 10 caracteres).
2. O seleccione uno de los botones rápidos de prueba:
   - `🔴 Luz LOS Roja Huawei`: Simula corte total de fibra óptica.
   - `🐢 Lentitud / Fast Ethernet`: Simula degradación por cable a 100 Mbps.
   - `🔑 Cambio Clave Wi-Fi`: Simula solicitud de configuración de credenciales.
   - `💳 Corte por Factura`: Simula suspensión comercial por mora.
3. Haga clic en **«Clasificar con IA y Crear Ticket»**.
4. El sistema en menos de 1 segundo:
   - Sanitiza automáticamente contraseñas si las escribió por error (LOPDP).
   - Extrae el Impacto y Urgencia con IA.
   - Calcula matemáticamente la Prioridad ITIL y el tiempo máximo SLA.
   - Busca en los 15 manuales técnicos la solución y cita el paso exacto (`DOC-XX`).
   - Ubica la tarjeta en la columna correspondiente del tablero Kanban.

---

## 4. Gestión en el Tablero Kanban (Operador y Técnicos)

El tablero organiza los tickets en 4 columnas de flujo operativo:

1. **🆕 Nuevos:** Incidentes recién ingresados en espera de atención inicial.
2. **⚙️ En Atención:** Incidentes asignados a un operador de mesa de ayuda en proceso de diagnóstico remoto.
3. **🚚 Escalado a Cuadrilla:** Averías críticas con daño físico confirmado (luz LOS roja, fibra rota) que requieren visita presencial con fusionadora.
4. **✅ Resueltos:** Incidentes con solución confirmada y servicio restablecido.

### Mover Tickets entre Columnas:
En cada tarjeta de ticket encontrará botones de acción directa:
- Haga clic en **«⚙️ Atender»** para iniciar el soporte remoto.
- Haga clic en **«🚚 Escalar»** para despachar cuadrilla de campo.
- Haga clic en **«✅ Resolver»** una vez verificada la navegación del cliente.
