from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, and_
from typing import List, Optional

from app.core.db.repository.base import BaseRepository
from app.core.db.models import Game, Record
from app.core.db.statuses import RecordStatus

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
            Exception: При ошибке чтения
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
            logger.exception(f"Error checking if game '{game_name}' exists")
            raise
        
        
    async def search(self, query: str, limit: int = 50) -> List[Game]:
        """
        Поиск игр по названию.
        
        Использует регистронезависимый поиск с подстановочным знаком.
        Например, запрос "witch" найдёт "The Witcher 3".
        
        Args:
            query: Строка для поиска
            limit: Максимальное количество результатов (по умолчанию 50)
            
        Returns:
            Список найденных игр, отсортированных по названию
            
        Raises:
            Exception: При ошибке поиска
        """
        
        try:
            
            stmt = (
                select(Game)
                .where(Game.name.ilike(f"%{query}%"))
                .order_by(Game.name.desc())
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            games = result.scalars().all()
            
            logger.info(f"Game search: found {len(games)} games for query '{query}'")
            return games
            
        except Exception as e:
            logger.exception(f"Error game search: {e}")
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
        
        logger.debug(f"Search available games for query: {query}")
        
        try:
            stmt = (
                select(Game)
                .join(Record, Record.game_id == Game.id)
                .where(
                    and_(
                        Game.name.ilike(f"%{query}%"),
                        Record.status == RecordStatus.AVAILABLE.value
                    )
                )
                .distinct()
                .order_by(Game.name.desc())
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            games = result.scalars().all()
            
            logger.debug(f"Available games search: found {len(games)} games for query '{query}'")
            return games
        except Exception as e:
            logger.exception(f"Error getting available games for query '{query}': {e}")
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
        
        logger.debug(f"Search delivery to client games for query: {query}")
        
        try:
            stmt = (
                select(Game)
                .join(Record, Record.game_id == Game.id)
                .where(
                    and_(
                        Game.name.ilike(f"%{query}%"),
                        Record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value
                    )
                )
                .distinct()
                .order_by(Game.name.desc())
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            games = result.scalars().all()
            
            logger.debug(f"Delivery to client games search: found {len(games)} games for query '{query}'")
            return games
        except Exception as e:
            logger.exception(f"Error getting delivery to client games for query '{query}': {e}")
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
        
        logger.debug(f"Search delivery to me games for query: {query}")
        
        try:
            stmt = (
                select(Game)
                .join(Record, Record.game_id == Game.id)
                .where(
                    and_(
                        Game.name.ilike(f"%{query}%"),
                        Record.status == RecordStatus.IN_TRANSIT_TO_ME.value
                    )
                )
                .distinct()
                .order_by(Game.name.desc())
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            games = result.scalars().all()
            
            logger.debug(f"Delivery to me games search: found {len(games)} games for query '{query}'")
            return games
        except Exception as e:
            logger.exception(f"Error getting delivery to me games for query '{query}': {e}")
            raise
        
        
    async def get_by_name(self, game_name: str) -> Optional[Game]:
        """
        Поиск Game по точному названию игры
        
        Args:
            game_name: название игры
            
        Returns:
            Game или None
        
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug(f"Getting Game by game name: {game_name}")
        
        try:
            stmt = (
                select(Game)
                .where(Game.name == game_name)
            )
            
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        
        except Exception as e:
            logger.exception(f"Error getting Game by game name: {game_name}': {e}")
            raise
        
            