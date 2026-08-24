from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from bot.db.models import Utility
from bot.db.repository.base import BaseRepository


class UtilityRepository(BaseRepository[Utility]):
    """Репозиторий Utility. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Utility)