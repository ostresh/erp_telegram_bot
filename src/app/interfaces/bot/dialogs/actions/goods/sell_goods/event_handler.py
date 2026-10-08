from datetime import datetime, timezone
from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import TextInput

from app.core.db.statuses import RecordStatus
from app.interfaces.bot.dialogs.common.mapping import DeliveryMapping
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import SellGoodsSG
from .flow import SellGoodsFlow

import logging

logger = logging.getLogger(__name__)

class SellGoodsEventHandler(CommonEventHandler):
    """
    Обработчик для sell-goods
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: SellGoodsFlow
        - States: SellGoodsSG
    """
    flow: ClassVar[type[SellGoodsFlow]] = SellGoodsFlow
    states: ClassVar[type[SellGoodsSG]] = SellGoodsSG
    
    
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
        await manager.switch_to(cls.states.receive_method, show_mode=ShowMode.EDIT)

        
        
    @classmethod
    @handle_db_errors
    async def on_price_sold_typed(
        cls,
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: int,
    ) -> None:
        """
        Обработчик ввода цены продажи
        
        После ввода обновляется объект Record
        
        Объект форматируется и сразу выводится
        
        Перенаправляется в главное меню
        """
        
        manager.show_mode = ShowMode.EDIT
        
        receive_type = manager.dialog_data.get('receive_type')
        price_sold = text
        record_id = manager.dialog_data.get('record_id')
        status = (
            RecordStatus.SOLD.value 
            if receive_type == DeliveryMapping.LOCAL
            else RecordStatus.IN_TRANSIT_TO_CLIENT.value
        )
        
        data = {
            'price_sold' : price_sold,
            'status' : status,
            'sold_at': datetime.now(timezone.utc)
        }
        
        u_record = await cls.flow.update_record(manager, record_id, **data)
        f_record = await cls.flow.format_record(manager, u_record.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_record)