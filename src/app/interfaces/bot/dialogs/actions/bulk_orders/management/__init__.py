from .delete_bulk_order.dialog import delete_bulk_order_dialog

MANAGEMENT_DIALOGS = [
    delete_bulk_order_dialog,
]

__all__ = [
    'MANAGEMENT_DIALOGS'
]