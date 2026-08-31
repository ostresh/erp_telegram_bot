from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from bot.db.models import Game
from bot.db.repository.base import BaseRepository

import logging

logger = logging.getLogger(__name__)

class GameRepository(BaseRepository[Game]):
    """Репозиторий для Game. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Game)
        
        
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
        
        logger.debug(f"Checking if game '{game_name}' exists")
        
        try:
            stmt = select(
                exists(
                    select(Game.name)
                    .where(Game.name == game_name)
                )
            )
            result = await self.session.execute(stmt)
            exists_result = result.scalar()
            
            logger.debug(f"Game '{game_name}' exists: {exists_result}")
            return exists_result
        except Exception:
            logger.debug(f"Error checking if game '{game_name}' exists")
            raise