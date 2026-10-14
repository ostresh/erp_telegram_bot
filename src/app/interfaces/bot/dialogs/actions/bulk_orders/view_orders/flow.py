from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import BulkOrder
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.bulk_order import BulkOrderService
from app.interfaces.bot.dialogs.common import CommonFlow


class ViewOrdersFlow(CommonFlow):
    
    @classmethod
    async def get_bulk_orders(cls, manager: DialogManager) -> List[BulkOrder]:
        """
        Получение оптовых заказов
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = BulkOrderService(session)
            if manager.start_data.get('handler_action') == 'bulk_order_by_id':
                bulk_orders = await service.get_created()
                bulk_orders += await service.get_in_transit()
                bulk_orders = sorted(bulk_orders, key=lambda item: item.id)
            
            elif manager.start_data.get('handler_action') == 'all_bulk_orders':
                bulk_orders = await service.get_all(reverse=True)
            
            else: 
                bulk_orders = []
           
        return bulk_orders
        

        
        
        
        