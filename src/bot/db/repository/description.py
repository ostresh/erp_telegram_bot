from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Description
from bot.db.repository.base import BaseRepository


class DescriptionRepository(BaseRepository[Description]):
    """Репозиторий Description. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Description)