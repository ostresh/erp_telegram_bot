from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Unit of Work - менеджер транзакций.
    
    Управляет жизненным циклом сессии БД:
    - Создает новую сессию для каждой транзакции
    - Коммитит при успешном завершении
    - Откатывает при возникновении ошибки
    - Закрывает сессию в любом случае
    
    Использование:
        async with uow() as session:
            ...
    """
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Инициализация Unit of Work.
        
        Args:
            session_factory: Фабрика сессий (AsyncSessionLocal).
            Каждый вызов фабрики создает НОВУЮ сессию.
        """
        self.session_factory = session_factory
    
    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Контекстный менеджер для работы с транзакцией.
        
        Создает новую сессию, выполняет блок кода и:
        - Коммитит, если всё прошло успешно
        - Откатывает, если возникло исключение
        - Всегда закрывает сессию
        
        Yields:
            AsyncSession: Активная сессия БД
            
        Raises:
            Exception: Любое исключение из блока with после отката
            
        Example:
            async with uow() as session:
                ...
        """
        
        session: AsyncSession = self.session_factory()
        
        try:
            # Возвращаем сессию в блок with
            yield session
            
            # Если дошли сюда без исключений - коммитим транзакцию
            await session.commit()
            logger.debug("Transaction committed successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise 
            
        finally:
            await session.close()
            logger.debug("Database session closed")