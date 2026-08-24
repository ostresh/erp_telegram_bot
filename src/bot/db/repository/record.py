from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from bot.db.models import Record, Game
from bot.db.repository.base import BaseRepository
from bot.db.status.status import RecordStatus

class RecordRepository(BaseRepository[Record]):
    """Репозиторий для Record. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Record)
    
    
    async def is_game_aviable(self, game_name: str) -> bool:
        """
        Проверка, есть ли игра в наличии
        
        Return:
            Bool есть ли игра
        """
        
        stmt = select(
        exists(
            select(Record.id)
            .where(
                Record.game_id.in_(
                    select(Game.id).where(Game.name == game_name)
                ),
                Record.status == RecordStatus.AVAILABLE.value
            )
        ))
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def get_aviable_games(self) -> List[Record]:
        """
        Получение всех игр из наличия
        С группировкой по играм
        
        Return:
            Список Record
        """
        
        stmt = (
            select(Game.name, Record.price_selling)
            .join(Game, Record.game_id == Game.id)
            .where(Record.status == RecordStatus.AVAILABLE.value)
            .group_by(Record.game_id, Game.name, Record.price_selling)
            .order_by(Game.name)
        )
        result = await self.session.execute(stmt)
        return result.all()
    
    
    async def update_price_selling_for_games(self, game_name: str, new_price: int) -> int:
        """
        Обновляет цену продажи для всез доступных записей игры
        
        Args:
            game_name - название игры
            new_price - цена
            
        Return:
            количество измененных строк
        """
        
        stmt = (
            update(Record)
            .where(
                and_(
                    Record.status == RecordStatus.AVAILABLE.value,
                    Record.game_id.in_(
                        select(Game.id).where(Game.name == game_name)
                        )
                    )
                )
            .values(price_selling=new_price)
        )
        
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
    