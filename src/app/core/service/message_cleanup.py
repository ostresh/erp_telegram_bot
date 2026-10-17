from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
)

from app.core.db.repository import MessageToDeleteRepository
from app.core.db.models import MessageToDelete
from app.core.service.base import BaseService

import logging

logger = logging.getLogger(__name__)

class MessageCleanupService(BaseService[MessageToDelete, MessageToDeleteRepository]):
    """Сервис для работы с MessageToDelete"""

    HOURS_TO_KEEP = 1  # Сколько часов хранить сообщения
    BATCH_SIZE = 100   # Максимум сообщений за один запрос к Telegram

    # Ошибки Telegram, при которых повторная попытка удаления не поможет:
    # сообщение/чат недоступны навсегда. Такие записи удаляются из БД,
    # чтобы не ретраиться бесконечно.
    PERMANENT_ERROR_MARKERS = (
        "message to delete not found",
        "message is not found",
        "message can't be deleted",
        "chat not found",
        "peer_id_invalid",
    )

    # Инициализация

    def __init__(self, session: AsyncSession):
        super().__init__(session, MessageToDeleteRepository(session))

    # Основные операции

    async def schedule_for_deletion(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
    ) -> None:
        """Планирует сообщение к удалению через HOURS_TO_KEEP часов.

        Args:
            chat_id (int): id чата, где находится сообщение.
            message_id (int): id сообщения бота.
            user_id (int): id пользователя, которому показано сообщение.

        Returns:
            None
        """
        try:
            message = MessageToDelete(
                chat_id=chat_id,
                message_id=message_id,
                user_id=user_id,
            )

            await self.repo.create(message)
        except Exception:
            logger.exception("Error scheduling message for deletion")
            raise

    async def cleanup_expired_messages(self, bot: Bot) -> int:
        """Удаляет сообщения, запланированные к удалению более HOURS_TO_KEEP назад.

        Процесс:
        1. Получает устаревшие сообщения из БД.
        2. Группирует их по chat_id.
        3. Удаляет из Telegram батчами по BATCH_SIZE штук.
        4. Удаляет из БД одним запросом записи, которые были удалены,
           уже отсутствуют или недостижимы навсегда. Записи с временными
           ошибками остаются для повторной попытки.

        Args:
            bot (Bot): экземпляр бота для удаления сообщений. Жизненным циклом
                бота управляет вызывающая сторона (создаётся на каждую задачу).

        Returns:
            int: количество обработанных сообщений.
        """
        try:
            expired = await self.repo.get_expired(self.HOURS_TO_KEEP)

            if not expired:
                return 0

            by_chat = self._group_by_chat(expired)

            handled = await self._delete_from_telegram(by_chat, bot)

            await self._cleanup_database(expired, handled)

            return len(handled)
        except Exception:
            logger.exception("Error cleaning up expired messages")
            raise

    # Вспомогательные методы

    def _group_by_chat(
        self,
        messages: List[MessageToDelete],
    ) -> dict[int, List[int]]:
        """Группирует сообщения по chat_id.

        Args:
            messages (List[MessageToDelete]): список сообщений для группировки.

        Returns:
            dict[int, List[int]]: словарь {chat_id: [message_id, ...]}.
        """
        by_chat: dict[int, List[int]] = {}

        for message in messages:
            by_chat.setdefault(message.chat_id, []).append(message.message_id)

        return by_chat

    @classmethod
    def _is_permanent_error(cls, error: Exception) -> bool:
        """Проверяет, что повторная попытка удаления не поможет.

        Args:
            error (Exception): исключение, полученное от Telegram API.

        Returns:
            bool: True, если сообщение недостижимо навсегда.
        """
        # Бот исключён из чата / не имеет прав — ситуация не изменится сама
        if isinstance(error, TelegramForbiddenError):
            return True

        # Чат или сообщение не найдены
        if isinstance(error, TelegramNotFound):
            return True

        # Часть недостижимых случаев приходит как Bad Request
        if isinstance(error, TelegramBadRequest):
            text = str(error).lower()
            return any(
                marker in text for marker in cls.PERMANENT_ERROR_MARKERS
            )

        return False

    async def _delete_from_telegram(
        self,
        by_chat: dict[int, List[int]],
        bot: Bot,
    ) -> set[tuple[int, int]]:
        """Удаляет сообщения из Telegram.

        Telegram API позволяет удалять до BATCH_SIZE сообщений за один запрос,
        поэтому сообщения разбиваются на батчи. Ошибка удаления отдельного
        батча не прерывает обработку остальных.

        Безнадёжные ошибки (чат удалён, бот исключён из чата, сообщение
        недоступно) считаются обработанными: повторять попытки бессмысленно,
        поэтому такие записи должны быть удалены из БД. Временные ошибки
        (флуд-контроль, сетевые сбои, 5xx) оставляют записи для ретрая.

        Args:
            by_chat (dict[int, List[int]]): словарь {chat_id: [message_id, ...]}.
            bot (Bot): экземпляр бота для удаления сообщений.

        Returns:
            set[tuple[int, int]]: множество (chat_id, message_id) сообщений,
            которые удалены, уже отсутствуют в чате или недостижимы навсегда.
        """
        handled: set[tuple[int, int]] = set()

        for chat_id, message_ids in by_chat.items():
            for i in range(0, len(message_ids), self.BATCH_SIZE):
                chunk = message_ids[i:i + self.BATCH_SIZE]

                try:
                    await bot.delete_messages(
                        chat_id=chat_id,
                        message_ids=chunk,
                    )
                except Exception as error:
                    if not self._is_permanent_error(error):
                        logger.exception("Failed to delete messages in chat")
                        continue

                    logger.warning(
                        "Messages in chat_id=%s are unreachable, "
                        "dropping them from DB: %s",
                        chat_id,
                        error,
                    )

                handled.update((chat_id, message_id) for message_id in chunk)

        return handled

    async def _cleanup_database(
        self,
        messages: List[MessageToDelete],
        handled: set[tuple[int, int]],
    ) -> None:
        """Удаляет обработанные записи из БД одним батчем.

        Записи, которые не удалось обработать в Telegram, остаются в БД
        и будут повторно обработаны при следующем запуске.

        Args:
            messages (List[MessageToDelete]): список устаревших сообщений.
            handled (set[tuple[int, int]]): (chat_id, message_id) сообщений,
                удалённых, уже отсутствующих в чате или недостижимых навсегда.

        Returns:
            None
        """
        ids = [
            item.id
            for item in messages
            if (item.chat_id, item.message_id) in handled
        ]

        if not ids:
            return

        await self.repo.delete_by_ids(ids)