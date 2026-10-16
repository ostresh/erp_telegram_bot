from .view_description import router as view_description_router
from .change_description import router as change_description_router

DESCRIPTION_ROUTERS = [
    change_description_router,
    view_description_router
]

__all__ = [
    'DESCRIPTION_ROUTERS'
]