import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.utils.logger import setup_logger
from .dependencies.redis import close_redis_client, init_redis_client
from .domains import ROUTERS

from .config import api_config

# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)

logger.info("Конфигурация аутентификации API принята, mode=%s", api_config.auth_mode)

enable_docs = api_config.api_docs_enabled and not api_config.is_production

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan контекст для инициализации и очистки ресурсов.
    """
    
    # Startup
    logger.info("Initializing Redis client...")
    await init_redis_client()
    logger.info("Redis client initialized")
    
    yield
    
    # Shutdown
    logger.info("Closing Redis client...")
    await close_redis_client()
    logger.info("Redis client closed")

app = FastAPI(
    title="ERP API",
    version="0.1.0",
    docs_url="/docs" if enable_docs else None,
    redoc_url="/redoc" if enable_docs else None,
    openapi_url=f"{api_config.api_prefix}/openapi.json" if enable_docs else None,
    lifespan=lifespan
)

for config in ROUTERS:
    app.include_router(
        router=config.router,
        prefix=f"{api_config.api_prefix}{config.prefix}",
        tags=config.tags,
    )