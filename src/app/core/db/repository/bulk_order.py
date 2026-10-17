from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db.models import BulkOrder
from app.core.db.statuses import BulkOrderStatus
from app.core.db.repository.base import BaseRepository

import logging

logger = logging.getLogger(__name__)

class BulkOrderRepository(BaseRepository[BulkOrder]):
    """Репозиторий для BulkOrder. Наследует базовые CRUD, добавляет специфичные методы"""

    # Инициализация

    def __init__(self, session: AsyncSession):
        super().__init__(session, BulkOrder)

    # Получение списков

    async def get_by_status(self, status: Optional[BulkOrderStatus] = None) -> List[BulkOrder]:
        """Получает все оптовые заказы с фильтрацией по статусу.

        Args:
            status (Optional[BulkOrderStatus]): Статус для фильтрации
        
        Returns:
            List[BulkOrder]: список оптовых заказов в статусе CREATED.
        """
        logger.debug("Getting created bulk orders")

        stmt = (
            select(BulkOrder)
            .order_by(BulkOrder.id.asc())
        )
        
        if status:
            stmt = stmt.where(BulkOrder.order_status == status.value)
        
        result = await self.session.execute(stmt)
        bulk_orders = result.scalars().all()

        logger.debug(f"Retrieved {len(bulk_orders)} created bulk orders")
        return bulk_orders

    # Получение по идентификаторам

    async def get_many_by_ids(
        self,
        order_ids: List[int],
    ) -> List[BulkOrder]:
        """Получает несколько оптовых заказов по списку id одним запросом.

        Args:
            order_ids (List[int]): список id оптовых заказов.

        Returns:
            List[BulkOrder]: список найденных оптовых заказов.
        """
        logger.debug(f"Getting BulkOrder by ids={order_ids}")

        if not order_ids:
            logger.debug(f"BulkOrders with ids={order_ids} not found")
            return []

        stmt = (
            select(BulkOrder)
            .where(BulkOrder.id.in_(order_ids))
            .order_by(BulkOrder.id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id_with_relations(self, item_id: int) -> Optional[BulkOrder]:
        """Получает оптовый заказ по id с загруженными связями (записи).

        Args:
            item_id (int): id оптового заказа.

        Returns:
            Optional[BulkOrder]: оптовый заказ со связями или None, если не найден.
        """
        logger.debug(f"Getting BulkOrder by id={item_id} with relations")

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
            logger.debug(f"BulkOrder with id={item_id} found (with relations)")
        else:
            logger.debug(f"BulkOrder with id={item_id} not found")

        return item