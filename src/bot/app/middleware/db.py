from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from bot.db.unit_of_work import UnitOfWork
import logging

logger = logging.getLogger(__name__)


class UnitOfWorkMiddleware(BaseMiddleware):
    """
    Middleware для передачи UnitOfWork в хендлеры.
    
    Автоматически добавляет объект uow в данные хендлера,
    чтобы его можно было получить через dependency injection:
    
        @router.message()
        async def handler(message: Message, uow: UnitOfWork):
            async with uow() as session:
                ...

    """
    
    def __init__(self, uow: UnitOfWork):
        """
        Инициализация middleware.
        
        Args:
            uow: Экземпляр UnitOfWork для управления транзакциями
        """
        self.uow = uow
    
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события и передача UoW в хендлер.
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Событие (сообщение, callback query и т.д.)
            data: Данные, передаваемые в хендлер
            
        Returns:
            Результат выполнения хендлера
        """
        # Добавляем UoW в данные хендлера
        data['uow'] = self.uow
        
        logger.debug(f"UnitOfWork injected for {event.__class__.__name__}")
        
        # Передаем управление следующему обработчику
        return await handler(event, data)