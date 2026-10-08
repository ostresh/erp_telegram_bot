from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import SellGoodsSG as States
from .event_handler import SellGoodsEventHandler as EventHandler
from .getter import SellGoodsGetter as Getter



sell_goods_dialog = Dialog(
    
    # первый этап - ввод игры
    RootWindow(
        *CommonWidgets.game_input(
            EventHandler,
            switch_inline_query_text=Const('@available ')
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
           id='receive_select',
           item_id_getter=lambda item: item.get('id'),
           items='methods',
           on_click=EventHandler.on_receive_method_selected
        ),
        state=States.receive_method,
        getter=Getter.get_delivery
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
            id='type_price_sold',
            type_factory=int,
            on_success=EventHandler.on_price_sold_typed,
            on_error=EventHandler.on_int_error
        ),
        state=States.input_price_sold
    )
)