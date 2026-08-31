from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists
from typing import List, Tuple, Optional

from bot.db.models import Record, Game
from bot.db.repository.base import BaseRepository
from bot.db.status.status import RecordStatus

import logging

logger = logging.getLogger(__name__)

class RecordRepository(BaseRepository[Record]):
    """Репозиторий для Record. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Record)
    
    
    async def is_game_available(self, game_name: str) -> bool:
        """
        Проверка, есть ли игра в наличии
        
        Args:
            game_name - название игры
        
        Return:
            Bool есть ли игра
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug(f"Checking availability for game '{game_name}'")
        
        try:
            stmt = select(
            exists(
                select(Record.id)
                .join(Game, Record.game_id == Game.id)
                .where(
                    Game.name == game_name,
                    Record.status == RecordStatus.AVAILABLE.value
                )
            ))
            result = await self.session.execute(stmt)
            available = result.scalar()
            
            logger.debug(f"Game '{game_name}' available: {available}")
            return available
        except Exception:
            logger.debug(f"Error checking availability for game '{game_name}'")
            raise
    
    async def get_available_games(self) -> List[Tuple[str, int, int]]:
        """
        Получение всех игр из наличия
        С группировкой по играм
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug("Getting available games")
        
        try:
            stmt = (
                select(Game.name, Record.price_purchase,Record.price_selling)
                .join(Game, Record.game_id == Game.id)
                .where(Record.status == RecordStatus.AVAILABLE.value)
                .group_by(Record.game_id, Game.name, Record.price_selling)
                .order_by(Game.name)
            )
            result = await self.session.execute(stmt)
            games = result.all()
            
            logger.debug(f"Retrieved {len(games)} available games")
            return games
        except Exception:
            logger.debug("Error getting available games")
            raise
    
    async def update_price_selling_for_games(self, game_name: str, new_price: int) -> int:
        """
        Обновляет цену продажи для всех доступных записей игры
        
        Args:
            game_name - название игры
            new_price - цена
            
        Return:
            количество измененных строк или None
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug(f"Updating price for game '{game_name}' to {new_price}")
        
        try:
            stmt = (
                update(Record)
                .where(
                    Record.status == RecordStatus.AVAILABLE.value,
                    Record.game_id.in_(
                        select(Game.id).where(Game.name == game_name)
                    )
                )
                .values(price_selling=new_price)
            )
            
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            count = result.rowcount
            
            is_updated = count > 0
            
            if is_updated:      
                logger.debug(f"Updated price for {count} records of game '{game_name}'")
            else:
                logger.debug(f"Available {game_name} in records not found'")
            return count
        except Exception:
            logger.debug(f"Error updating price for game '{game_name}'")
            raise