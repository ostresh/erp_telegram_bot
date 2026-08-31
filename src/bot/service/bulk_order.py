from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import BulkOrderRepository
from bot.db.models import BulkOrder
from bot.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class BulkOrderService(BaseService[BulkOrder, BulkOrderRepository]):
    """Сервис для работы с BulkOrder"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BulkOrderRepository(session))