from typing import List

from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import AddTrnsFlow as Flow


class AddTrnsGetter(CommonGetter):
    
    @staticmethod
    async def get_utils(dialog_manager: DialogManager, **kwargs) -> dict[str, List[dict]]:
        """
        Получение всех Utility
        
        Удаляется [UTIL] в названии
        """
        
        utils = await Flow.get_utils(dialog_manager)
        
        utils = sorted(
            [{'id' : util.id, 'title' : util.title.split('] ')[1]} for util in utils],
            key=lambda x: x.get('title')
        )
        
        return {
            'utils' : utils
        }
        
        
        