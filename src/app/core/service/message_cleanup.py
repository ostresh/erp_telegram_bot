from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from config import config
from app.interfaces.bot.core.celery_bot import get_bot
from app.core.db.repository import MessageToDeleteRepository
from app.core.db.models import MessageToDelete
from app.core.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class MessageCleanupService(BaseService[MessageToDelete, MessageToDeleteRepository]):
    """Сервис для работы с MessageToDelete"""
    
    HOURS_TO_KEEP = 1  # Сколько часов хранить сообщения
    BATCH_SIZE = 100   # Максимум сообщений за один запрос к Telegram
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, MessageToDeleteRepository(session))
        
    async def schedule_for_deletion(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
    ) -> None:
        """
        Планирует сообщение к удалению через HOURS_TO_KEEP часов.
        
        Вызывается после отправки сообщения-результата пользователю.
        
        Args:
            chat_id: ID чата, где находится сообщение
            message_id: ID сообщения бота
            user_id: ID пользователя, которому показано сообщение
        
        Raises:
            Exception: При ошибке сохранения в БД
        """
        
        message = MessageToDelete(
            chat_id = chat_id,
            message_id = message_id,
            user_id = user_id
        )
        
        await self.repo.create(message)
        
        logger.info(
            f"Scheduled message for deletion: "
            f"chat_id={chat_id}, message_id={message_id}, user_id={user_id}"
        )
        
    async def cleanup_expired_messages(self) -> int:
        """
        Удаляет все сообщения, запланированные к удалению более HOURS_TO_KEEP назад.
        
        Процесс:
        1. Получает устаревшие сообщения из БД
        2. Группирует их по chat_id
        3. Удаляет из Telegram батчами по 100 штук
        4. Удаляет записи из БД
        
        Returns:
            Количество успешно удалённых сообщений
        
        Raises:
            Exception: При критической ошибке очистки
        """
        
        expired = await self.repo.get_expired(self.HOURS_TO_KEEP)
        
        if not expired:
            logger.debug("No expired messages to delete")
            return 0
        
        logger.info(f"Found {len(expired)} expired messages")
        
        by_chat = self._group_by_chat(expired)
        
        deleted_count = await self._delete_from_telegram(by_chat)
        
        await self._cleanup_database(expired)
        
        logger.info(f"Cleanup completed: {deleted_count} messages deleted")
        
        return deleted_count
        
    def _group_by_chat(
        self,
        messages: List[MessageToDelete]
    ) -> dict[int, List[int]]:
        """
        Группирует сообщения по chat_id.
        
        Args:
            messages: Список сообщений для группировки
        
        Returns:
            Словарь {chat_id: [message_id, ...]}
        """
        
        by_chat: dict[int, List[int]] = {}
        
        for message in messages:
            by_chat.setdefault(message.chat_id, []).append(message.message_id)
            
        return by_chat
    
    
    async def _delete_from_telegram(
        self,
        by_chat: dict[int, List[int]]
    ) -> int:
        """
        Удаляет сообщения из Telegram.
        
        Telegram API позволяет удалять до 100 сообщений за один запрос,
        поэтому сообщения разбиваются на батчи.
        
        Args:
            by_chat: Словарь {chat_id: [message_id, ...]}
        
        Returns:
            Количество успешно удалённых сообщений
            
        Exceptions:
            Ошибки при удалении сообщений
        """
        
        bot = get_bot()
        
        deleted_count = 0
        
        try:
            for chat_id, message_ids in by_chat.items():
                for i in range(0, len(message_ids), self.BATCH_SIZE):
                    chunk = message_ids[i:i + self.BATCH_SIZE]

                    try:
                        await bot.delete_messages(
                            chat_id=chat_id,
                            message_ids=chunk
                        )
                        deleted_count += len(chunk)
                    except Exception as e:
                        logger.warning(
                            f"Failed to delete messages in chat {chat_id}: {e}"
                        )
        
        finally:
            await bot.session.close()
            
        return deleted_count
    
    async def _cleanup_database(
        self,
        messages: List[MessageToDelete]
    ) -> None:
        """
        Удаляет обработанные записи из БД.
        
        Args:
            messages: Список обработанных сообщений
        """
        
        for item in messages:
            await self.repo.delete(item.id)
        
        
