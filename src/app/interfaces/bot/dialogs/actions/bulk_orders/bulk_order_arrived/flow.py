from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import BulkOrder
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.bulk_order import BulkOrderService
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class BulkOrderArrivedFlow(CommonFlow):
    
    @classmethod
    async def get_in_transit_bulk_orders(cls, manager: DialogManager) -> List[BulkOrder]:
        """
        Получение оптовых заказов, которые едут ко мне
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = BulkOrderService(session)
            bulk_orders = await service.get_in_transit()
            
        return bulk_orders
    
    @staticmethod
    async def complete_arrival(manager: DialogManager, bulk_order_id: int) -> BulkOrder:
        """
        Завершает прибытие оптового заказа в одной транзакции:
        обновляет статус заказа и переводит связанные записи в наличие.

        Args:
            manager: DialogManager
            bulk_order_id (int): id оптового заказа

        Returns:
            BulkOrder: обновлённый оптовый заказ
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = BulkOrderService(session)
            u_bulk_order = await service.complete_arrival(bulk_order_id)
        
        return u_bulk_order

        
        
        
        
        
        