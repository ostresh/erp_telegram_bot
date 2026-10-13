from .create_bulk_order.dialog import create_bulk_order_dialog
from .add_delivery_to_bulk_order.dialog import add_delivery_to_bulk_order_dialog
from .bulk_order_arrived.dialog import bulk_order_arrived_dialog

BULK_ORDER_DIALOGS = [
    create_bulk_order_dialog,
    add_delivery_to_bulk_order_dialog,
    bulk_order_arrived_dialog
]

__all__ = [
    'BULK_ORDER_DIALOGS'
]