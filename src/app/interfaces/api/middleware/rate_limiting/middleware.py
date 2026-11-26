from redis import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.interfaces.api.config import api_config
from app.interfaces.api.dependencies.redis import get_redis
from .limiter import RateLimiter

import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware для ограничения количества запросов
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Обработка запроса
        
        Пока просто пропускаем все запросы
        Позже здесь будет проверка лимитов
        """
        
        try:
        
            if not api_config.rate_limit_enabled:
                return await call_next(request)
            
            redis = await get_redis()
            limiter = RateLimiter(redis)
            
            ip = self._get_client_ip(request)
            
            # проверка лимита по ip
            result = await limiter.check_ip_limit(
                ip=ip,
                limit=api_config.rate_limit_ip_limit,
                window_size=api_config.rate_limit_window_size
            )
            
            # если нет разрешения (лимит превышен)
            if not result.allowed:
                retry_after = api_config.rate_limit_window_size
                return JSONResponse(
                    status_code=429,
                    content={"detail" : "Too Many Requests"},
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(result.limit),
                        "X-RateLimit-Ramaining": str(result.remaining)
                    }
                )
                
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
        
        