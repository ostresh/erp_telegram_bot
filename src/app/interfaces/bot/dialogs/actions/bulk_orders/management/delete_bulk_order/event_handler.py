from typing import Any, ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .states import DeleteBulkOrderSG
from .flow import DeleteBulkOrderFlow

class DeleteBulkOrderEventHandler(CommonEventHandler):
    """
    Обработчик для delete_bulk_order
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: DeleteBulkOrderFlow
        - States: DeleteBulkOrderSG
    """
    flow: ClassVar[type[DeleteBulkOrderFlow]] = DeleteBulkOrderFlow
    states: ClassVar[type[DeleteBulkOrderSG]] = DeleteBulkOrderSG
    
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
        
        manager.show_mode = ShowMode.EDIT
        
        bulk_order_id = manager.dialog_data.get('bulk_order_id')
        
        is_deleted = await cls.flow.delete_bulk_order(manager, bulk_order_id)
        
        if is_deleted:
            await cls.flow.finish_dialog_with_result(
                manager,
                text=f'{Emoji.STATUS} Успешное удаление {Emoji.ID} {bulk_order_id} оптового заказа'
            )
        else:
            await cls.flow.finish_dialog_with_result(
                manager,
                text=f'{Emoji.ERROR} Произошла ошибка'
            )
            
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
        
        
    
        
        
        
        
        