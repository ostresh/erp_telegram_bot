from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import config


DATABASE_URL = (
    f"postgresql+asyncpg://{config.DB_CONFIG['user']}:{config.DB_CONFIG['password']}"
    f"@{config.DB_CONFIG['host']}:{config.DB_CONFIG['port']}/{config.DB_CONFIG['database']}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

def get_uow():
    """
    Фабричная функция для создания UnitOfWork.
    
    Returns:
        UnitOfWork: Экземпляр с настроенной фабрикой сессий
    """
    from app.db.unit_of_work import UnitOfWork
    return UnitOfWork(session_factory=AsyncSessionLocal)


async def close_db():
    """Закрытие соединений с БД"""
    await engine.dispose()