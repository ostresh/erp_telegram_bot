from .create_bulk_order import router as create_bulk_order_router
from .add_delivery_to_bulk_order import router as add_delivery_to_bulk_order_router
from .bulk_order_arrived import router as bulk_order_arrived_router
from .view_orders import VIEW_ORDER_ROUTERS
from .management import MANAGEMENT_ROUTERS

BULK_ORDER_ROUTERS = [
    create_bulk_order_router,
    add_delivery_to_bulk_order_router,
    bulk_order_arrived_router,
    *VIEW_ORDER_ROUTERS,
    *MANAGEMENT_ROUTERS
]

__all__ = [
    'BULK_ORDER_ROUTERS'
]