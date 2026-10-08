from aiogram import Router

from .common import COMMON_ROUTERS
from .goods import GOODS_ROUTERS


main_router = Router(name="main")

main_router.include_routers(
    *COMMON_ROUTERS,
    *GOODS_ROUTERS
)

__all__ = ["main_router"]