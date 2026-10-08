from .commands import router as commands_router
from .navigation import router as navigation_router
from .search import router as search_router

COMMON_ROUTERS = [
    commands_router,
    navigation_router,
    search_router,
]

__all__ = [
    COMMON_ROUTERS
]