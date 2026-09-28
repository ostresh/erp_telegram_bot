from typing import Any

from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.core.db.unit_of_work import UnitOfWork
from app.core.service import GameService, RecordService
from app.interfaces.bot.dialogs.common import CommonFlow

class BuyGoodsFlow(CommonFlow):
    
    @classmethod
    async def get_records(cls, manager: DialogManager):
        """
        Переопределение стандартного метода
        """
        return []
    
    @staticmethod
    async def create_record_from_game_name(manager: DialogManager, game_name: str, **data: Any) -> Record:
        """
        Создает Record
        
        Args:
            manager: DialogManager,
            game_name: название игры
            data: словарь с данными для создания
            
        Returns:
            созданный Record
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
                
        async with uow() as session:
            game_service = GameService(session)
            record_service = RecordService(session)
            
            price_selling = await record_service.get_price_selling_for_game_in_available(game_name=game_name)
            game = await game_service.get_by_name(game_name=game_name)
                     
            record = Record(
                game_id=game.id,
                price_selling=price_selling,
                **data
            )
            
            new_record = await record_service.create(record)

        return new_record
        