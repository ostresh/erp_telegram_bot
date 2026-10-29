from fastapi import APIRouter, Depends, HTTPException, status
from redis import Redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.utils.logger import setup_logger
from app.core.db.unit_of_work import UnitOfWork
from app.interfaces.api.config import api_config
from app.interfaces.api.dependencies.auth import get_current_identity
from app.interfaces.api.dependencies.db import get_uow
from app.interfaces.api.dependencies.redis import get_redis
 
from .schemas import ComponentStatus, DetailedHealthResponse, HealthResponse

import logging
setup_logger()
logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

@router.get(
    "/live",
    response_model=HealthResponse,
    summary="Health Liveness"
)
async def live() -> HealthResponse:
    """
    Liveness проба, жив ли процесс
    
    Не проверяет БД, Redis и внешние сервисы
    Публичный, без авторазиции
    """
    return HealthResponse(status="ok")

@router.get(
    "/ready",
    response_model=HealthResponse,
    summary="Health Readiness"
)
async def ready(
    _identity=Depends(get_current_identity),
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis)
    ) -> HealthResponse:
    """
    Readiness проба, готов ли процесс принимать трафик
    Защищна авторизацией
    """
    async with uow() as session:
        try:
            await session.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            logger.error("PostgreSQL readiness check failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable"
            )
            
    try:
        await redis.ping()
    except Exception as e:
        logger.error("Redis readiness check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )
        
    return HealthResponse(status="ok")

@router.get(
    "/detailed",
    response_model=DetailedHealthResponse,
    summary="Detailed Health"
)
async def detailed(
    _identity=Depends(get_current_identity),
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis)
) -> DetailedHealthResponse:
    """
    Детальная проверка состояния всех компонентов системы
    
    Возвращает статус каждого компонента отдельно.
    Защищена авторизацией
    """
    overall_status = "ok"
    
    postgres_status = "ok"
    postgres_message = None
    async with uow() as session:
        try:
            await session.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            postgres_status = "error"
            postgres_message = "Database unavailable"
            logger.error("PostgreSQL health check failed: %s", e)
            overall_status = "error"
            
    redis_status = "ok"
    redis_message = None
    try:
        await redis.ping()
    except Exception as e:
        redis_status = "error"
        redis_message = "Redis unavailable"
        logger.error("Redis health check failed: %s", e)
        overall_status = "error"
        
    return DetailedHealthResponse(
        status=overall_status,
        postgres=ComponentStatus(
            status=postgres_status,
            message=postgres_message
        ),
        redis=ComponentStatus(
            status=redis_status,
            message=redis_message
        ),
    )
    

        