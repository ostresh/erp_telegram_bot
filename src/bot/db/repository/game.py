from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

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
        
        stmt = select(Game.id).where(Game.name == game_name).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None