from .swap.dialog import swap_dialog
from .reserve.dialog import reserve_dialog
from .comment.dialog import comment_dialog
from .wrh_dlvr import WRH_DLVR
from .management import MANAGEMENT

GOODS_EXTRA_DIALOGS = [
    swap_dialog,
    reserve_dialog,
    comment_dialog,
    *WRH_DLVR,
    *MANAGEMENT
]

__all__ = [
    'GOODS_EXTRA_DIALOGS'
]