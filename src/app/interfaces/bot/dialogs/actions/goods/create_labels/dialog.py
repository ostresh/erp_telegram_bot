from enum import Enum

from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.kbd import Button, Group, Select, SwitchTo
from aiogram_dialog.widgets.input import TextInput

from app.core.dto.labels import DeliveryType
from app.interfaces.bot.dialogs.common.widgets import CommonWidgets
from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import CreateLabelsSG as States
from .event_handler import CreateLabelsEventHandler as EventHandler
from .getter import CreateLabelsGetter as Getter


create_labels_dialog = Dialog(
    
    # основное окно 
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja(
                '{%- if dialog_data["dtos"] -%}'
                '{% set dtos = dialog_data["dtos"] %}'
                '<b>Заказы:\n\n</b>'
                '{% for dto in dtos %}'
                    '<b>{{dto.order_number}} ({{dto.delivery.display_name}}):\n</b>'
                    '{% for item in dto.items %}'
                        '{{item.game_name}} x{{item.count}}\n'
                    '{% endfor %}'
                    '\n\n'
                '{% endfor %}'
                '{% else %}'
                '<b>Добавьте новый заказ</b>'
                '{%- endif -%}'
            ),
            sep='\n\n'
        ),
        SwitchTo(
            Const('Добавить заказ'),
            id='add_order',
            state=States.order_number_input
        ),
        Button(
            Const('Далее →'),
            id='next',
            on_click=EventHandler.on_end_dialog,
        ),
        state=States.main
    ),
    
    # введение номера заказа
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const('<b>Введите номер заказа:</b>'),
            sep='\n\n'
        ),
        TextInput(
            id='order_number_input',
            type_factory=str,
            on_success=EventHandler.on_order_number_input,
            on_error=EventHandler.on_text_error
        ),
        state=States.order_number_input
    ),
    
    # выбор доставки
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>Заказ: {{dialog_data[order_number]}}</b>'),
            Const('Выберите доставку:'),
            sep='\n\n'
        ),
        Group(
            Select(
                Format("{item[name]}"),
                id="game_select",
                item_id_getter=lambda x: x["id"],
                items="deliveries",
                on_click=EventHandler.on_delivery_selected,
            ),
            width=1
        ),
        state=States.delivery_input,
        getter=Getter.get_delivery_type
    ),
    
    # главное меню добавления игр
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>Заказ: {{dialog_data[order_number]}}</b>'),
            Format(f'<b>Доставка: {{dialog_data[delivery].display_name}}</b>'),
            Jinja(
                '{%- if dialog_data["game_names"] -%}'
                '<b>Игры:\n</b>'
                '{% for item in dialog_data["game_names"] %}'
                '{{item}}\n'
                '{% endfor %}'
                '{% else %}'
                '<b>Добавьте игры</b>'
                '{%- endif -%}'
            ),
            sep='\n\n'
        ),
        SwitchTo(
            Const('Добавить игру'),
            id='add_order',
            state=States.game_input
        ),
        Button(
            Const('Далее →'),
            id='next',
            on_click=EventHandler.create_order,
        ),
        state=States.main_game_input,
    ),
    
    # добавление игры
    InnerWindow(
        *CommonWidgets.game_input(
            EventHandler,
            switch_inline_query_text=Const('@available ')
        ),
        state=States.game_input
    )
    
)