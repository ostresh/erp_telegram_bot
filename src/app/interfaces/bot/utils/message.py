import logging
from typing import Union

from aiogram.types import Message

from app.core.db.unit_of_work import CeleryUnitOfWork, UnitOfWork
from app.core.service.message_cleanup import MessageCleanupService

logger = logging.getLogger(__name__)


async def schedule_message_for_deletion(
    message: Message,
    uow: Union[UnitOfWork, CeleryUnitOfWork],
) -> None:
    """
    Планирует сообщение бота к удалению через час.
    
    Утилита для использования в обработчиках диалогов и командах.
    Оборачивает работу с сервисом в удобную функцию.
    
    Пример использования:
        >>> result_msg = await message.answer("Запись создана!")
        >>> await schedule_message_for_deletion(result_msg, uow)
    
    Args:
        message: Сообщение бота для планирования удаления
        uow: Unit of Work для работы с БД. Поддерживается как UnitOfWork
            (middleware диалогов), так и CeleryUnitOfWork (Celery задачи).
    
    Raises:
        Exception: При ошибке сохранения в БД (логируется, не прерывает работу)
    """
    
    try:
        async with uow() as session:
            service = MessageCleanupService(session)
            await service.schedule_for_deletion(
                chat_id=message.chat.id,
                message_id=message.message_id,
                user_id=message.from_user.id if message.from_user else 0
            )
    
    except Exception as e:
        logger.error(f"Failed to schedule message for deletion: {e}")