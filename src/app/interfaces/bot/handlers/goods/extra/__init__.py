from .swap import router as swap_router
from .reserve import router as reserve_router
from .comment import router as comment_router
from .wrh_dlvr import WRH_DLVR
from .management import MANAGEMENT

GOODS_EXTRA_ROUTERS = [
    swap_router,
    reserve_router,
    comment_router,
    *WRH_DLVR,
    *MANAGEMENT
]

__all__ = [
    'GOODS_EXTRA_ROUTERS'
]