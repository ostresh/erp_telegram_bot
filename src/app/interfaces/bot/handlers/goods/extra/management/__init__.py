from .cancel_order import router as cancel_order_router
from .change_record import router as change_record_router
from .delete_record import router as delete_record_router

MANAGEMENT = [
    cancel_order_router,
    change_record_router,
    delete_record_router
]

__all__ = [
    'MANAGEMENT'
]
