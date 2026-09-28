from .buy_goods.dialog import buy_goods_dialog
from .sell_goods.dialog import sell_goods_dialog
from .order_arrived.dialog import order_arrived_dialog
from .change_selling_price.dialog import change_selling_price_dialog
from .add_trns.dialog import add_trns_dialog

GOODS_DIALOGS = [
    buy_goods_dialog,
    sell_goods_dialog,
    order_arrived_dialog,
    change_selling_price_dialog,
    add_trns_dialog
]

__all__ = [
    'GOODS_DIALOGS'
]