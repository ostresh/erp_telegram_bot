from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Multi, Format
)
from aiogram_dialog.widgets.input import TextInput
from app.interfaces.bot.dialogs.core import RootWindow

from app.interfaces.bot.utils.emoji import Emoji

from .states import ChangeDescriptionSG as States
from .event_handler import ChangeDescriptionEventHandler as EventHandler


change_description_dialog = Dialog(
    
    #первый этап - ввод нового описания
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.DESCRIPTION} СТАРОЕ ОПИСАНИЕ ↑</b>'),
            Format(f'<b>Введите новое описание</b>'),
            sep='\n\n'
        ),
        TextInput(
            id='input_new_desc',
            type_factory=str,
            on_success=EventHandler.on_new_desc_input,
            on_error=EventHandler.on_text_error
        ),
        state=States.new_description_input
    ),
    on_start=EventHandler.on_start
)