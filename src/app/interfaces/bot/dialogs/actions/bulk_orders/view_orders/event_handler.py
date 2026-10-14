from typing import Any, ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import ViewOrdersSG
from .flow import ViewOrdersFlow

class ViewOrdersEventHandler(CommonEventHandler):
    """
    Обработчик для view_orders
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ViewOrdersFlow
        - States: ViewOrdersSG
    """
    flow: ClassVar[type[ViewOrdersFlow]] = ViewOrdersFlow
    states: ClassVar[type[ViewOrdersSG]] = ViewOrdersSG
    
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
        
        manager.show_mode = ShowMode.DELETE_AND_SEND
        
        bulk_order_id = manager.dialog_data.get('bulk_order_id')
        f_bulk_order = manager.dialog_data.get('f_bulk_order')
            
        records = await cls.flow.get_records_by_bulk_order_id(manager, bulk_order_id)
        f_records = await cls.flow.format_many_records(manager, [record.id for record in records])

        await cls.flow.finish_dialog_with_many_result(manager, f_records + [f_bulk_order])
        
    @classmethod
    @handle_db_errors
    async def on_start(cls, start_data: Any, manager: DialogManager):
        """
        Обработчик старта диалога
        Проверяет, если один элемент в bulk_order, то сразу записывает его в dialog_data
        """
        
        bulk_orders = await cls.flow.get_bulk_orders(manager)
        
        if len(bulk_orders) == 1:
            manager.dialog_data['bulk_order_id'] = bulk_orders[0].id
            f_bulk_order = await cls.flow.format_bulk_order(manager, bulk_orders[0].id)
            manager.dialog_data['f_bulk_order'] = f_bulk_order
        
    
        
        
        
        
        