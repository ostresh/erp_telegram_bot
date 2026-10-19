from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, exists, and_
from typing import List, Optional, Sequence

from app.core.db.repository.base import BaseRepository
from app.core.db.models import Game, Record
from app.core.db.statuses import RecordStatus
from app.core.dto import AvailableGameDTO

import logging

logger = logging.getLogger(__name__)

class GameRepository(BaseRepository[Game]):
    """Репозиторий для Game. Наследует базовые CRUD, добавляет специфичные методы"""

    # Инициализация

    def __init__(self, session: AsyncSession):
        super().__init__(session, Game)

    # Проверки существования

    async def is_game_exists(self, game_name: str) -> bool:
        """Проверяет, существует ли игра с указанным названием.

        Args:
            game_name (str): название игры.

        Returns:
            bool: True, если игра существует.
        """
        logger.debug(f"Checking if game '{game_name}' exists")

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

    async def exists_by_exact_names(
        self,
        names: Sequence[str],
    ) -> bool:
        """Проверяет существование игры по точному совпадению с одним из переданных имён.

        Args:
            names (Sequence[str]): список вариантов имени для проверки.

        Returns:
            bool: True, если найдена хотя бы одна игра.
        """
        logger.debug(f"Checking game existence by exact names: {names}")

        stmt = (
            select(Game.id)
            .where(
                (Game.name).in_(names)
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)
        found = result.scalar_one_or_none() is not None

        logger.debug(f"Game found by exact names: {found}")
        return found

    # Поиск

    async def search_by_status(
        self, 
        query: str, 
        status: Optional[RecordStatus] = None, 
        limit: int = 50
    ) -> List[Game]:
        """Ищет игры по названию с фильтрацией по статусу записей.

        Использует регистронезависимый поиск с подстановочным знаком.
        Например, запрос "witch" найдёт "The Witcher 3".

        Args:
            query (str): строка для поиска в названии игры.
            status (RecordStatus): статус записей для фильтрации.
            limit (int): максимальное количество результатов.

        Returns:
            List[Game]: список найденных игр, отсортированных по названию.
        """
        logger.debug(f"Search games by status '{status.value if status else 'no status'}' for query: {query}")
        
        stmt = (
            select(Game)
            .where(Game.name.ilike(f"%{query}%"))
            .distinct()
            .order_by(Game.name.desc())
            .limit(limit)
        )
        
        if status:
            stmt = stmt.join(Record, Record.game_id == Game.id).where(Record.status == status.value)
        
        result = await self.session.execute(stmt)
        games = result.scalars().all()
        
        logger.debug(f"Found {len(games)} games for query '{query}' with status '{status.value if status else 'no status'}'")
        return games
    
    # Получение по имени

    async def get_by_name(self, game_name: str) -> Optional[Game]:
        """Получает игру по точному названию.

        Args:
            game_name (str): название игры.

        Returns:
            Optional[Game]: найденная игра или None.
        """
        logger.debug(f"Getting Game by game name: {game_name}")

        stmt = (
            select(Game)
            .where(Game.name == game_name)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_names(self, game_names: list[str]) -> List[Game]:
        """Получает игры по списку точных названий.

        Args:
            game_names (list[str]): список названий игр.

        Returns:
            List[Game]: найденные игры.
        """
        logger.debug(f"Getting Game by game names: {game_names}")

        stmt = (
            select(Game)
            .where(Game.name.in_(game_names))
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_ids(self, ids: List[int]) -> List[Game]:
        """Получает игры по списку id.

        Args:
            ids (List[int]): список id игр.

        Returns:
            List[Game]: найденные игры, отсортированные по названию.
            Игр, которых нет в БД, в списке не будет.
        """
        logger.debug(f"Getting games by ids: {ids}")

        if not ids:
            return []

        stmt = (
            select(Game)
            .where(Game.id.in_(ids))
            .order_by(Game.name)
        )

        result = await self.session.execute(stmt)
        games = result.scalars().all()

        logger.debug(f"Games by ids: found {len(games)} of {len(ids)} requested")
        return games

    # Получение списка

    async def get_available(self) -> List[AvailableGameDTO]:
        """Получает игры из наличия с агрегированными ценами и количеством.

        Returns:
            List[AvailableGameDTO]: список игр из наличия вместе с
            price_purchase, price_selling, games_count.
        """
        logger.debug("Getting available games")

        stmt = (
            select(
                Game,
                func.max(Record.price_purchase).label('price_purchase'),
                func.max(Record.price_selling).label('price_selling'),
                func.count(Record.id).label('games_count'),
            )
            .join(Record, Game.id == Record.game_id)
            .where(Record.status == RecordStatus.AVAILABLE.value)
            .group_by(Game.id)
            .order_by(Game.name)
        )

        rows = (await self.session.execute(stmt)).all()
        games = [
            AvailableGameDTO(
                game=row.Game,
                price_purchase=row.price_purchase,
                price_selling=row.price_selling,
                games_count=row.games_count,
            )
            for row in rows
        ]

        logger.debug(f"Retrieved {len(games)} available games")
        return games
