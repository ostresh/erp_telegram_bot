from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db.models import BulkOrder, Record
from app.core.db.statuses import BulkOrderStatus
from app.core.db.repository.base import BaseRepository


import logging

logger = logging.getLogger(__name__)

class BulkOrderRepository(BaseRepository[BulkOrder]):
    """Репозиторий BulkOrder. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BulkOrder)
        
    async def get_created(self) -> List[BulkOrder]:
        """
        Получение всех новосозданных оптовых заказов
        
        Return:
            Список BulkOrder
        
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug("Getting created bulk orders")
        
        try:
            stmt = (
                select(BulkOrder)
                .where(
                    BulkOrder.order_status == BulkOrderStatus.CREATED.value
                )
                .order_by(BulkOrder.id.asc())
            )
            result = await self.session.execute(stmt)
            bulk_orders = result.scalars().all()
        
            logger.debug(f"Retrieved {len(bulk_orders)} created bulk orders")
            return bulk_orders
        except Exception as e:
            logger.exception(f"Error getting created bulk orders {e}")
            raise
        
    async def get_in_transit(self) -> List[BulkOrder]:
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
        
    async def get_many_by_ids(
        self,
        order_ids: List[int],
    ) -> List[BulkOrder]:
        """
        Получает несколько записей со всеми связями одним запросом.

        Использует IN для фильтрации и selectinload для жадной
        загрузки связей, что минимизирует количество запросов к БД.

        Args:
            record_ids: список id записей

        Returns:
            List[Record]: список записей со связями
        """
        
        logger.debug(f"Getting BulkOrder by ids={order_ids}")
        
        if not order_ids:
            logger.debug(f"BulkOrders with ids={order_ids} not found")
            return []

        try:
            stmt = (
                select(BulkOrder)
                .where(BulkOrder.id.in_(order_ids))
                .order_by(BulkOrder.id.asc())
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.exception(f"Error getting BulkOrder by ids={order_ids}: {e}")
            raise
        
    async def get_by_id_with_relations(self, item_id: int) -> Optional[BulkOrder]:
        """
        Получение оптового заказа по id с загруженными связями
        (записи) для полного вывода информации
        
        Args:
            item_id - id записи
        
        Return:
            Объект BulkOrder с загруженными связями или None
        
        Raises:
            Exception: При ошибке получения
        """
        logger.debug(f"Getting BulkOder by id={item_id} with relations")
        
        try:
            stmt = (
                select(BulkOrder)
                .options(
                    selectinload(BulkOrder.records),
                )
                .where(BulkOrder.id == item_id)
            )
            result = await self.session.execute(stmt)
            item = result.scalar()
            
            if item:
                logger.debug(f"BulkOder with id={item_id} found (with relations)")
            else:
                logger.debug(f"BulkOder with id={item_id} not found")
            
            return item
        except Exception as e:
            logger.exception(f"Error getting BulkOder by id={item_id} with relations: {e}")
            raise