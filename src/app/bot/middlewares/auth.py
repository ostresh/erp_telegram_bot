from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Dict, Callable, Awaitable
from config import config
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """
    Middleware для проверки доступа к боту.
    
    Пропускает только владельца бота (config.OWNER_ID).
    Остальным пользователям отправляет сообщение об отсутствии доступа.
    """
    
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем callback query (они уже прошли проверку через message)
        if isinstance(event, CallbackQuery):
            logger.debug(f"AuthMiddleware: passing CallbackQuery from user {event.from_user.id}")
            return await handler(event, data)
        
        # Проверяем доступ для message
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id if event.from_user else None
        
        if user_id and user_id == config.OWNER_ID:
            logger.debug(f"AuthMiddleware: access granted for user {user_id}")
            return await handler(event, data)
        else:
            logger.warning(f"AuthMiddleware: access denied for user {user_id}")
            # Для Message используем answer(), но это работает только для CallbackQuery
            # Для Message нужно использовать bot.send_message
            bot = data.get('bot')
            if bot and event.chat:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text="❌ У вас нет доступа к этому боту."
                )
            return  # Блокируем выполнение хендлера