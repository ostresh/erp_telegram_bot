from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format, Multi
)
from aiogram_dialog.widgets.kbd import Select

from app.interfaces.bot.utils.emoji import Emoji
from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow, InnerWindow

from .states import OrderArrivedSG as States
from .event_handler import OrderArrivedEventHandler as EventHandler
from .getter import OrderArrivedGetter as Getter


order_arrived_dialog = Dialog(
    
    #первый этап - выбор получателя 
    RootWindow(
        Multi(
            Format('{start_data[menu_text]}'),
            Const(f'<b>{Emoji.LOCAL_OR_DELIVERY} Выберите, к кому прибыл заказ </b>'),
            sep='\n\n'
        ),
        Select(
            Format('{item[title]}'),
            id='select_order_recipient',
            item_id_getter=lambda item: item.get('id'),
            items='methods',
            on_click=EventHandler.on_recipient_type_selected
        ),
        getter=Getter.get_order_recipient,
        state=States.select_order_recipient
    ),
    
    # второй этап - ввод игры
    InnerWindow(
        *CommonWidgets.game_input(
            EventHandler,
            Format('<b>{dialog_data[recipient_title]}</b>'),
            switch_inline_query_text=Format('@{dialog_data[recipient_type]} ')
            ),
        state=States.game_input,
    ),
    
    # третий этап - выбор id записи
    InnerWindow(
        *CommonWidgets.select_record_id(
            EventHandler,
            Format('<b>{dialog_data[recipient_title]}</b>'),
        ),
        state=States.select_record_id,
        getter=Getter.get_record_ids
    ),
)