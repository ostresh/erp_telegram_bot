# middleware/auth_middleware.py
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Dict, Callable, Awaitable
from config import config

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, CallbackQuery):
            return await handler(event, data)
        
        if event.from_user and event.from_user.id == config.OWNER_ID:
            return await handler(event, data)
        else:
            await event.answer("❌ У вас нет доступа к этому боту.", show_alert=True)
            
        return  # Блокируем выполнение хендлера
