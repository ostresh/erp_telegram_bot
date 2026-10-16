from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import UpdateGameSG as States
from .event_handler import UpdateGameEventHandler as EventHandler

update_game_dialog = Dialog(
    
    # первый этап - ввод названия игры
    RootWindow(
        *CommonWidgets.game_input(EventHandler),
        state=States.game_input,
    ),
    
    # второй этап - ввод нового названия
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game_name]}}</b>'),
            Const('Введите новое название игры'),
            sep='\n\n'
        ),
        TextInput(
            id='new_name_input',
            type_factory=str,
            on_success=EventHandler.on_new_name_typed,
            on_error=EventHandler.on_text_error
        ),
        state=States.new_name_input
    ),
)