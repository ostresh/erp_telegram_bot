from .view_description.dialog import view_description_dialog
from .change_description.dialog import change_description_dialog

DESCRIPTION_DIALOGS = [
    change_description_dialog,
    view_description_dialog
]

__all__ = [
    'DESCRIPTION_DIALOGS'
]