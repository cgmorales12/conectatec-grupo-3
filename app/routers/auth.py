"""
Enrutador de Autenticación para el Personal TIC - ConectaTec
Endpoints: Inicio de Sesión y Verificación de Perfil Activo (RBAC)
Autor: Amalia Geoconda Iguasnia (QA / Seguridad y Requerimientos)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import LoginIn, LoginOut, PerfilTICOut
from app.database import verificar_credenciales_tic
from app.services.auth import generar_token_sesion, obtener_usuario_autenticado

router = APIRouter(prefix="/v1/auth", tags=["Autenticación TIC"])


@router.post(
    "/login",
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    summary="Inicio de sesión exclusivo para personal técnico TIC"
)
def iniciar_sesion_tic(payload: LoginIn):
    """
    Valida credenciales contra la base de datos de usuarios autorizados.
    Retorna un token de sesión criptográfico (HMAC-SHA256) con validez de 8 horas.
    """
    usuario_valido = verificar_credenciales_tic(payload.usuario, payload.password)
    if not usuario_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no válidas. Verifique su usuario o contraseña de soporte TIC.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = generar_token_sesion(usuario_valido, duracion_horas=8)
    
    return LoginOut(
        token=token,
        usuario=usuario_valido["usuario"],
        nombre_completo=usuario_valido["nombre_completo"],
        rol=usuario_valido["rol"],
        expira_en_horas=8
    )


@router.get(
    "/perfil",
    response_model=PerfilTICOut,
    status_code=status.HTTP_200_OK,
    summary="Verifica la sesión activa del personal TIC"
)
def obtener_perfil_activo(usuario_sesion: dict = Depends(obtener_usuario_autenticado)):
    """
    Retorna los datos del usuario técnico asociado al token Bearer provisto.
    """
    return PerfilTICOut(
        usuario=usuario_sesion["usuario"],
        nombre_completo=usuario_sesion["nombre_completo"],
        rol=usuario_sesion["rol"]
    )
