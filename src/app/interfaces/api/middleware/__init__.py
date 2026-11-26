from starlette.middleware.base import BaseHTTPMiddleware

from .rate_limiting import RateLimitMiddleware

MIDDLEWARES: list[type[BaseHTTPMiddleware]] = [
    RateLimitMiddleware
]

__all__ = [
    'MIDDLEWARES'
]