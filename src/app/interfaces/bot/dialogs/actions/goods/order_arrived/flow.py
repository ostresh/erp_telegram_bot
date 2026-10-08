from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.core.service import RecordService
from app.core.db.unit_of_work import UnitOfWork
from app.interfaces.bot.dialogs.common.mapping import RecipientMapping
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class OrderArrivedFlow(CommonFlow):
    
    @classmethod
    async def get_records(cls, manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры и определенного получателя
        """
        game_name = manager.dialog_data.get('game_name')
        recipient_type = manager.dialog_data.get('recipient_type')
        return await cls.get_records_by_recipient_and_game(manager, recipient_type, game_name)
    
    @staticmethod
    async def get_records_by_recipient_and_game(manager: DialogManager, recipient_type: str, game_name: str) -> List[Record]:
        """
        Получение записей
        
        Args:
            manager: DialogManager
            recipient_type: тип получателя
            game_name: название игры
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            
            getter = (
                record_service.get_in_transit_to_client_by_game
                if recipient_type == RecipientMapping.TO_CLIENT
                else record_service.get_in_transit_to_me_by_game
            )
            records = await getter(game_name)
            
        return records