# DOC-04: Guía de Autogestión de Credenciales Wi-Fi (SSID y Clave WPA2/WPA3)

**Categoría:** Redes Inalámbricas / Seguridad  
**Fabricante / Origen:** ConectaTec ISP / Centro de Atención al Cliente  
**Versión / Vigencia:** v3.1 - Octubre 2026  

## Descripción General
Instrucciones paso a paso para el cambio seguro del nombre de red (SSID) y contraseña de seguridad inalámbrica a través de la interfaz web institucional y portal de cliente.

## Procedimiento Operativo Paso a Paso
### Paso 1: Conexión al equipo mediante cable de red o Wi-Fi actual
Conéctese preferiblemente por cable de red UTP a cualquier puerto LAN de la ONT, o mantenga conexión activa a la red Wi-Fi actual.

### Paso 2: Acceso a la interfaz gráfica de administración
Abra su navegador web e ingrese en la barra de direcciones la IP de puerta de enlace predeterminada: http://192.168.1.1 o http://192.168.100.1.

### Paso 3: Autenticación de credenciales de usuario
Ingrese el usuario y contraseña proporcionados en la etiqueta inferior de su equipo o use las credenciales seguras del portal de autogestión ConectaTec.

### Paso 4: Modificación de parámetros inalámbricos (WLAN Settings)
Navegue a la pestaña 'Network' -> 'WLAN' -> 'SSID Settings'. Modifique el campo 'SSID Name' y en 'WPA PreSharedKey' escriba una nueva clave con mínimo 10 caracteres alfanuméricos.

### Paso 5: Aplicar cambios y reconexión de dispositivos
Haga clic en 'Apply' o 'Guardar'. La red inalámbrica se reiniciará inmediatamente. Vuelva a vincular todos sus dispositivos con la nueva contraseña.

## Matriz de Diagnóstico Rápido

| Parámetro | Valor Recomendado | Estándar de Seguridad | Recomendación Técnica |
| --- | --- | --- | --- |
| Modo de Seguridad | WPA2-PSK [AES] / WPA3 | Estándar de cifrado robusto | Evite WEP o WPA-TKIP obsoletos. |
| Longitud de Clave | Mínimo 10 - 16 caracteres | Políticas LOPDP de seguridad | Combine mayúsculas, minúsculas y números. |
| Frecuencia 2.4 GHz | Ancho de canal 20 MHz | Mayor penetración en muros | Ideal para dispositivos IoT y telefonía. |
| Frecuencia 5 GHz | Ancho de canal 40/80 MHz | Ultra velocidad y bajo retardo | Ideal para streaming 4K y gaming. |

---
*ConectaTec ISP · Base de Conocimiento Oficial RAG · UNIANDES 2026*
