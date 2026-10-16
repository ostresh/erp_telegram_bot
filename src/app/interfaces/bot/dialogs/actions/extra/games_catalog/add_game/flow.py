from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Game
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.game import GameService
from app.interfaces.bot.dialogs.common import CommonFlow

class AddGameFlow(CommonFlow):
    
    @classmethod
    async def create_games(cls, manager: DialogManager, games: list[str]) -> List[str]:
        """
        Создает Game в games_list
        
        Args:
            games (list[str]): список названий игр
        
        Returns:
            Список Game.name
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = GameService(session)
            new_games = await service.create_many([Game(name=game) for game in games])
            
        return [game.name for game in new_games]
    
    @staticmethod
    async def is_game_already_exists(manager: DialogManager, game_name: str) -> bool:
        """
        Проверка, существует ли игра в списке.

        Если не существует:
            записывает ошибку в dialog_data['game_error'],
            чтобы окно показало её пользователю.

        Побочный эффект:
            При неудаче устанавливает manager.dialog_data['game_error']

        Args:
            manager: DialogManager
            game_name: название игры

        Returns:
            bool: существует ли игра
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            game_service = GameService(session)
            is_exists = await game_service.is_game_exists_without_prefix(game_name)

        if not is_exists:
            return False

        return True
            
        
        