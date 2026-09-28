from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.core.service import RecordService
from app.core.db.unit_of_work import UnitOfWork
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class SellGoodsFlow(CommonFlow):
    
    @classmethod
    async def get_records(cls, manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры
        """
        game_name = manager.dialog_data.get('game_name')
        return await cls.get_available_records_by_game(manager, game_name)
        
    
    @staticmethod
    async def get_available_records_by_game(manager: DialogManager, game_name: str) -> List[Record]:
        """
        Получение записей, которые в наличии, по игре
        
        Args:
            manager: DialogManager
            game_name: название игры
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            records = await record_service.get_available_by_game(game_name)
            
        return records