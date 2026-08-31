from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional

from bot.db.repository import RecordRepository
from bot.db.models import Record
from bot.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class RecordService(BaseService[Record, RecordRepository]):
    """Сервис для работы с Record"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, RecordRepository(session))
        
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
        
        logger.info(f"Checking availability for game '{game_name}'")
        
        try:
            return await self.repo.is_game_available(game_name)
        except Exception as e:
            logger.exception(f"Error checking game available: {e}")
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
        
        logger.info("Getting available games")
        
        try:
            return await self.repo.get_available_games()
        except Exception as e:
            logger.exception(f"Error get available games: {e}")
            raise
        
    
    async def update_price_selling_for_games(self, game_name: str, new_price: int) -> int:
        """
        Обновляет цену продажи для всех доступных записей игры
        
        Args:
            game_name - название игры
            new_price - цена
            
        Return:
            количество измененных строк
        """
        
        logger.info(f"Updating price for game '{game_name}' to {new_price}")
        
        try:
            rowscount = await self.repo.update_price_selling_for_games(game_name, new_price)
            
            is_updated = rowscount > 0
            
            if is_updated:
                logger.info(f'Update price selling ({new_price}) for {game_name} successfully')
            else:
                logger.warning(f"Available {game_name} in records not found")
            
            return rowscount
        except Exception as e:
            logger.exception(f'Error for update price selling for {game_name}: {e}')
            raise
    