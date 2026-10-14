from .create_bulk_order.dialog import create_bulk_order_dialog
from .add_delivery_to_bulk_order.dialog import add_delivery_to_bulk_order_dialog
from .bulk_order_arrived.dialog import bulk_order_arrived_dialog
from .view_orders.dialog import view_orders_dialog
from .management import MANAGEMENT_DIALOGS

BULK_ORDER_DIALOGS = [
    create_bulk_order_dialog,
    add_delivery_to_bulk_order_dialog,
    bulk_order_arrived_dialog,
    view_orders_dialog,
    *MANAGEMENT_DIALOGS
]

__all__ = [
    'BULK_ORDER_DIALOGS'
]