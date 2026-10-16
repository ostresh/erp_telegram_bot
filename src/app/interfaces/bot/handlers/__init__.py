from aiogram import Router

from .common import COMMON_ROUTERS
from .goods import GOODS_ROUTERS
from .bulk_orders import BULK_ORDER_ROUTERS
from .extra import EXTRA_ROUTERS


main_router = Router(name="main")

main_router.include_routers(
    *COMMON_ROUTERS,
    *GOODS_ROUTERS,
    *BULK_ORDER_ROUTERS,
    *EXTRA_ROUTERS
)

__all__ = ["main_router"]