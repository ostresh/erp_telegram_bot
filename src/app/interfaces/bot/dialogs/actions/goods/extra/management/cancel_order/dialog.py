from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import CancelOrderSG as States
from .event_handler import CancelOrderEventHandler as EventHandler
from .getter import CancelOrderGetter as Getter



cancel_order_dialog = Dialog(
    
    # первый этап - ввод игры
    RootWindow(
        *CommonWidgets.game_input(
            EventHandler,
            switch_inline_query_text=Const('@to_client ')
            ),
        state=States.game_input,
    ),
    
    # второй этап - выбор id записи
    InnerWindow(
        *CommonWidgets.select_record_id(
            EventHandler,
        ),
        state=States.select_record_id,
        getter=Getter.get_record_ids
    )
)