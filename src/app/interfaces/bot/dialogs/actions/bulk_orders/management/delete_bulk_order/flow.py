from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import BulkOrder
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.bulk_order import BulkOrderService
from app.interfaces.bot.dialogs.common import CommonFlow


class DeleteBulkOrderFlow(CommonFlow):
    
    @staticmethod
    async def get_bulk_orders(manager: DialogManager) -> List[BulkOrder]:
        """
        Получение оптовых заказов
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = BulkOrderService(session)
            bulk_orders = await service.get_all(reverse=True)
            
        return bulk_orders
    
    @staticmethod
    async def delete_bulk_order(manager: DialogManager, bulk_order_id: int) -> bool:
        """
        Удаление оптового заказа
        Вместе с этим удаляются и связанные Records
        
        Args:
            bulk_order_id (int): id оптового заказа
            
        Returns:
            bool удален ли заказ
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
            
        async with uow() as session:
            service = BulkOrderService(session)
            is_deleted = await service.delete(bulk_order_id)
        
        return is_deleted
        
        

        
        
        
        