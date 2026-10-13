from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.validators import CommonValidators
from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.core import RootWindow

from .states import CreateBulkOrderSG as States
from .event_handler import CreateBulkOrderEventHandler as EventHandler


create_bulk_order_dialog = Dialog(
    
    #первый этап - ввод json
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'<b>{Emoji.BULK_ORDER} Введите JSON код </b>'),
            sep='\n\n'
        ),
        TextInput(
            id='input_json',
            type_factory=CommonValidators.validate_json_for_bulk_order,
            on_success=EventHandler.on_input_json,
            on_error=EventHandler.on_text_error
        ),
        state=States.input_json
    ),
)