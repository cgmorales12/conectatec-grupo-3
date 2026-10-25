"""
Módulo de enrutadores modulares de FastAPI - ConectaTec
"""
from app.routers.tickets import router as tickets_router
from app.routers.salud import router as salud_router

__all__ = ["tickets_router", "salud_router"]
