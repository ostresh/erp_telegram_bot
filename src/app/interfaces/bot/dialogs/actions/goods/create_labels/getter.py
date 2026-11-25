from typing import List

from aiogram_dialog import DialogManager

from app.core.dto.labels import DeliveryType
from app.interfaces.bot.dialogs.common import CommonGetter


class CreateLabelsGetter(CommonGetter):
    
    @staticmethod
    async def get_delivery_type(dialog_manager: DialogManager, **kwargs) -> dict[str, List[dict]]:
        """
        Получение типов доставки
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
        
        
        