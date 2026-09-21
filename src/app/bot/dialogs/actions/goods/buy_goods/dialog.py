from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import (
    Const, Format, Multi,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import SwitchInlineQueryCurrentChat

from app.bot.utils.emoji import Emoji
from app.bot.dialogs.common import CommonGetter, CommonEventHandler
from app.bot.dialogs.core import RootWindow, InnerWindow

from .states import BuyGoodsSG
from .event_handler import BuyGoodsEventHandler



buy_goods_dialog = Dialog(
    
    # первый этап - выбор игры
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
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
            on_success=BuyGoodsEventHandler.on_game_typed,
            on_error=CommonEventHandler.on_text_error
        ),
        state=BuyGoodsSG.type_game,
    ),
    
    # второй этап - выбор способа получения
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game]}}</b>'),
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
        state=BuyGoodsSG.receive_method,
        getter=CommonGetter.get_local_or_delivery
    ),
    
    # третий этап - ввод закупочной цены
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game]}}</b>'),
            Format('<b>{dialog_data[receive_title]}</b>'),
            Format(f'{Emoji.PRICE_BUY} <b>Введите закупочную стоимость</b>'),
            sep='\n\n'
        ),
        TextInput(
            id='type_purchase_price',
            type_factory=int,
            on_success=BuyGoodsEventHandler.on_price_purchase_typed,
            on_error=CommonEventHandler.on_int_error
        ),
        state=BuyGoodsSG.type_price_purchase
    )
)