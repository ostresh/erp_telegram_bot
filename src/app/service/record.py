from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional

from app.db.repository import RecordRepository
from app.db.models import Record
from app.service.base import BaseService

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
    
    async def get_delivery_to_me(self) -> List[Record]:
        """
        Получение всех записей
        Которые едут ко мне
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке создания
        """
        
        logger.info("Getting delivery to me records")
        
        try:
            return await self.repo.get_delivery_to_me()
        except Exception as e:
            logger.exception(f"Error get delivery to me records: {e}")
            raise
        
    async def get_delivery_to_client(self) -> List[Record]:
        """
        Получение всех записей
        Которые едут к покупателю
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке создания
        """
        
        logger.info("Getting delivery to client records")
        
        try:
            return await self.repo.get_delivery_to_client()
        except Exception as e:
            logger.exception(f"Error get delivery to client records: {e}")
            raise
        
        
    async def get_by_bulk_order_id(self, order_id: int) -> List[Record]:
        """
        Получение всех записей,
        связанных с оптовым заказом
        
        Args:
            order_id - id оптового заказа
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке получения
        """
        
        logger.info(f"Getting records for bulk order id={order_id}")
                
        try:
            return await self.repo.get_by_bulk_order_id(order_id)
        except Exception as e:
            logger.exception(f"Error get records for bulk order id={order_id}: {e}")
            raise
    
        
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Record]:
        """
        Получение записи по id с загруженными связями
        (игра и транзакция) для полного вывода информации
        
        Args:
            item_id - id записи
        
        Return:
            Объект Record с загруженными связями или None
        
        Raises:
            Exception: При ошибке получения
        """
        
        logger.info(f"Getting Record by id={item_id} with relations")
                        
        try:
            return await self.repo.get_by_id_with_relations(item_id)
        except Exception as e:
            logger.exception(f"Error getting Record by id={item_id} with relations: {e}")
            raise
            
            
    