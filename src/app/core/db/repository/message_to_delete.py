from typing import List
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.db.repository.base import BaseRepository
from app.core.db.models import MessageToDelete

import logging

logger = logging.getLogger(__name__)

class MessageToDeleteRepository(BaseRepository[MessageToDelete]):
    """Репозиторий для MessageToDelete. Наследует базовые CRUD, добавляет специфичные методы"""

    # Инициализация

    def __init__(self, session: AsyncSession):
        super().__init__(session, MessageToDelete)

    # Получение сообщений

    async def get_expired(self, hours: int = 1) -> List[MessageToDelete]:
        """Получает сообщения, запланированные к удалению более `hours` часов назад.

        Args:
            hours (int): количество часов, после которых сообщение считается устаревшим.

        Returns:
            List[MessageToDelete]: список сообщений, готовых к удалению.
        """
        logger.debug(f"Getting expired messages for the last {hours}")

        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

        stmt = (
            select(MessageToDelete)
            .where(MessageToDelete.created_at < threshold)
            .order_by(MessageToDelete.created_at.asc())
        )

        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        logger.debug(f"Retrieved {len(messages)} expired messages")
        return messages

    # Удаление сообщений

    async def delete_by_ids(self, ids: List[int]) -> int:
        """Удаляет записи по списку id одним запросом.

        Позволяет избавиться от N+1: вместо отдельного DELETE на каждую запись
        выполняется один запрос с условием `id IN (...)`.

        Args:
            ids (List[int]): список id удаляемых записей.

        Returns:
            int: количество удалённых записей.

        Raises:
            Exception: При ошибке удаления
        """
        unique_ids = set(ids)

        if not unique_ids:
            logger.debug("No message ids provided for deletion")
            return 0

        logger.debug(f"Deleting {len(unique_ids)} {MessageToDelete.__name__} records")

        try:
            stmt = (
                delete(MessageToDelete)
                .where(MessageToDelete.id.in_(unique_ids))
            )

            result = await self.session.execute(stmt)

            deleted = result.rowcount or 0
            logger.debug(f"Deleted {deleted} {MessageToDelete.__name__} records")
            return deleted
        except Exception as e:
            logger.exception(f"Error deleting {MessageToDelete.__name__} records: {e}")
            raise