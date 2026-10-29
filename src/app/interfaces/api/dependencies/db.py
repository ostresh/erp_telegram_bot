from collections.abc import AsyncGenerator

from app.core.db.config import get_uow as create_uow
from app.core.db.unit_of_work import UnitOfWork

async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """
    Зависимость FastAPI для получения UnitOfWork.

    Создаёт новый UoW для каждого запроса.
    Сессия автоматически закрывается после завершения запроса.

    Использование:
        async def endpoint(uow: UnitOfWork = Depends(get_uow)):
            async with uow() as session:
                result = await session.execute(...)
    """
    yield create_uow()