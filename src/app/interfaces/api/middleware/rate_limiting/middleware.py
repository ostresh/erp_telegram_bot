from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.interfaces.api.config import api_config
from app.interfaces.api.dependencies.redis import get_redis
from .schemas import RateLimitResult
from .limiter import RateLimiter

import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware для ограничения количества запросов
    
    Проверяет лимиты по порядку:
    1. Лимит по IP (основная защита от перебора)
    2. Лимит по токену (если токен есть)
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Обработка запроса
        
        Пока просто пропускаем все запросы
        Позже здесь будет проверка лимитов
        """
        
        if not api_config.rate_limit_enabled:
            return await call_next(request)
        
        try:
            
            redis = await get_redis()
            limiter = RateLimiter(redis)
            
            ip = self._get_client_ip(request) if request.client else 'unknown'
            
            # 1. проверка лимита по ip
            ip_result = await limiter.check_ip_limit(ip=ip)
            if not ip_result.allowed:
                return self._rate_limit_response(ip_result)
            
            # 2. проверка лимита по хешу
            token_hash = limiter.extract_token_hash(
                request.headers.get("Authorization")
            )
            
            if token_hash is not None:
                token_result = await limiter.check_hash_limit(token_hash=token_hash)
                if not token_result.allowed:
                    return self._rate_limit_response(token_result)
                
                result = token_result
                
            else:
                result = ip_result
                
            # если лимит не превышен
            response = await call_next(request)
            
            response.headers["X-RateLimit-Limit"] = str(result.limit)
            response.headers["X-RateLimit-Remaining"] = str(result.remaining)
            
            return response
        
        except RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            
            if api_config.rate_limit_redis_failure_policy == "fail-closed":
                # при fail-closed статус 503
                return JSONResponse(
                    status_code=503,
                    content={"detail": "Service Unavailable"}
                )
            else:
                # при fail_open пропускаем дальше
                logger.warning("Rate limiting disabled due to Redis failure")
                return await call_next(request)
            
        except Exception as e:
            # Неожиданная ошибка — логируем и пропускаем
            logger.exception(f"Unexpected error in rate limiter: {e}")
            return await call_next(request) 
            
        
    def _get_client_ip(self, request: Request) -> str:
        """
        Получает IP клиента
        
        Позже добавим поддержку X-Forwarded-For
        """
        return request.client.host
        
    def _rate_limit_response(self, result: RateLimitResult) -> JSONResponse:
        """Создает ответ 429 Too Many Requests"""
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"},
            headers={
                "Retry-After": str(api_config.rate_limit_window_size),
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": str(result.remaining)
            }
        ) 