from .delete_bulk_order import router as delete_bulk_order_router

MANAGEMENT_ROUTERS = [
    delete_bulk_order_router
]

__all__ = [
    'MANAGEMENT_ROUTERS'
]