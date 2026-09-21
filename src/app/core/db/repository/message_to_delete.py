from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, and_
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from app.core.db.repository.base import BaseRepository
from app.core.db.models import MessageToDelete

import logging

logger = logging.getLogger(__name__)

class MessageToDeleteRepository(BaseRepository[MessageToDelete]):
    """Репозиторий для MessageToDelete. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, MessageToDelete)
        
    async def get_expired(self, hours: int = 1) -> List[MessageToDelete]:
        """
        Получает сообщения, запланированные к удалению более `hours` часов назад.
        
        Используется периодической задачей для очистки чатов пользователей.
        
        Args:
            hours: Количество часов, после которых сообщение считается устаревшим
        
        Returns:
            Список сообщений, готовых к удалению
        
        Raises:
            Exception: При ошибке выполнения запроса к БД
        """
        
        logger.debug(f'Getting expired messages for the last {hours}')
        
        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        try:
            stmt = (
                select(MessageToDelete)
                .where(MessageToDelete.created_at < threshold)
                .order_by(MessageToDelete.created_at.asc())
            )
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.debug(f'Error getting expired messages for the last {hours}: {e}')