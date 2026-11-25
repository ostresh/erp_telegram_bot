from typing import List

from aiogram_dialog import DialogManager

from app.core.dto.labels import DeliveryType
from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import CreateLabelsFlow as Flow


class CreateLabelsGetter(CommonGetter):
    
    @staticmethod
    async def get_delivery_type(dialog_manager: DialogManager, **kwargs) -> dict[str, List[dict]]:
        """
        Получение всех Utility
        
        Удаляется [UTIL] в названии
        """
        
        deliveries = [
            {
                "id" : item.value,
                "name" : item.display_name
            }
            for item in DeliveryType
        ]
        
        return {
            'deliveries' : deliveries
        }
        
        
        