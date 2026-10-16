from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db.repository import GameRepository
from app.core.db.models import Game
from app.core.db.statuses.record import RecordStatus
from app.core.dto import AvailableGameDTO
from app.core.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class GameService(BaseService[Game, GameRepository]):
    """Сервис для работы с Game"""

    # Инициализация

    def __init__(self, session: AsyncSession):
        super().__init__(session, GameRepository(session))

    # Проверки

    async def is_game_exists(self, game_name: str) -> bool:
        """Проверяет, существует ли игра с указанным названием.

        Args:
            game_name (str): название игры.

        Returns:
            bool: True, если игра существует.
        """
        try:
            return await self.repo.is_game_exists(game_name)
        except Exception:
            logger.exception("Error checking game exists")
            raise

    async def is_game_exists_without_prefix(self, name: str) -> bool:
        """Проверяет существование игры в БД без учёта платформенного префикса.

        Формирует список вариантов имени: чистое имя + имя с каждым известным
        платформенным префиксом из PlatformMapping.PLATFORM_WITH_PREFIXES,
        затем проверяет точное совпадение по ним.

        Args:
            name (str): название игры без префикса.

        Returns:
            bool: True, если найдена игра с одним из вариантов имени.
        """
        try:
            from app.interfaces.bot.dialogs.common.mapping import PlatformMapping

            clean_name = name.strip()

            variants = [clean_name] + [
                f"{prefix} {clean_name}"
                for prefixes in PlatformMapping.PLATFORM_WITH_PREFIXES.values()
                for prefix in prefixes
            ]

            return await self.repo.exists_by_exact_names(variants)
        except Exception:
            logger.exception("Error checking game exists without prefix")
            raise

    # Поиск

    async def search(self, query: str, limit: int = 50) -> List[Game]:
        """Ищет игры по названию без учёта регистра.

        Args:
            query (str): строка для поиска.
            limit (int): максимальное количество результатов.

        Returns:
            List[Game]: найденные игры, отсортированные по названию.
        """
        try:
            return await self.repo.search_by_status(query=query, limit=limit)
        except Exception:
            logger.exception("Error searching games")
            raise

    async def search_available(self, query: str, limit: int = 50) -> List[Game]:
        """Ищет игры из наличия по названию без учёта регистра.

        Args:
            query (str): строка для поиска.
            limit (int): максимальное количество результатов.

        Returns:
            List[Game]: найденные игры, отсортированные по названию.
        """
        try:
            return await self.repo.search_by_status(
                query=query, 
                status=RecordStatus.AVAILABLE, 
                limit=limit
            )
        except Exception:
            logger.exception("Error searching available games")
            raise

    async def search_in_transit_to_client(self, query: str, limit: int = 50) -> List[Game]:
        """Ищет игры, которые едут к покупателю, по названию без учёта регистра.

        Args:
            query (str): строка для поиска.
            limit (int): максимальное количество результатов.

        Returns:
            List[Game]: найденные игры, отсортированные по названию.
        """
        try:
            return await self.repo.search_by_status(
                query=query, 
                status=RecordStatus.IN_TRANSIT_TO_CLIENT, 
                limit=limit
            )
        except Exception:
            logger.exception("Error searching in transit to client games")
            raise

    async def search_in_transit_to_me(self, query: str, limit: int = 50) -> List[Game]:
        """Ищет игры, которые едут ко мне, по названию без учёта регистра.

        Args:
            query (str): строка для поиска.
            limit (int): максимальное количество результатов.

        Returns:
            List[Game]: найденные игры, отсортированные по названию.
        """
        try:
            return await self.repo.search_by_status(
                query=query, 
                status=RecordStatus.IN_TRANSIT_TO_ME, 
                limit=limit
            )
        except Exception:
            logger.exception("Error searching in transit to me games")
            raise

    # Получение по имени

    async def get_by_name(self, game_name: str) -> Optional[Game]:
        """Получает игру по точному названию.

        Args:
            game_name (str): название игры.

        Returns:
            Optional[Game]: найденная игра или None.
        """
        try:
            return await self.repo.get_by_name(game_name)
        except Exception:
            logger.exception("Error getting game by name")
            raise

    async def get_by_names(self, game_names: list[str]) -> List[Game]:
        """Получает игры по списку точных названий.

        Args:
            game_names (list[str]): список названий игр.

        Returns:
            List[Game]: найденные игры.
        """
        try:
            return await self.repo.get_by_names(game_names)
        except Exception:
            logger.exception("Error getting games by names")
            raise

    async def get_by_ids(self, ids: List[int]) -> List[Game]:
        """Получает игры по списку id.

        Args:
            ids (List[int]): список id игр.

        Returns:
            List[Game]: найденные игры, отсортированные по названию.
            Игр, которых нет в БД, в списке не будет.
        """
        try:
            return await self.repo.get_by_ids(ids)
        except Exception:
            logger.exception("Error getting games by ids")
            raise

    # Получение списка

    async def get_available(self) -> List[AvailableGameDTO]:
        """Получает игры из наличия с агрегированными ценами и количеством.

        Returns:
            List[AvailableGameDTO]: список игр из наличия вместе с
            price_purchase, price_selling, games_count.
        """
        try:
            return await self.repo.get_available()
        except Exception:
            logger.exception("Error getting available games")
            raise
