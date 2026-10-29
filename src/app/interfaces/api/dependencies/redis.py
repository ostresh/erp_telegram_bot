from collections.abc import AsyncGenerator

from redis.asyncio import Redis

_redis_client: Redis | None = None

async def get_redis() -> Redis:
    """
    Зависимость FastAPI для получения Redis клиента.

    Возвращает уже созданный Redis клиент.
    """
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return _redis_client

async def init_redis_client() -> Redis:
    """
    Инициализация Redis клиента при старте приложения.

    Вызывается в lifespan контексте main.py.
    """
    global _redis_client
    
    from app.interfaces.api.config import api_config
    
    _redis_client = Redis.from_url(
        api_config.redis_url,
        decode_responses=True
    )
    
    return _redis_client

async def close_redis_client() -> None:
    """
    Закрытие Redis клиента при остановке приложения.

    Вызывается в lifespan контексте main.py.
    """
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None