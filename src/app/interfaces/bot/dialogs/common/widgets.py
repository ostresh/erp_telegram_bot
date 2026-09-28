from typing import Union
from aiogram_dialog.widgets.text import (
    Const, Format, Multi, Jinja, Text
)
from aiogram_dialog.widgets.utils import WidgetSrc
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import SwitchInlineQueryCurrentChat
from aiogram_dialog.widgets.kbd import ScrollingGroup, Group, Select, Button

from app.interfaces.bot.utils.emoji import Emoji

from .event_handler import CommonEventHandler

class CommonWidgets:
    
    @staticmethod
    def game_input(handler: type[CommonEventHandler], *text_widgets: Text, switch_inline_query_text: Union[Const, Format] = Const('')) -> tuple[WidgetSrc, ...]:
        """
        Полный базовый блок окна ввода игры.

        Композиция:
            шапка меню → ошибка игры (если есть) → доп. строки → приглашение
            → кнопка инлайн-поиска → поле ввода

        Обработчик успеха берётся из переданного класса: метод
        on_game_typed одинаков во всех диалогах (наследуется из
        CommonEventHandler), а поведение различается через полиморфизм
        (cls во Флоу/Геттерах).

        Args:
            handler: класс EventHandler конкретного диалога
            texts: дополнительные текстовые виджеты в шапку
            switch_inline_query_text: Const | Format с заполненной строкой

        Returns:
            кортеж виджетов — в окно распаковывается через *
        """
        
        return (
            Multi(
                Format('{start_data[menu_text]}'),
                *text_widgets,
                Jinja("{%- if dialog_data.get('game_error') -%}❌ {{ dialog_data['game_error'] }}\n\n{%- endif -%}"),
                Const(f'<b>{Emoji.GAME} ВВЕДИТЕ НАЗВАНИЕ ИГРЫ </b>'),
                sep='\n\n'
            ),
            SwitchInlineQueryCurrentChat(
                Const('🔍 ПОИСК ИГРЫ'),
                switch_inline_query_text
            ),
            TextInput(
                id='type_game',
                type_factory=str,
                on_success=handler.on_game_typed,
                on_error=CommonEventHandler.on_text_error
            ),
        )
        
    @staticmethod
    def select_record_id(handler: type[CommonEventHandler], *text_widgets: Text) -> tuple[WidgetSrc, ...]:
        """
        Базовый шаблон для выбора ID записи. Позволяет вставить другие виджеты в шаблон
        
        Композиция:
            шапка меню → доп. строки → отформатированная строка записи → кнопки выбора ID
        
        Args:
            handler: класс EventHandler конкретного диалога
            widgets: другие виджеты, которые нужно вставить в шаблон
        """
        
        return (
            Multi(
                Format('{start_data[menu_text]}'),
                *text_widgets,
                Jinja("""
                {%- if dialog_data['f_record'] -%}                  
                {{dialog_data['f_record'] | safe}}
                {%- else -%}
                <b>{{-dialog_data['emoji_game']}} ИГРА: {{dialog_data['game_name']-}}</b>
                {%- endif -%}
                """),
                Const(f'{Emoji.ID} Выберите ID записи:', when='has_multiple'),
                sep='\n\n',
            ),
            
            # если больше 15 элементов, подключается пагинация
            ScrollingGroup(
                Select(
                    Format('{item[id]}'),
                    id="record_id_select_scroll",
                    item_id_getter=lambda item: item.get('id'),
                    items="game_ids",
                    on_click=handler.on_record_id_selected,
                    type_factory=int
                ),
                id="items_scroll",
                width=3,
                height=5,
                when='needs_scrolling'
            ),
            
            # если меньше 15, без пагинации
            Group(
                Select(
                    Format('{item[id]}'),
                    id="record_id_select_group",
                    item_id_getter=lambda item: item.get('id'),
                    items="game_ids",
                    on_click=handler.on_record_id_selected,
                    type_factory=int
                ),
                width=3,
                when='needs_plain_group'
            ),
            Button(
                Const('Далее →'),
                id='select_record_id_button',
                on_click=handler.on_select_record_id_button
            )
        )
        