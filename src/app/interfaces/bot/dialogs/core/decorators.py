import functools
import logging
from typing import Any, Callable

from aiogram_dialog import DialogManager, ShowMode
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

DB_ERROR_TEXT = '❌ Ошибка БД. Попробуйте позже'


def _find_manager(args: tuple, kwargs: dict) -> Any:
    """Ищет DialogManager по наличию характерных атрибутов"""
    for arg in (*args, *kwargs.values()):
        if hasattr(arg, 'dialog_data') and hasattr(arg, 'middleware_data'):
            return arg
    return None


def _find_message(args: tuple, kwargs: dict) -> Any:
    """Ищет Message по наличию характерных атрибутов"""
    for arg in (*args, *kwargs.values()):
        # Message имеет message_id и chat, но НЕ имеет data (это у CallbackQuery)
        if hasattr(arg, 'message_id') and hasattr(arg, 'chat') and not hasattr(arg, 'data'):
            return arg
    return None


def _find_callback(args: tuple, kwargs: dict) -> Any:
    """Ищет CallbackQuery по наличию характерных атрибутов"""
    for arg in (*args, *kwargs.values()):
        # CallbackQuery имеет message и data
        if hasattr(arg, 'message') and hasattr(arg, 'data'):
            return arg
    return None


def handle_db_errors(func: Callable) -> Callable:
    """
    Декоратор для обработчиков событий диалога.

    Ловит ошибки БД:
        - логирует traceback
        - показывает пользователю временное сообщение об ошибке
        - тихо завершает обработчик (окно диалога не ломается)

    Требует, чтобы в сигнатуре обработчика были
    Message (или CallbackQuery) и DialogManager.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError:
            logger.exception(f'DB error in handler: {func.__qualname__}')

            manager: DialogManager = _find_manager(args, kwargs)
            message = _find_message(args, kwargs)

            manager.show_mode = ShowMode.DELETE_AND_SEND
            
            if message is None:
                callback = _find_callback(args, kwargs)
                message = callback.message if callback else None

            if manager is None or message is None:
                return None

            uow = manager.middleware_data['uow']
            error_message = await message.answer(DB_ERROR_TEXT)
            
            # schedule_message_for_deletion принимает (message, uow)
            from app.interfaces.bot.utils.message import schedule_message_for_deletion
            await schedule_message_for_deletion(error_message, uow)
            return None

    return wrapper