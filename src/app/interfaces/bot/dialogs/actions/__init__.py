from .goods import GOODS_DIALOGS
from .bulk_orders import BULK_ORDER_DIALOGS

ACTION_DIALOGS = [
    *GOODS_DIALOGS,
    *BULK_ORDER_DIALOGS
]

__all__ = [
    'ACTION_DIALOGS'
]