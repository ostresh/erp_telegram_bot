import time

from redis.asyncio import Redis

from .lua_scripts import RATE_LIMIT_LUA_SCRIPT
from .schemas import RateLimitResult


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
        
    async def check_ip_limit(
        self,
        ip: str,
        limit: int,
        window_size: int
    ) -> RateLimitResult:
        """
        Проверяет, не превышен ли лимит.
        
        Args:
            ip: IP адрес
            limit: Максимальное количество запросов
            window_size: Размер окна в секундах
            
        Returns:
            RateLimitResult с информацией о разрешении и текущем счётчике
        """

        # генерируем ключ для текущего окна
        # формат: rl:ip:<IP>:<timestamp_окна>
        current_window = self._get_current_window(window_size)
        key = f"rl:ip:{ip}:{current_window}"
        
        # выполняем Lua скрипт атомарно
        current = await self.redis.eval(
            RATE_LIMIT_LUA_SCRIPT,
            1,
            key,
            limit,
            window_size
        )
        
        # проверка, не превышен ли лимит
        allowed = current <= limit
            
        return RateLimitResult(
            allowed=allowed,
            current_count=int(current),
            limit=limit,
            remaining=max(0, limit - current)
        )
        
    def _get_current_window(self, window_size: int) -> int:
        """
        Возвращает номер текущего окна
        
        Например, если window_size=60 и сейчас 14:35:23
        то номер окна будет 14:35:00 (начало минуты)
        """
        current_time = int(time.time())
        return current_time - (current_time % window_size)
        
        
    