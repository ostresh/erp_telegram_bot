

from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Game
from app.core.db.unit_of_work import UnitOfWork
from app.core.dto.game import AvailableGameDTO
from app.core.service import GameService
from app.interfaces.bot.utils.formatter import MessageFormatter


class GameOperationsMixin:
    """CRUD и форматирование записей Record."""

    @staticmethod
    async def get_game_from_game_name(manager: DialogManager, game_name) -> Game:
        """
        Получение Game из названия игры
        
        Args:
            game_name: название игры
            
        Returns:
            Объект Game
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = GameService(session)
            game = await service.get_by_name(game_name)
            
        return game
    
    @staticmethod
    async def format_many_games(manager: DialogManager, games: List[AvailableGameDTO], chunk_size: int = 7):
        """
        Получает Record по id и форматирует его.

        Загружает запись вместе со связанными объектами
        (игра, транзакция, оптовый заказ) и форматирует в HTML
        для отправки в Telegram.

        Args:
            manager: DialogManager
            record_id: id записи

        Returns:
            str: отформатированная строка записи в HTML
        """

        return MessageFormatter.format_many_available_games(games, chunk_size)
        