from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.core import RootWindow
from app.interfaces.bot.utils.emoji import Emoji

from .states import ProductReportSG as States
from .event_handler import ProductReportEventHandler as EventHandler


product_report_dialog = Dialog(
    
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'{Emoji.DATE} Введите период даты в формате DD.MM.YYYY - DD.MM.YYYY:'),
            sep='\n\n'
        ),
        TextInput(
            id='type_period',
            type_factory=str,
            on_success=EventHandler.on_date_input,
            on_error=EventHandler.on_text_error
        ),
        state=States.type_period
    ),
)