from aiogram_dialog import Dialog, ShowMode
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Group, SwitchInlineQueryCurrentChat, SwitchTo

from app.core.db.statuses.record import RecordStatus
from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import ChangeRecordSG as States
from .event_handler import ChangeRecordEventHandler as EventHandler
from .getter import ChangeRecordGetter as Getter

back_button = Button(
    Const('← Назад'),
    id='back_button',
    on_click=EventHandler.on_back
)

change_record_dialog = Dialog(
    
    # первый этап - ввод игры
    RootWindow(
        *CommonWidgets.game_input(
            EventHandler,
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
    ),
    
    # третий этап - выбор кнопки для изменения
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("""
            {%- if dialog_data['f_record'] -%}                  
            {{dialog_data['f_record'] | safe}}
            {%- endif -%}
            """),
            Const(f'Выберите атрибут для изменения:'),
            sep='\n\n',
        ),
        Group(
            # ===== Связи =====
            SwitchTo(
                text=Const(f'{Emoji.GAME} ИЗМЕНИТЬ ИГРУ'),
                id='game_id',
                state=States.change_game,
                show_mode=ShowMode.EDIT
            ),
            Button(
                text=Const(f'{Emoji.BULK_ORDER} ИЗМЕНИТЬ ОПТОВЫЙ ЗАКАЗ'),
                id='bulk_order_id',
                on_click=EventHandler.on_change_attribute_button,
            ),

            # ===== Даты =====
            Button(
                text=Const(f'{Emoji.DATE} ИЗМЕНИТЬ ДАТУ ПОКУПКИ'),
                id='purchase_at',
                on_click=EventHandler.on_change_attribute_button,
            ),
            Button(
                text=Const(f'{Emoji.DATE} ИЗМЕНИТЬ ДАТУ ПРОДАЖИ'),
                id='sold_at',
                on_click=EventHandler.on_change_attribute_button,
            ),

            # ===== Цены =====
            Button(
                text=Const(f'{Emoji.PRICE_PURCHASE} ИЗМЕНИТЬ ЦЕНУ ПОКУПКИ'),
                id='price_purchase',
                on_click=EventHandler.on_change_attribute_button,
            ),
            Button(
                text=Const(f'{Emoji.PRICE_SELLING} ИЗМЕНИТЬ ЦЕНУ ПРОДАЖИ'),
                id='price_selling',
                on_click=EventHandler.on_change_attribute_button,
            ),
            Button(
                text=Const(f'{Emoji.PRICE_SOLD} ИЗМЕНИТЬ ЦЕНУ ФАКТ. ПРОДАЖИ'),
                id='price_sold',
                on_click=EventHandler.on_change_attribute_button,
            ),

            # ===== Статус и специальные поля =====
            SwitchTo(
                text=Const(f'{Emoji.STATUS} ИЗМЕНИТЬ СТАТУС'),
                id='status',
                state=States.change_status,
            ),
            Button(
                text=Const(f'{Emoji.SWAP} ИЗМЕНИТЬ ОБМЕН'),
                id='swap',
                on_click=EventHandler.on_change_attribute_button,
            ),
            Button(
                text=Const(f'{Emoji.RESERVE} ИЗМЕНИТЬ РЕЗЕРВ'),
                id='reserve',
                on_click=EventHandler.on_change_attribute_button,
            ),
            Button(
                text=Const(f'{Emoji.COMMENT} ИЗМЕНИТЬ КОММЕНТАРИЙ'),
                id='comment',
                on_click=EventHandler.on_change_attribute_button,
            ),
            Button(
                text=Const('Далее →'),
                id='end_dialog',
                on_click=EventHandler.end_dialog
            ) 
        ),
        state=States.main
    ),
    
    # окно изменения атрибута
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("""
            {%- if dialog_data['f_record'] -%}                  
            {{dialog_data['f_record'] | safe}}
            {%- endif -%}
            """),
            Format('<b>{dialog_data[attribute_title]}</b>'),
            Const(f'Введите новое значение:'),
            sep='\n\n',
        ),
        TextInput(
            id='change_attribute',
            type_factory=str,
            on_success=EventHandler.on_change_attribute,
            on_error=EventHandler.on_text_error
        ),
        state=States.change_attribute,
        back_button=back_button
    ),
    
    # окно изменения игры
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("{%- if dialog_data.get('game_error') -%}❌ {{ dialog_data['game_error'] }}\n\n{%- endif -%}"),
            Const(f'<b>{Emoji.GAME} ВВЕДИТЕ НАЗВАНИЕ ИГРЫ </b>'),
            sep='\n\n'
        ),
        SwitchInlineQueryCurrentChat(
            Const('🔍 ПОИСК ИГРЫ'),
            Const('')
        ),
        TextInput(
            id='type_game',
            type_factory=str,
            on_success=EventHandler.on_game_attribute_type,
            on_error=EventHandler.on_text_error
        ),
        state=States.change_game,
        back_button=back_button
    ),
    
    # окно изменения статуса
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("""
            {%- if dialog_data['f_record'] -%}                  
            {{dialog_data['f_record'] | safe}}
            {%- endif -%}
            """),
            Const(f'Выберите новое значение:'),
            sep='\n\n',
        ),
        Group(
            Button(
                text=Const(RecordStatus.AVAILABLE.display_name),
                id=RecordStatus.AVAILABLE.value,
                on_click=EventHandler.on_change_status,
            ),
            Button(
                text=Const(RecordStatus.SOLD.display_name),
                id=RecordStatus.SOLD.value,
                on_click=EventHandler.on_change_status,
            ),
            Button(
                text=Const(RecordStatus.IN_TRANSIT_TO_ME.display_name),
                id=RecordStatus.IN_TRANSIT_TO_ME.value,
                on_click=EventHandler.on_change_status,
            ),
            Button(
                text=Const(RecordStatus.IN_TRANSIT_TO_CLIENT.display_name),
                id=RecordStatus.IN_TRANSIT_TO_CLIENT.value,
                on_click=EventHandler.on_change_status,
            ),
            width=2,
        ),
        state=States.change_status,
        back_button=back_button
    )
)