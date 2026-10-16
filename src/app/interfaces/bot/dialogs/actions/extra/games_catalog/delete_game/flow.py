from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Game
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.game import GameService
from app.interfaces.bot.dialogs.common import CommonFlow

class DeleteGameFlow(CommonFlow):
    
    @classmethod
    async def get_games(cls, manager: DialogManager, game_names: List[str]) -> List[Game]:
        """
        Получение объектов Game из списка названий игр
        
        Args:
            game_names (list[str]): список названий игр
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = GameService(session)
            games = await service.get_by_names(game_names)
        
        return games
                
    @classmethod
    async def delete_games(cls, manager: DialogManager, game_ids: List[int]) -> bool:
        """
        Удаление Games
        
        Args:
            game_ids (List[int]): список id игр
        """
        
        if not game_ids:
            return False
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = GameService(session)
            is_deleted = [await service.delete(game_id) for game_id in game_ids]
        
        return all(is_deleted)

        
        
        
        