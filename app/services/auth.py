from __future__ import annotations
"""
Servicio de Autenticación y Control de Acceso (RBAC) - Personal TIC
Cumple: Tokens firmados criptográficamente (HMAC-SHA256), expiración por turno laboral y cero dependencias externas.
Autor: Amalia Geoconda Iguasnia (QA / Seguridad y Requerimientos)
"""

import os
import json
import time
import base64
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass


def _obtener_clave_secreta() -> str:
    """
    Obtiene la clave de firma JWT desde variables de entorno (.env).
    Principio de Seguridad LOPDP / OWASP: Cero claves por defecto hardcodeadas en código fuente.
    Si no está configurada, genera dinámicamente una clave criptográfica de 256 bits.
    """
    clave = os.environ.get("JWT_SECRET_KEY")
    if not clave:
        clave = secrets.token_hex(32)
        os.environ["JWT_SECRET_KEY"] = clave
    return clave


def _b64url_encode(data: bytes) -> str:
    """Codifica bytes en formato Base64URL sin relleno de signos igual."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(cadena: str) -> bytes:
    """Decodifica una cadena Base64URL agregando el relleno necesario."""
    padding = "=" * ((4 - len(cadena) % 4) % 4)
    return base64.urlsafe_b64decode(cadena + padding)


def generar_token_sesion(usuario_datos: Dict[str, Any], duracion_horas: int = 8) -> str:
    """
    Genera un token de sesión firmado compatible con RFC 7519 para el personal TIC.
    """
    ahora = int(time.time())
    expiracion = ahora + (duracion_horas * 3600)
    
    cabecera = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    payload = {
        "sub": str(usuario_datos.get("id", usuario_datos.get("usuario"))),
        "usuario": usuario_datos.get("usuario"),
        "nombre_completo": usuario_datos.get("nombre_completo"),
        "rol": usuario_datos.get("rol", "tecnico_tic"),
        "iat": ahora,
        "exp": expiracion
    }
    
    cabecera_b64 = _b64url_encode(json.dumps(cabecera, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    mensaje_a_firmar = f"{cabecera_b64}.{payload_b64}".encode("utf-8")
    
    clave = _obtener_clave_secreta()
    firma = hmac.new(clave.encode("utf-8"), mensaje_a_firmar, hashlib.sha256).digest()
    firma_b64 = _b64url_encode(firma)
    
    return f"{cabecera_b64}.{payload_b64}.{firma_b64}"


def verificar_token_sesion(token: str) -> Optional[Dict[str, Any]]:
    """
    Valida la integridad de la firma HMAC y comprueba que el token no haya expirado.
    """
    try:
        partes = token.strip().split(".")
        if len(partes) != 3:
            return None
        
        cabecera_b64, payload_b64, firma_b64 = partes
        mensaje_firmado = f"{cabecera_b64}.{payload_b64}".encode("utf-8")
        clave = _obtener_clave_secreta()
        firma_esperada = hmac.new(clave.encode("utf-8"), mensaje_firmado, hashlib.sha256).digest()
        firma_recibida = _b64url_decode(firma_b64)
        
        # Comparación de tiempo constante contra ataques de temporización (OWASP)
        if not hmac.compare_digest(firma_esperada, firma_recibida):
            return None
        
        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        # Verificar expiración
        ahora = int(time.time())
        if payload.get("exp", 0) < ahora:
            return None
            
        return payload
    except Exception:
        return None


def obtener_usuario_autenticado(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Dependencia FastAPI que intercepta el encabezado Authorization: Bearer <token>.
    Si el token no existe, está alterado o caducó, deniega el acceso con 401 Problem Details.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso restringido: Se requiere autenticación del Personal TIC para realizar esta operación.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    partes = authorization.split(" ")
    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorización no válido. Debe ser: Bearer <token_jwt>.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = partes[1]
    payload = verificar_token_sesion(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o credenciales no válidas. Por favor inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload
