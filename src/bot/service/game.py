from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import GameRepository
from bot.db.models import Game
from bot.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class GameService(BaseService[Game, GameRepository]):
    """Сервис для работы с Game"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, GameRepository(session))
        
    async def is_game_exists(self, game_name: str) -> bool:
        """
        Проверка, есть ли игра в списке
        
        Args:
            game_name - название игры
        
        Return:
            bool есть ли игра
        
        Raises:
            Exception: При ошибке создания
        """

        logger.info(f"Checking is game exists '{game_name}'")

        try:
            return await self.repo.is_game_exists(game_name)
        except Exception as e:
            logger.exception(f"Error checking game is exists: {e}")
            raise