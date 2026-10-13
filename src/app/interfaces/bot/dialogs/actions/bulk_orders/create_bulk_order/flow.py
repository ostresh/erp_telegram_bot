from aiogram_dialog import DialogManager

from app.core.db.models import BulkOrder
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.bulk_order import BulkOrderService
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class CreateBulkOrderFlow(CommonFlow):
    
    @staticmethod
    async def create_bulk_order_from_json(manager: DialogManager, json_: str) -> BulkOrder:
        """
        Создание нового BulkOrder из JSON
        
        Args:
            json_ (str): JSON строка
        
        Returns:
            созданный BulkOrder
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
                
        async with uow() as session:
            service = BulkOrderService(session)
            new_bulk_order = await service.create_from_json(json_)
            
        return new_bulk_order
    
    
        
        
        
        