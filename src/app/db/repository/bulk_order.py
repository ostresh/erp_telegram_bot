from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select

from app.db.models import BulkOrder
from app.db.statuses import BulkOrderStatus
from app.db.repository.base import BaseRepository


import logging

logger = logging.getLogger(__name__)

class BulkOrderRepository(BaseRepository[BulkOrder]):
    """Репозиторий BulkOrder. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BulkOrder)
        
    async def get_delivery_to_me(self) -> List[BulkOrder]:
        """
        Получение всех оптовых заказов
        Которые едут ко мне
        
        Return:
            Список BulkOrder
        
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug("Getting dilevery to me bulk orders")
        
        try:
            stmt = (
                select(BulkOrder)
                .where(
                    BulkOrder.order_status == BulkOrderStatus.IN_TRANSIT.value
                )
                .order_by(BulkOrder.id.asc())
            )
            result = await self.session.execute(stmt)
            bulk_orders = result.scalars().all()
        
            logger.debug(f"Retrieved {len(bulk_orders)} delivery to me bulk orders")
            return bulk_orders
        except Exception as e:
            logger.exception(f"Error getting delivery to me bulk orders {e}")
            raise