from typing import Any, ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import AddDeliveryToBulkOrderSG
from .flow import AddDeliveryToBulkOrderFlow

import logging

logger = logging.getLogger(__name__)

class AddDeliveryToBulkOrderEventHandler(CommonEventHandler):
    """
    Обработчик для add_delivery_to_bulk_order
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: AddDeliveryToBulkOrderFlow
        - States: AddDeliveryToBulkOrderSG
    """
    flow: ClassVar[type[AddDeliveryToBulkOrderFlow]] = AddDeliveryToBulkOrderFlow
    states: ClassVar[type[AddDeliveryToBulkOrderSG]] = AddDeliveryToBulkOrderSG
    
    @classmethod
    @handle_db_errors
    async def on_bulk_order_id_selected(
        cls,
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: int,
    ):
        """Выбор ID оптового заказа — обновляет сообщение с форматированной строкой оптового заказа."""
        await callback.answer()

        f_bulk_order = await cls.flow.format_bulk_order(manager, item_id)
        manager.dialog_data['bulk_order_id'] = item_id
        manager.dialog_data['f_bulk_order'] = f_bulk_order.strip()
        await manager.update(show_mode=ShowMode.EDIT)

    @classmethod
    @handle_db_errors
    async def on_select_bulk_order_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Кнопка "Далее" после выбора записи.

        Должна быть переопределена в каждом диалоговом обработчике.
        """
        
        if not await cls.flow.is_bulk_order_id_selected(callback, manager):
            return
        
        await callback.answer()
        await manager.switch_to(cls.states.input_delivery_price)
        
    @classmethod
    @handle_db_errors
    async def on_delivery_price_typed(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: int
    ):
        """
        Обработчик ввода цены доставки
        """
        
        price = text
        bulk_order_id = manager.dialog_data.get('bulk_order_id')
        
        u_bulk_order = await cls.flow.apply_delivery_cost(manager, bulk_order_id, price)
        f_bulk_order = await cls.flow.format_bulk_order(manager, u_bulk_order.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_bulk_order)
        
    @classmethod
    @handle_db_errors
    async def on_start(cls, start_data: Any, manager: DialogManager):
        """
        Обработчик старта диалога
        Проверяет, если один элемент в bulk_order, то сразу записывает его в dialog_data
        """
        
        bulk_orders = await cls.flow.get_created_bulk_orders(manager)
        
        if len(bulk_orders) == 1:
            manager.dialog_data['bulk_order_id'] = bulk_orders[0].id
            f_bulk_order = await cls.flow.format_bulk_order(manager, bulk_orders[0].id)
            manager.dialog_data['f_bulk_order'] = f_bulk_order
        
    
        
        
        
        
        