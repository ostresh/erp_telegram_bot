from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.core import RootWindow

from .states import DeleteRecordSG as States
from .event_handler import DeleteRecordEventHandler as EventHandler


delete_record_dialog = Dialog(
    
    # первый этап - ввод игры
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("{%- if dialog_data.get('record_error') -%}❌ {{ dialog_data['record_error'] }}\n\n{%- endif -%}"),
            Jinja("{%- if dialog_data.get('f_record') -%} {{ dialog_data['f_record'] | safe}}\n\n{%- endif -%}"),
            Const(f'<b>{Emoji.ID} Введите ID записи </b>'),
            sep='\n\n'
        ),
        TextInput(
            id='input_record_id',
            type_factory=int,
            on_error=EventHandler.on_int_error,
            on_success=EventHandler.on_record_id_typed
        ),
        Button(
          text=Const('Далее →'),
          id='end_dialog',
          on_click=EventHandler.end_dialog  
        ),
        state=States.record_input,
    ),
)