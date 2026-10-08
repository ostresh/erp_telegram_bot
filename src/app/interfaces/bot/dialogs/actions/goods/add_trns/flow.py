from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Utility
from app.core.service import UtilityService
from app.core.db.unit_of_work import UnitOfWork
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class AddTrnsFlow(CommonFlow):
    
    @staticmethod
    async def get_utils(manager: DialogManager) -> List[Utility]:
        """
        Получение всех транзакций
        
        Returns:
            Список транзакций
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = UtilityService(session)
            utils = await service.get_all()
            
        return utils
    
    @staticmethod
    async def get_util_by_id(manager: DialogManager, util_id: int) -> Utility:
        """
        Получение Utility по id
        
        Returns:
            Utility
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
                
        async with uow() as session:
            service = UtilityService(session)
            util = await service.get_by_id(util_id)
            
        return util
        
        