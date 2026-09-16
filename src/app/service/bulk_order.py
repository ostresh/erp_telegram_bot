from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.repository import BulkOrderRepository
from app.db.models import BulkOrder
from app.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class BulkOrderService(BaseService[BulkOrder, BulkOrderRepository]):
    """Сервис для работы с BulkOrder"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BulkOrderRepository(session))
        
    async def get_delivery_to_me(self) -> List[BulkOrder]:
        """
        Получение всех записей
        Которые едут ко мне
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке создания
        """
        
        logger.info("Getting delivery to me bulk orders")
                
        try:
            return await self.repo.get_delivery_to_me()
        except Exception as e:
            logger.exception(f"Error get delivery to me bulk orders: {e}")
            raise