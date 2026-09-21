from aiogram_dialog.widgets.kbd import Row, Button, Back
from aiogram_dialog.widgets.text import Const

from app.interfaces.bot.messages.menu import MenuConstants
from .event_handler import CommonEventHandler


class CommonDialogNavigation:
    """
    Общие элементы навигации для диалогов.

    Содержит готовые кнопки и строки для навигации:
    - Возврат в меню (для первого окна)
    - Возврат по диалогу (для внутренних окон)
    """
    
    # Для первого окна диалога (возврат в меню)
    root_controls: Row = Row(
        Button(
            Const(MenuConstants.BACK_TEXT),
            id='back_button',
            on_click=CommonEventHandler.on_back,
        ),
        Button(
            Const(MenuConstants.CLOSE_TEXT),
            id='close_button',
            on_click=CommonEventHandler.on_close,
        ),
    )
    
    # Для внутренних окон диалога (возврат на предыдущее окно)
    inner_controls: Row = Row(
        Back(Const(MenuConstants.BACK_TEXT)),
        Button(
            Const(MenuConstants.CLOSE_TEXT),
            id='close_button',
            on_click=CommonEventHandler.on_close,
        ),
    )