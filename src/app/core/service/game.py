from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db.repository import GameRepository
from app.core.db.models import Game
from app.core.service.base import BaseService

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
        
    async def search(self, query: str, limit: int = 50) -> list[Game]:
        """
        Поиск игр по названию.
        
        Использует регистронезависимый поиск с подстановочным знаком.
        Например, запрос "witch" найдёт "The Witcher 3".
        
        Args:
            query: Строка для поиска
            limit: Максимальное количество результатов (по умолчанию 50)
            
        Returns:
            Список Game, отсортированных по названию
            
        Raises:
            Exception: При ошибке получения
        """
        
        logger.info(f"Search games for query: {query}'")
        
        try:
            return await self.repo.search(query, limit)
        except Exception as e:
            logger.exception(f"Error search games for query {query}: {e}")
            raise
        
    
    async def search_available(self, query: str, limit: int = 50) -> List[Game]:
        """
        Поиск игр из наличия по названию игры
        
        Использует регистронезависимый поиск с подстановочным знаком.
        Например, запрос "witch" найдёт "The Witcher 3".
        
        Args:
            query: Строка для поиска
            limit: Максимальное количество результатов (по умолчанию 50)
            
        Returns:
            Список найденных игр, отсортированных по названию игры
            
        Raises:
            Exception: При ошибке поиска
        """
        
        logger.info(f"Search available games for query: {query}'")
                
        try:
            return await self.repo.search_available(query, limit)
        except Exception as e:
            logger.exception(f"Error search available games for query {query}: {e}")
            raise
        
    async def search_delivery_to_client(self, query: str, limit: int = 50) -> List[Game]:
        """
        Поиск игр по названию игры, которые едут к покупателю
        
        Использует регистронезависимый поиск с подстановочным знаком.
        Например, запрос "witch" найдёт "The Witcher 3".
        
        Args:
            query: Строка для поиска
            limit: Максимальное количество результатов (по умолчанию 50)
            
        Returns:
            Список найденных игр, отсортированных по названию игры
            
        Raises:
            Exception: При ошибке поиска
        """
        
        logger.info(f"Search delivery to client games for query: {query}'")
                        
        try:
            return await self.repo.search_delivery_to_client(query, limit)
        except Exception as e:
            logger.exception(f"Error delivery to client search games for query {query}: {e}")
            raise
    
    async def search_delivery_to_me(self, query: str, limit: int = 50) -> List[Game]:
        """
        Поиск игр по названию игры, которые едут ко мне
        
        Использует регистронезависимый поиск с подстановочным знаком.
        Например, запрос "witch" найдёт "The Witcher 3".
        
        Args:
            query: Строка для поиска
            limit: Максимальное количество результатов (по умолчанию 50)
            
        Returns:
            Список найденных игр, отсортированных по названию игры
            
        Raises:
            Exception: При ошибке поиска
        """
        
        logger.info(f"Search delivery to me games for query: {query}'")
                        
        try:
            return await self.repo.search_delivery_to_me(query, limit)
        except Exception as e:
            logger.exception(f"Error delivery to me search games for query {query}: {e}")
            raise
        
    async def get_by_name(self, game_name: str) -> Optional[Game]:
        """
        Поиск Game по точному названию игры
        
        Args:
            game_name: название игры
            
        Returns:
            Game или None
        
        Raises:
            Exception: При ошибке поиска
        """
        
        logger.info(f"Getting Game by game name: {game_name}")
        
        try:
            return await self.repo.get_by_name(game_name)
        except Exception as e:
            logger.exception(f"Error getting Game by game name: {game_name}: {e}")
            raise    
        
        