from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler.mixins import ValidationMixin
from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import ReserveSG as States
from .event_handler import ReserveEventHandler as EventHandler
from .getter import ReserveGetter as Getter


reserve_dialog = Dialog(
    
    # первый этап - ввод игры 
    RootWindow(
        *CommonWidgets.game_input(
            EventHandler,
            switch_inline_query_text=Const('@available ')
        ),
        state=States.game_input
    ),
    
    # второй этап - выбор id записи
    InnerWindow(
        *CommonWidgets.select_record_id(EventHandler),
        state=States.select_record_id,
        getter=Getter.get_record_ids
    ),
    
    # третий этап - ввод брони
    InnerWindow(
       Multi(
            Format('{start_data[menu_text]}'),
            Jinja("""
            {%- if dialog_data['f_record'] -%}                  
            {{dialog_data['f_record'] | safe}}
            {%- else -%}
            <b>{{-dialog_data['emoji_game']}} ИГРА: {{dialog_data['game_name']-}}</b>
            {%- endif -%}
            """),
            Const(f'<b>{Emoji.RESERVE} Введите информацию о брони </b>'),
            sep='\n\n'
        ),
        TextInput(
            id='type_reserve',
            type_factory=str,
            on_success=EventHandler.on_reserve_typed,
            on_error=ValidationMixin.on_text_error
        ),
        state=States.reserve_input
    )
    
)