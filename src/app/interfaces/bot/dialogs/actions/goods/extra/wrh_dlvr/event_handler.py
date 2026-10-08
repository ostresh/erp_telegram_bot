from typing import ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors

from .states import WarehouseAndDeliverySG
from .flow import WarehouseAndDeliveryFlow

import logging

logger = logging.getLogger(__name__)

class WarehouseAndDeliveryEventHandler(CommonEventHandler):
    """
    Обработчик для wrh_dvlr
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: WarehouseAndDeliveryFlow
        - States: WarehouseAndDeliverySG
    """
    flow: ClassVar[type[WarehouseAndDeliveryFlow]] = WarehouseAndDeliveryFlow
    states: ClassVar[type[WarehouseAndDeliverySG]] = WarehouseAndDeliverySG
    
    @classmethod
    @handle_db_errors
    async def on_upload_records(
        cls,
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик для кнопки выгрузки записей, которые едут ко мне
        """
        
        manager.show_mode = ShowMode.DELETE_AND_SEND
        
        await callback.answer()
        
        getter = cls.flow.get_items(manager)
        formatter = cls.flow.formatter(manager)
        
        items = await getter(manager)
        
        if not items:
            await cls.flow.finish_dialog_with_result(
                manager,
                text = '⚠️ Таких записей нет'
            )
        else:
            f_items = await formatter(manager, items)
            await cls.flow.finish_dialog_with_many_result(manager, f_items)
        