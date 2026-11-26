from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.interfaces.api.config import api_config

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
        
        if not api_config.rate_limit_enabled:
            return await call_next(request)
        
        # проверка лимитов
        
        response = await call_next(request)
        return response
        