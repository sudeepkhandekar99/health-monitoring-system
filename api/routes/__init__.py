from .patients import router as patients_router
from .alerts import router as alerts_router
from .admin import router as admin_router

__all__ = ["patients_router", "alerts_router", "admin_router"]