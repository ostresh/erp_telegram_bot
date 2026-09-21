from aiogram import Router

from .common.commands import router as commands_router
from .common.navigation import router as navigation_router
from .common.search import router as search_router
from .common.hello import router as hello_router
from .goods.buy_goods import router as buy_goods_router
from .goods.sell_goods import router as sell_goods_router


main_router = Router(name="main")

main_router.include_routers(
    commands_router,
    navigation_router,
    search_router,
    hello_router,
    buy_goods_router,
    sell_goods_router
)

__all__ = ["main_router"]