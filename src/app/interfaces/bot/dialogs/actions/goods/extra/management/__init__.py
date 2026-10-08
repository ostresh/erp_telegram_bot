from .cancel_order.dialog import cancel_order_dialog
from .change_record.dialog import change_record_dialog
from .delete_record.dialog import delete_record_dialog

MANAGEMENT = [
    cancel_order_dialog,
    change_record_dialog,
    delete_record_dialog
]

__all__ = [
    'MANAGEMENT'
]
