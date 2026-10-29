from .health.router import router as health_router
from .user.router import router as user_router
from app.interfaces.api.common.schemas.router_config import RouterConfig

SYSTEM_ROUTERS = [
    RouterConfig(router=health_router, prefix="/health", tags=["health"]),
    RouterConfig(router=user_router, prefix="/user", tags=["user"])
]

__all__ = [
    'SYSTEM_ROUTERS'
]