from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.text import (
    Const, Format, Multi, Jinja
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import SwitchInlineQueryCurrentChat, ScrollingGroup, Group

from app.bot.utils.emoji import Emoji
from app.bot.dialogs.common import CommonGetter, CommonEventHandler
from app.bot.dialogs.core import RootWindow, InnerWindow

from .states import SellGoodsSG
from .event_handler import SellGoodsEventHandler
from .getter import SellGoodsGetter



sell_goods_dialog = Dialog(
    
    # первый этап - выбор игры
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'<b>{Emoji.GAME} ВВЕДИТЕ НАЗВАНИЕ ИГРЫ </b>'),
            sep='\n\n'
        ),
        
        SwitchInlineQueryCurrentChat(
            Const('🔍 ПОИСК ИГРЫ'),
            Const('@available ')
        ),
        TextInput(
            id='type_game',
            type_factory=str,
            on_success=SellGoodsEventHandler.on_game_typed,
            on_error=CommonEventHandler.on_text_error
        ),
        state=SellGoodsSG.type_game,
    ),
    
    # второй этап - выбор id игры
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("""
{%- if dialog_data['f_record']  -%}                  
{{dialog_data['f_record'] | safe}}
{%- else -%}
<b>{{-dialog_data['emoji_game']}} ИГРА: {{dialog_data['game']-}}</b>
{%- endif -%}
"""),
            Const(f'{Emoji.ID} Выберите ID записи:', when='is_not_one'),
            sep='\n\n',
        ),
        
        # если больше 15 элементов, подключается пагинация
        ScrollingGroup(
            Select(
                Format('{item[title]}'),
                id="record_id_select",
                item_id_getter=lambda item: item["id"],
                items="game_ids",
                on_click=SellGoodsEventHandler.on_record_id_selected,
            ),
            id="items_scroll",
            width=3,
            height=5,
            when='gt_pagination_threshold'
        ),
        
        # если меньше 15, без пагинации
        Group(
            Select(
                Format('{item[title]}'),
                id="record_id_select",
                item_id_getter=lambda item: item["id"],
                items="game_ids",
                on_click=SellGoodsEventHandler.on_record_id_selected
            ),
            width=3,
            when='le_pagination_threshold'
        ),
        Button(
            Const('Далее →'),
            id='select_record_id_button',
            on_click=SellGoodsEventHandler.on_record_id_switch_to
        ),
        state=SellGoodsSG.select_record_id,
        getter=SellGoodsGetter.get_available_record_ids
    ),
    
    # третий этап - выбор способа получения
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format('{dialog_data[f_record]}'),
            Const(f'{Emoji.LOCAL_OR_DELIVERY} Выберите способ получения:'),
            sep='\n\n'
        ),
        Select(
           Format('{item[title]}'),
           id = 'receive_select',
           item_id_getter=lambda item: item.get('id'),
           items = 'methods',
           on_click=CommonEventHandler.on_receive_method_selected
        ),
        state=SellGoodsSG.receive_method,
        getter=CommonGetter.get_local_or_delivery
    ),
    
    # четвертый этап - ввод цены продажи
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format('{dialog_data[f_record]}'),
            Format('<b>{dialog_data[receive_title]}</b>'),
            Format(f'{Emoji.PRICE_SOLD} <b>Введите цену продажи</b>'),
            sep='\n\n'
        ),
        TextInput(
            id='type_purchase_price',
            type_factory=int,
            on_success=SellGoodsEventHandler.on_price_sold_typed,
            on_error=CommonEventHandler.on_int_error
        ),
        state=SellGoodsSG.type_price_sold
    )
)