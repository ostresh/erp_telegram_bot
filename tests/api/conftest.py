import os
from unittest.mock import AsyncMock

# Наша конфигурация безопасности (api_config) создаётся в момент импорта
# модуля config.py — это и есть механизм fail-closed. Значит, переменные
# окружения должны быть установлены РАНЬШЕ, чем тестовые модули импортируют
# приложение.

TEST_TOKEN = "test-api-token-" + "x" * 32

os.environ["ENVIRONMENT"] = "development"
os.environ["API_TOKEN"] = TEST_TOKEN
os.environ.pop("API_TOKEN_SHA256", None)

from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from app.interfaces.api.dependencies.redis import get_redis
from app.interfaces.api.dependencies.db import get_uow
from app.interfaces.api.main import app

@pytest_asyncio.fixture
async def client():
    """Асинхронный HTTP клиент для тестов"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    """Headers с Authorization"""
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


@pytest.fixture()
def mock_redis():
    """
    Фикстура для подмены зависимости get_redis на фейковый клиент.
    
    Использование:
        def test_something(client, mock_redis):
            mock_redis.ping.return_value = True
            response = await client.get("/ready")
    """
    
    fake_redis = AsyncMock()
    
    return fake_redis

@pytest.fixture()
def mock_uow():
    """
    Фикстура для подмены зависимости get_uow на фейковый UnitOfWork.
    
    Использование:
        def test_something(client, mock_uow):
            response = await client.get("/ready")
    """
    from contextlib import asynccontextmanager
    
    class FakeUnitOfWork:
        def __init__(self):
            self.execute_side_effect = None
            
        @asynccontextmanager
        async def __call__(self):
            session = AsyncMock()
            
            if self.execute_side_effect is None:
                session.execute.return_value = None
            else:
                session.execute.side_effect = self.execute_side_effect
            
            yield session
            
    fake_uow = FakeUnitOfWork()
    
    return fake_uow

@pytest.fixture
def override_infra(mock_redis, mock_uow):
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_uow] = lambda: mock_uow
    yield
    app.dependency_overrides.pop(get_redis, None)
    app.dependency_overrides.pop(get_uow, None)