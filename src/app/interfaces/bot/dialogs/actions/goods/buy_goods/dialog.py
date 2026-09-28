from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import BuyGoodsSG as States
from .event_handler import BuyGoodsEventHandler as EventHandler
from .getter import BuyGoodsGetter as Getter

buy_goods_dialog = Dialog(
    
    # первый этап - выбор игры
    RootWindow(
        *CommonWidgets.game_input(
            EventHandler
        ),
        state=States.game_input,
    ),
    
    # второй этап - выбор способа получения
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game_name]}}</b>'),
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
    
    # третий этап - ввод закупочной цены
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game_name]}}</b>'),
            Format('<b>{dialog_data[receive_title]}</b>'),
            Format(f'{Emoji.PRICE_PURCHASE} <b>Введите закупочную стоимость</b>'),
            sep='\n\n'
        ),
        TextInput(
            id='type_purchase_price',
            type_factory=int,
            on_success=EventHandler.on_price_purchase_typed,
            on_error=EventHandler.on_int_error
        ),
        state=States.input_price_purchase
    )
)