from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import (
    Const, Format
)
from aiogram_dialog.widgets.kbd import Button

from app.interfaces.bot.dialogs.core import RootWindow

from .states import WarehouseAndDeliverySG as States
from .event_handler import WarehouseAndDeliveryEventHandler as EventHandler


warehouse_and_delivery_dialog = Dialog(
    
    #первый этап - выбор игр, которые получаю, и которые отдаю 
    RootWindow(
        Format('{start_data[menu_text]}\n\n'),
        Button(
            Const('Выгрузить'),
            id='upload',
            on_click=EventHandler.on_upload_records
        ),
        state=States.upload
    )
    
)