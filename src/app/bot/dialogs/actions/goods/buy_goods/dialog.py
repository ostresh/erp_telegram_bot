from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import (
    Button, SwitchTo, Back, Cancel,
    Group, Row, Column,
    Select, Multiselect, Radio, Checkbox,
    ScrollingGroup, NextPage, PrevPage,
    Url, Counter, Calendar,
)
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Case, Multi,
)
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import SwitchInlineQueryCurrentChat

from app.bot.utils.emoji import Emoji
from app.bot.messages.menu import MenuConstants
from app.bot.dialogs.common import CommonDialogNavigation

from .states import BuyGoodsSG
from .event_handler import BuyGoodsEventHandler
from .getters import BuyGoodsGetters


buy_goods_dialog = Dialog(
    
    # первый этап - выбор игры
    Window(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'<b>{Emoji.GAME} ВВЕДИТЕ НАЗВАНИЕ ИГРЫ </b>'),
            sep='\n\n'
        ),
        
        SwitchInlineQueryCurrentChat(
            Const('🔍 ПОИСК ИГРЫ'),
            Const('')
        ),
        CommonDialogNavigation.root_controls,
        TextInput(
            id='type_game',
            type_factory=str,
            on_success=BuyGoodsEventHandler.on_game_typed
        ),
        state=BuyGoodsSG.type_game,
    ),
    
    # второй этап - выбор способа получения
    Window(
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
           on_click=BuyGoodsEventHandler.on_receive_method_selected
        ),
        CommonDialogNavigation.inner_controls,
        state=BuyGoodsSG.receive_method,
        getter=BuyGoodsGetters.get_local_or_delivery
    ),
    
    # третий этап - ввод закупочной цены
    Window(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game]}}</b>'),
            Format('<b>{dialog_data[receive_title]}</b>'),
            Format(f'{Emoji.PRICE_BUY} <b>Введите закупочную стоимость</b>'),
            sep='\n\n'
        ),
        CommonDialogNavigation.inner_controls,
        TextInput(
            id='type_purchase_price',
            type_factory=int,
            on_success=BuyGoodsEventHandler.on_price_purchase_typed
        ),
        state=BuyGoodsSG.type_price_purchase
    )
)