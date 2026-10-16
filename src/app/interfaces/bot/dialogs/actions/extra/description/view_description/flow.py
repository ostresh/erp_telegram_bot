from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.service.description import DescriptionService
from app.interfaces.bot.dialogs.common import CommonFlow


class ViewDescriptionFlow(CommonFlow):
    
    @classmethod
    async def get_description(cls, manager: DialogManager) -> str:
        """
        Получение описания
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = DescriptionService(session)
            desc = await service.get_by_id(item_id=1)
           
        return desc.title