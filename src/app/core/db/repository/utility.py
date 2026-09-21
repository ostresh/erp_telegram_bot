from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.models import Utility
from app.core.db.repository.base import BaseRepository


class UtilityRepository(BaseRepository[Utility]):
    """Репозиторий Utility. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Utility)