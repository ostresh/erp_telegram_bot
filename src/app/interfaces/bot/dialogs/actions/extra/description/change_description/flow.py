from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.service.description import DescriptionService
from app.interfaces.bot.dialogs.common import CommonFlow


class ChangeDescriptionFlow(CommonFlow):
    
    @classmethod
    async def get_description(cls, manager: DialogManager) -> str:
        """
        Получение описания объявления
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = DescriptionService(session)
            desc = await service.get_by_id(item_id=1)
           
        return desc.title
    
    @classmethod
    async def update_description(cls, manager: DialogManager, new_desc: str) -> str:
        """
        Обновление описания
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = DescriptionService(session)
            desc = await service.update(item_id=1, title=new_desc)
            
        return desc.title