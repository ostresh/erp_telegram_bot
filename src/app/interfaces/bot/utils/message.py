import logging

from aiogram.types import Message

from app.core.db.unit_of_work import UnitOfWork
from app.core.service import MessageCleanupService

logger = logging.getLogger(__name__)


async def schedule_message_for_deletion(
    message: Message,
    uow: UnitOfWork,
) -> None:
    """
    Планирует сообщение бота к удалению через час.
    
    Утилита для использования в обработчиках диалогов и команд.
    Оборачивает работу с сервисом в удобную функцию.
    
    Пример использования:
        >>> result_msg = await message.answer("Запись создана!")
        >>> await schedule_message_for_deletion(result_msg, uow)
    
    Args:
        message: Сообщение бота для планирования удаления
        uow: Unit of Work для работы с БД
    
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