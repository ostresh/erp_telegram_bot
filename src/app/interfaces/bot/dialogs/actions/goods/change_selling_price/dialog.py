from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import ChangeSellingPriceSG as States
from .event_handler import ChangeSellingPriceEventHandler as EventHandler
from .getter import ChangeSellingPriceGetter as Getter

change_selling_price_dialog = Dialog(
    
    # первый этап - выбор игры
    RootWindow(
        *CommonWidgets.game_input(
            EventHandler,
            switch_inline_query_text=Const('@available ')
        ),
        state=States.game_input,
    ),
    
    # второй этап - ввод цены продажи
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Format(f'<b>{Emoji.GAME} ИГРА: {{dialog_data[game_name]}}</b>'),
            Format(f'<b>{Emoji.PRICE_SELLING} Текущие цены: {{prices}}</b>'),
            Const(f'{Emoji.PRICE_SELLING} Введите цену для продажи:'),
            sep='\n\n'
        ),
        TextInput(
            id='change_selling_price',
            type_factory=int,
            on_success=EventHandler.on_input_price_selling,
            on_error=EventHandler.on_int_error
        ),
        getter=Getter.get_prices_selling,
        state=States.input_price_selling
    ),
)