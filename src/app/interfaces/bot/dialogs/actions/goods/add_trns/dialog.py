from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import AddTrnsSG as States
from .event_handler import AddTrnsEventHandler as EventHandler
from .getter import AddTrnsGetter as Getter


add_trns_dialog = Dialog(
    
    #первый этап - выбор Utility 
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'<b>{Emoji.TRNS} Выберите транзакцию </b>'),
            sep='\n\n'
        ),
        Group(
            Select(
                Format('{item[title]}'),
                id='trns_select',
                item_id_getter=lambda item: item.get('id'),
                items='utils',
                on_click=EventHandler.on_trns_selected
            ),
            width=1
        ),
        getter=Getter.get_utils,
        state=States.util_select
    ),
    
    # второй этап - ввод расхода
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.TRNS} ТРАНЗАКЦИЯ: {{dialog_data[util_title]}}</b>'),
            Format(f'{Emoji.PRICE_PURCHASE} Введите расход:'), 
            sep='\n\n'
        ),
        TextInput(
            id='price_purchase_input',
            type_factory=int,
            on_success=EventHandler.on_price_purchase_input,
            on_error=EventHandler.on_int_error
        ),
        state=States.input_price_purchase
    ),
    
    # третий этап - завершение диалога
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.TRNS} ТРАНЗАКЦИЯ: {{dialog_data[util_title]}}</b>'),
            Format(f'<b>{Emoji.PRICE_PURCHASE} {{dialog_data[price_purchase]}}</b>'),
            Jinja(
                '{%- if dialog_data["comment"] -%}'
                '<b>{{ dialog_data["emoji"] }} {{ dialog_data["comment"] }}</b>'
                '{%- endif -%}'
            ),
            sep='\n\n'
        ),
        Button(
            Format(f'{Emoji.COMMENT} ДОБАВИТЬ КОММЕНТАРИЙ'),
            id='add_comment',
            on_click=EventHandler.on_add_comment_button
        ),
        Button(
            Const('Далее →'),
            id='end_dialog',
            on_click=EventHandler.on_end_dialog
        ),
        state=States.end_dialog
    ),
    
    # опциональное окно - ввод комментария
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.TRNS} ТРАНЗАКЦИЯ: {{dialog_data[util_title]}}</b>'),
            Format(f'<b>{Emoji.PRICE_PURCHASE} {{dialog_data[price_purchase]}}</b>'),
            Format(f'{Emoji.COMMENT} Введите комментарий:'), 
            sep='\n\n'
        ),
        TextInput(
            id='input_comment',
            type_factory=str,
            on_success=EventHandler.on_comment_input,
            on_error=EventHandler.on_text_error
        ),
        state=States.input_comment
    )
)