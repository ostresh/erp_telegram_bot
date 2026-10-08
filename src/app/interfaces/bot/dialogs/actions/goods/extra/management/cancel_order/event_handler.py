from typing import ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from app.core.db.statuses import RecordStatus
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import CancelOrderSG
from .flow import CancelOrderFlow

import logging

logger = logging.getLogger(__name__)

class CancelOrderEventHandler(CommonEventHandler):
    """
    Обработчик для cancel-order
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: CancelOrderFlow
        - States: CancelOrderSG
    """
    flow: ClassVar[type[CancelOrderFlow]] = CancelOrderFlow
    states: ClassVar[type[CancelOrderSG]] = CancelOrderSG
    
    
    @classmethod
    @handle_db_errors
    async def on_select_record_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """Переход к следующему шагу, если выбран record_id"""
        
        if not await cls.flow.is_record_id_selected(callback, manager):
            return
        
        await callback.answer()
        
        record_id = manager.dialog_data.get('record_id')
        
        data = {
            'price_sold' : None,
            'status' : RecordStatus.AVAILABLE.value,
            'sold_at' : None
        }
        
        u_record = await cls.flow.update_record(manager, record_id, **data)
        f_record = await cls.flow.format_record(manager, u_record.id)
        await cls.flow.finish_dialog_with_result(manager, f_record)