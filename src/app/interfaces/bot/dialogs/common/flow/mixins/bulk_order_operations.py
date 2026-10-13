

from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import BulkOrder
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.bulk_order import BulkOrderService
from app.interfaces.bot.utils.formatter import MessageFormatter


class BulkOrderOperationsMixin:
    
    @staticmethod
    async def format_bulk_order(manager: DialogManager, bulk_order: int) -> str:
        """
        Получает BulkOrder по id и  и форматирует в HTML для отправки в Telegram.

        Args:
            manager: DialogManager
            bulk_order: id оптового заказа

        Returns:
            str: отформатированная строка оптового заказа в HTML
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = BulkOrderService(session)
            bulk_order = await service.get_by_id(bulk_order)

        return MessageFormatter.format_bulk_order(bulk_order)

    @staticmethod
    async def format_many_bulk_orders(manager: DialogManager, bulk_orders_ids: List[int], chunk_size: int = 7) -> List[str]:
        """
        Получает несколько BulkOrder по id и  форматирует в HTML для отправки в Telegram.
        
        Args:
            manager: DialogManager
            bulk_order_ids (List[int]): id оптовых заказов 

        Returns:
            List[str]: список отформатированных строк оптового заказа в HTML
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = BulkOrderService(session)
            bulk_orders = await service.get_many_by_ids(bulk_orders_ids)

        return MessageFormatter.format_many_bulk_orders(bulk_orders, chunk_size)
    
    @staticmethod
    async def update_bulk_order(
        manager: DialogManager,
        bulk_order_id: int,
        **data,
    ) -> BulkOrder:
        """
        Обновляет один BulkOrder.

        Args:
            manager: DialogManager
            bulk_order_id: id записи
            data: словарь с полями для обновления (например, {'status': 'sold'})

        Returns:
            BulkOrder: обновлённый объект записи
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = BulkOrderService(session)
            u_bulk_order = await service.update(bulk_order_id, **data)

        return u_bulk_order
    
    @staticmethod
    async def update_many_bulk_orders(
        manager: DialogManager,
        bulk_order_ids: List[int],
        **data,
    ) -> List[BulkOrder]:
        """
        Обновляет несколько BulkOrder одинаковыми данными.

        Используется, когда нужно применить одно изменение
        к группе записей (например, при обмене дисков).

        Все записи обновляются в рамках одной сессии.

        Args:
            manager: DialogManager
            bulk_order_ids: список id записей для обновления
            data: словарь с одинаковыми для всех записей полями

        Returns:
            List[BulkOrder]: список обновлённых объектов записей
        """
        uow: UnitOfWork = manager.middleware_data["uow"]
        u_bulk_orders = []

        async with uow() as session:
            service = BulkOrderService(session)
            for bulk_order_id in bulk_order_ids:
                u_bulk_order = await service.update(bulk_order_id, **data)
                u_bulk_orders.append(u_bulk_order)

        return u_bulk_orders
