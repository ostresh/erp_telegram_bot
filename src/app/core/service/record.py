from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional

from app.core.db.repository import RecordRepository
from app.core.db.models import Record
from app.core.dto import AvailableRecordDTO
from app.core.service.base import BaseService

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
    
    
    async def get_available(self) -> List[AvailableRecordDTO]:
        """
        Получение всех игр из наличия
        С группировкой по играм
        
        Return:
            List[AvailableRecordDTO]: Record и Game.name
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.info("Getting available records")
        
        try:
            return await self.repo.get_available()
        except Exception as e:
            logger.exception(f"Error get available records: {e}")
            raise
        
    
    async def get_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.info(f"Getting records by game: {game_name}")
                
        try:
            return await self.repo.get_by_game(game_name)
        except Exception as e:
            logger.exception(f"Error getting records by game {game_name}: {e}")
            raise
       
    async def get_available_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей из наличия определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.info(f"Getting available records by game: {game_name}")
                
        try:
            return await self.repo.get_available_by_game(game_name)
        except Exception as e:
            logger.exception(f"Error getting available records by game {game_name}: {e}")
            raise
        
    async def get_in_transit_to_client_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей, которые едут к клиенту, определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.info(f"Getting in transit to client records by game: {game_name}")
                
        try:
            return await self.repo.get_in_transit_to_client_by_game(game_name)
        except Exception as e:
            logger.exception(f"Error getting in transit to client records by game {game_name}: {e}")
            raise
        
    async def get_in_transit_to_me_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей, которые едут к мне, определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.info(f"Getting in transit to me records by game: {game_name}")
                
        try:
            return await self.repo.get_in_transit_to_me_by_game(game_name)
        except Exception as e:
            logger.exception(f"Error getting in transit to me records by game {game_name}: {e}")
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
    
    async def get_in_transit_to_me(self) -> List[Record]:
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
            return await self.repo.get_in_transit_to_me()
        except Exception as e:
            logger.exception(f"Error get delivery to me records: {e}")
            raise
        
    async def get_in_transit_to_client(self) -> List[Record]:
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
            return await self.repo.get_in_transit_to_client()
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
        
    async def get_many_by_ids_with_relations(
        self,
        record_ids: List[int],
    ) -> List[Record]:
        """
        Получает несколько записей со всеми связями одним запросом.

        Использует IN для фильтрации и selectinload для жадной
        загрузки связей, что минимизирует количество запросов к БД.

        Args:
            record_ids: список id записей

        Returns:
            List[Record]: список записей со связями
        """
        
        logger.info(f"Getting Records by ids={record_ids} with relations")
                        
        try:
            return await self.repo.get_many_by_ids_with_relations(record_ids)
        except Exception as e:
            logger.exception(f"Error getting Records by ids={record_ids} with relations: {e}")
            raise
        
    async def get_price_selling_for_game_in_available(self, game_name: str) -> int:
        """
        Получение цены продажи для конкретной игры из наличия
        
        Args:
            game_name: Название игры
            
        Returns:
            Цену для продажи, если:
                Конкретная игра в наличии
                Для этой игры установлена цена (не 0)
            Если цена не установлена, вернет 0
        """
        
        logger.info(f"Getting price_sell for game in available: {game_name}")
                                
        try:
            return await self.repo.get_price_selling_for_game_in_available(game_name)
        except Exception as e:
            logger.exception(f"Error getting price_sell for game in available: {game_name}: {e}")
            raise
            
            
    