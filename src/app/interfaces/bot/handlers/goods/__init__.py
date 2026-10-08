from .buy_goods import router as buy_goods_router
from .sell_goods import router as sell_goods_router
from .order_arrived import router as order_arrived_router
from .change_selling_price import router as change_selling_price_router
from .add_trns import router as add_trns_router
from .extra import GOODS_EXTRA_ROUTERS

GOODS_ROUTERS = [
    buy_goods_router,
    sell_goods_router,
    order_arrived_router,
    change_selling_price_router,
    add_trns_router,
    *GOODS_EXTRA_ROUTERS
]

__all__ = [
    'GOODS_ROUTERS'
]