from typing import ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button

from app.interfaces.bot.dialogs.common.mapping import RecipientMapping
from app.core.db.statuses import RecordStatus
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import OrderArrivedSG
from .flow import OrderArrivedFlow

import logging

logger = logging.getLogger(__name__)

class OrderArrivedEventHandler(CommonEventHandler):
    """
    Обработчик для order-arrived
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: OrderArrivedFlow
        - States: OrderArrivedSG
    """
    flow: ClassVar[type[OrderArrivedFlow]] = OrderArrivedFlow
    states: ClassVar[type[OrderArrivedSG]] = OrderArrivedSG
    
    @classmethod
    async def on_recipient_type_selected(
        cls,
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ):
        """
        Обработчик выбора получателя
        
        Добавляет в dialog_data:
            тип получателя
            название типа получателя
        """
        
        await callback.answer()
                
        manager.dialog_data['recipient_type'] = item_id
        recipient_title = RecipientMapping.TITLES.get(item_id, 'Не найдено')
        manager.dialog_data['recipient_title'] = recipient_title
        
        await manager.switch_to(state=cls.states.game_input, show_mode=ShowMode.EDIT)
        
        
    @classmethod
    @handle_db_errors
    async def on_select_record_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обновление Record, если выбран record_id
        
        Обновляется статус
        Если:
            Выбран "к покупателю" → статус "sold"
            Выбран "ко мне" → статус "available"
        
        sold_at и price_sold не заполняются, так как были заполнены на этапе продажи,
        а не на этапе получения посылки заказчиком
        
        Выводится отформатированный Record
        """
        
        if not await cls.flow.is_record_id_selected(callback, manager):
            return
        
        await callback.answer()
        
        record_id = manager.dialog_data.get('record_id')
        recipient_type = manager.dialog_data.get('recipient_type')
        status = (
            RecordStatus.SOLD.value
            if recipient_type == RecipientMapping.TO_CLIENT
            else RecordStatus.AVAILABLE.value
        )
        
        data = {
            'status' : status
        }
        
        u_record = await cls.flow.update_record(manager, record_id, **data)
        f_record = await cls.flow.format_record(manager, u_record.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_record)