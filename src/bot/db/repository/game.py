from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from bot.db.models import Game
from bot.db.repository.base import BaseRepository


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
        """
        
        stmt = (
            select(
                exists(
                    select(Game.name)
                    .where(Game.name == game_name)
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar()