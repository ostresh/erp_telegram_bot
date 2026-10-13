from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import BulkOrder
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.bulk_order import BulkOrderService
from app.interfaces.bot.dialogs.common import CommonFlow


class AddDeliveryToBulkOrderFlow(CommonFlow):
    
    @classmethod
    async def get_created_bulk_orders(cls, manager: DialogManager) -> List[BulkOrder]:
        """
        Получение созданных оптовых заказов
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = BulkOrderService(session)
            bulk_orders = await service.get_created()
           
        return bulk_orders
        
    @staticmethod
    async def apply_delivery_cost(
        manager: DialogManager,
        bulk_order_id: int,
        delivery_cost: int,
    ) -> BulkOrder:
        """
        Проставляет стоимость доставки и распределяет её между записями
        оптового заказа в одной транзакции.

        Args:
            manager: DialogManager
            bulk_order_id (int): id оптового заказа
            delivery_cost (int): стоимость доставки

        Returns:
            BulkOrder: обновлённый оптовый заказ

        Raises:
            ValueError: если у оптового заказа нет записей
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = BulkOrderService(session)
            u_bulk_order = await service.add_delivery_cost(bulk_order_id, delivery_cost)
        
        return u_bulk_order

        
        
        
        