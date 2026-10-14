from aiogram_dialog import Dialog

from app.interfaces.bot.dialogs.common.widgets import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow

from .states import ViewOrdersSG as States
from .event_handler import ViewOrdersEventHandler as EventHandler
from .getter import ViewOrdersGetter as Getter


view_orders_dialog = Dialog(
    
    #первый этап - выбор оптового заказа
    RootWindow(
        *CommonWidgets.select_bulk_order_id(EventHandler),
        getter=Getter.get_bulk_order_ids,
        state=States.select_bulk_order_id
    ),
    on_start=EventHandler.on_start
)