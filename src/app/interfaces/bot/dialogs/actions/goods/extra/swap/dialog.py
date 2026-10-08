from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.kbd import Button, Group

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import SwapSG as States
from .event_handler import SwapEventHandler as EventHandler
from .getter import SwapGetter as Getter

back_button = Button(
    Const('← Назад'),
    id='back_button',
    on_click=EventHandler.on_back
)

swap_dialog = Dialog(
    
    #первый этап - выбор игр, которые получаю, и которые отдаю 
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'{Emoji.SWAP_OUT} ИСХОДЯЩИЕ'),
            Jinja("""
                  {%- if dialog_data.get('games_out') -%}
                  {%- for game in dialog_data.get('games_out') -%}
                  {{ game | safe }}{% if not loop.last %}{{ '\n' }}{% endif -%}
                  {%- endfor -%}
                  {%- endif -%}
                  """),
            Const(f'{Emoji.SWAP_IN} ВХОДЯЩИЕ'),
            Jinja("""
                {%- if dialog_data.get('games_in') -%}
                {%- for game in dialog_data.get('games_in') -%}
                <b>{{dialog_data.get('emoji_game')}} {{ game | safe }}</b>{% if not loop.last %}{{ '\n' }}{% endif -%}
                {%- endfor -%}
                {%- endif -%}
                """),
            Const(f'<b>{Emoji.SWAP} Выберите игры для обмена </b>'),
            sep='\n\n'
        ),
        Group(
            Button(
                Const(f'{Emoji.SWAP_OUT} ВЫБРАТЬ ИСХОДЯЩИЕ'),
                id='swap_out',
                on_click=EventHandler.on_swap_out_button,
            ),
            Button(
              Const(f'{Emoji.SWAP_IN} ВЫБРАТЬ ВХОДЯЩИЕ'),
              id='swap_in',
              on_click=EventHandler.on_swap_in_button,
            ),
            Button(
                Const('Далее →'),
                id='go_next',
                on_click=EventHandler.on_finish_dialog
            ),
            width=1
        ),
        state=States.main
    ),
    
    # Окно выбора игр, которые отдаю
    InnerWindow(
        *CommonWidgets.game_input(
            EventHandler,
            Format("{dialog_data[swap_title]}"),
            switch_inline_query_text=Const('@available ')
        ),
        state=States.giving_input,
        back_button=back_button
    ),
    
    # выбор id записи для исходящих
    InnerWindow(
        *CommonWidgets.select_record_id(
            EventHandler,
        ),
        state=States.select_record_id,
        getter=Getter.get_record_ids,
    ),
    
    # Окно выбора игр, которые получаю
    InnerWindow(
        *CommonWidgets.game_input(
            EventHandler,
            Format("{dialog_data[swap_title]}"),
            switch_inline_query_text=Const('')
        ),
        state=States.getting_input,
        back_button=back_button
    ),
)