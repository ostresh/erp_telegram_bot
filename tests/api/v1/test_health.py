import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

pytestmark = pytest.mark.usefixtures("override_infra")

LIVE = f"/api/v1/health/live"
READY = "/api/v1/health/ready"
DETAILED = "/api/v1/health/detailed"

async def test_live_returns_ok(client: AsyncClient):
    """Liveness не требует токена"""
    
    response = await client.get(LIVE)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
async def test_live_does_not_leat_internals(client: AsyncClient):
    """В ответе ничего, кроме статуса"""
    response = await client.get(LIVE)
    assert set(response.json().keys()) == {"status"}
    
@pytest.mark.asyncio
async def test_ready_requires_auth(client: AsyncClient):
    """Readiness требует авторизации."""
    response = await client.get(READY)
    assert response.status_code == 401
    
async def test_ready_with_valid_token_and_dependencies_ok(
    client: AsyncClient,
    auth_headers,
    mock_uow,
    mock_redis,
):
    """Readiness возвращает ok если все зависимости доступны."""
    mock_redis.ping.return_value = True

    response = await client.get(READY, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
async def test_ready_returns_503_when_postgres_unavailable(
    client: AsyncClient,
    auth_headers,
    mock_uow,
    mock_redis,
):
    """Readiness возвращает 503 если PostgreSQL недоступен."""
    mock_uow.execute_side_effect = SQLAlchemyError("Connection failed")
    mock_redis.ping.return_value = True
    
    response = await client.get(READY, headers=auth_headers)
    
    assert response.status_code == 503
    assert response.json() == {"detail": "Service unavailable"}
    
async def test_ready_returns_503_when_redis_unavailable(
    client: AsyncClient,
    auth_headers,
    mock_uow,
    mock_redis,
):
    """Readiness возвращает 503 если PostgreSQL недоступен."""
    mock_redis.ping.side_effect = ConnectionError("Redis connection failed")
    
    response = await client.get(READY, headers=auth_headers)
    
    assert response.status_code == 503
    assert response.json() == {"detail": "Service unavailable"}
    
async def test_ready_does_not_leak_error_details(
    client: AsyncClient,
    auth_headers,
    mock_uow,
    mock_redis
):
    """Readiness не раскрывает детали ошибок"""
    mock_uow.execute_side_effect = SQLAlchemyError("Connection failed")
    mock_redis.ping.side_effect = ConnectionError("Redis connection failed")
    
    response = await client.get(READY, headers=auth_headers)
        
    assert response.status_code == 503
    assert "message" not in response.text
    assert set(response.json().keys()) == {"detail"}
    
