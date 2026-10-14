from .all_bulk_orders import router as all_bulk_orders_router
from .active_orders import router as active_orders_router

VIEW_ORDER_ROUTERS = [
    all_bulk_orders_router,
    active_orders_router
]

__all__ = [
   'VIEW_ORDER_ROUTERS' 
]