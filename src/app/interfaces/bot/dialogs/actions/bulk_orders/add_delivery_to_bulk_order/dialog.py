from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Multi
)
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.widgets import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow
from app.interfaces.bot.utils.emoji import Emoji

from .states import AddDeliveryToBulkOrderSG as States
from .event_handler import AddDeliveryToBulkOrderEventHandler as EventHandler
from .getter import AddDeliveryToBulkOrderGetter as Getter


add_delivery_to_bulk_order_dialog = Dialog(
    
    #первый этап - выбор оптового заказа
    RootWindow(
        *CommonWidgets.select_bulk_order_id(EventHandler),
        getter=Getter.get_bulk_order_ids,
        state=States.select_bulk_order_id
    ),
    
    # второй этап - ввод стоимости доставки
    InnerWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Jinja("""
            {%- if dialog_data['f_bulk_order'] -%}                  
            {{dialog_data['f_bulk_order'] | safe}}
            {%- endif -%}
            """),
            Const(f'{Emoji.BULK_ORDER_DELIVERY_COST} Введите стоимость доставки'),
            sep='\n\n'
        ),
        TextInput(
            id='type_delivery_cost',
            type_factory=int,
            on_success=EventHandler.on_delivery_price_typed,
            on_error=EventHandler.on_int_error
        ),
        state=States.input_delivery_price
    ),
    on_start=EventHandler.on_start
)