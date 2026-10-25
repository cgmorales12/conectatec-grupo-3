"""
Módulo de enrutadores modulares de FastAPI - ConectaTec
"""
from app.routers.tickets import router as tickets_router
from app.routers.salud import router as salud_router
from app.routers.auth import router as auth_router
from app.routers.manuales import router as manuales_router

__all__ = ["tickets_router", "salud_router", "auth_router", "manuales_router"]
