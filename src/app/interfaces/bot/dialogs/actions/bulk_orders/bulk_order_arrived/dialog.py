from aiogram_dialog import Dialog

from app.interfaces.bot.dialogs.common.widgets import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow

from .states import BulkOrderArrivedSG as States
from .event_handler import BulkOrderArrivedEventHandler as EventHandler
from .getter import BulkOrderArrivedGetter as Getter


bulk_order_arrived_dialog = Dialog(
    
    #первый этап - выбор оптового заказа
    RootWindow(
        *CommonWidgets.select_bulk_order_id(EventHandler),
        getter=Getter.get_bulk_order_ids,
        state=States.select_bulk_order_id
    ),
    on_start=EventHandler.on_start
)