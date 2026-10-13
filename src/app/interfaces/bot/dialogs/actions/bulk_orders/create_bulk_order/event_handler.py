from typing import ClassVar

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import CreateBulkOrderSG
from .flow import CreateBulkOrderFlow

import logging

logger = logging.getLogger(__name__)

class CreateBulkOrderEventHandler(CommonEventHandler):
    """
    Обработчик для create_bulk_order
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: CreateBulkOrderFlow
        - States: CreateBulkOrderSG
    """
    flow: ClassVar[type[CreateBulkOrderFlow]] = CreateBulkOrderFlow
    states: ClassVar[type[CreateBulkOrderSG]] = CreateBulkOrderSG
    
    @classmethod
    @handle_db_errors
    async def on_input_json(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: str
    ):
        """
        Обработчик создания BulkOrder из JSON
        """
        
        manager.show_mode = ShowMode.EDIT
        
        json_ = text.strip()
        
        n_bulk_order = await cls.flow.create_bulk_order_from_json(manager, json_)
        f_bulk_order = await cls.flow.format_bulk_order(manager, n_bulk_order.id)
        
        records = await cls.flow.get_records_by_bulk_order_id(manager, n_bulk_order.id)
        f_records = await cls.flow.format_many_records(manager, [record.id for record in records])
        
        await cls.flow.finish_dialog_with_many_result(manager, f_records + [f_bulk_order])
        
    
        
        
        
        
        