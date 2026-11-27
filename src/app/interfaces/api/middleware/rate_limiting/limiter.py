import hashlib
import time

from redis.asyncio import Redis

from app.interfaces.api.config import api_config

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
    ) -> RateLimitResult:
        """
        Проверяет, не превышен ли лимит по IP.
        
        Args:
            ip (str): IP адрес
            
        Returns:
            RateLimitResult с информацией о разрешении и текущем счётчике
        """
        
        key = f"rl:ip:{ip}"
        return await self._check_limit(
            key=key,
            limit=api_config.rate_limit_ip_limit,
            window_size=api_config.rate_limit_window_size
        )
    
    async def check_hash_limit(
        self,
        token_hash: str,
    ) -> RateLimitResult:
        """
        Проверяет, не превышен ли лимит по token_hash.
        
        Args:
            token_hash (str): SHA-256 токена
            
        Returns:
            RateLimitResult с информацией о разрешении и текущем счётчике
        """
        
        key = f"rl:token:{token_hash}"
        return await self._check_limit(
            key=key,
            limit=api_config.rate_limit_token_limit,
            window_size=api_config.rate_limit_window_size
        )
    
    def extract_token_hash(self, auth_header: str | None) -> str | None:
        """
        Извлекает текоен из заголовка Authorization и возвращает его хеш
        
        Формат заголовка: "Bearer <token>"
        
        Args:
            auth_header (str | None): Значение заголовка Authorization
            
        Returns:
            SHA-256 хеш токена или None, если заголовок некорректен
        """
        
        if not auth_header:
            return None
        
        # проверяем формат: "Bearer <token>"
        parts = auth_header.split(" ", 1)
        if len(parts) != 2:
            return None
        
        scheme, token = parts
        if scheme.lower() != "bearer":
            return None
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash
    
    async def _check_limit(
        self,
        key: str,
        limit: int,
        window_size: int
    ) -> RateLimitResult:
        """
        Проверяет лимит запросов по ключу
        
        Args:
            key (str): ключ
            limit (int): лимит
            window_size (int): окно
            
        Returns:
            RateLimitResult с информацией о разрешении и текущем счётчике
        """
        
        now = int(time.time())
        
        current = await self.redis.eval(
            RATE_LIMIT_LUA_SCRIPT,
            1,
            key,
            limit,
            window_size,
            now
        )
        
        allowed = current <= limit
        remaining = max(0, limit - current)
                
        return RateLimitResult(
            allowed=allowed,
            current_count=int(current),
            limit=limit,
            window_size=window_size,
            remaining=remaining
        )