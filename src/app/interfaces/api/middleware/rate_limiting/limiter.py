from redis.asyncio import Redis
from pydantic import BaseModel, Field

class RateLimitResult(BaseModel):
    """
    Результат проверки rate limit
    
    Attributes:
        allowed (bool): разрешены ли запросы
        current_count (int): количество оставшихся запросов
    """
    
    allowed: bool = Field(..., description="Разрешены ли запросы")
    current_count: int = Field(..., description="Количество оставшихся запросов")
    

class RateLimiter:
    """
    Rate Limiter с ипспользованием Redis
    
    Позже здесь будет:
        - Lua скрипт для атомарной проверки
        - Проверка по IP
        - Проверка по хешу токена
    """
    
    def __init__(self, redis: Redis):
        self.redis = redis
        
    async def check_limit(
        self,
        key: str,
        limit: int,
        window_size: int
    ) -> RateLimitResult:
        """
        Проверяет, не превышен ли лимит.
        
        Args:
            key: Уникальный ключ (IP или хеш токена)
            limit: Максимальное количество запросов
            window_size: Размер окна в секундах
            
        Returns:
            RateLimitResult
        """
        
        # пока заглушка
        return RateLimitResult(
            allowed=True,
            current_count=0
        )
        
    