from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import BulkOrder
from bot.db.repository.base import BaseRepository


class BulkOrderRepository(BaseRepository[BulkOrder]):
    """Репозиторий BulkOrder. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, BulkOrder)