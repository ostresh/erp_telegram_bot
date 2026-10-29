from httpx import AsyncClient
import pytest

PROTECTED_ENDPOINT = f"/api/v1/user/profile"

async def test_with_valid_token(client: AsyncClient, auth_headers):
    response = await client.get(PROTECTED_ENDPOINT, headers=auth_headers)
    assert response.status_code == 200
    
async def test_no_token_returns_401(client: AsyncClient):
    response = await client.get(PROTECTED_ENDPOINT)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json() == {"detail": "Unauthorized"}
    
async def test_wrong_token_returns_401(client: AsyncClient):
    response = await client.get(
        PROTECTED_ENDPOINT,
        headers={"Authorization": "Bearer wrong-token-value"}
    )
    assert response.status_code == 401
    
async def test_wrong_scheme_returns_401(client: AsyncClient, auth_headers):
    token = auth_headers["Authorization"].removeprefix("Bearer ")
    response = await client.get(
        PROTECTED_ENDPOINT,
        headers={"Authorization": f"Basic {token}"}
    )
    assert response.status_code == 401
    
async def test_token_in_query_returns_401(client: AsyncClient, auth_headers):
    token = auth_headers["Authorization"].removeprefix("Bearer ")
    response = await client.get(f"{PROTECTED_ENDPOINT}?token={token}")
    assert response.status_code == 401
    
async def test_too_long_token_returns_401(client: AsyncClient):
    response = await client.get(
        PROTECTED_ENDPOINT,
        headers={"Authorization": f"Bearer {'x * 1000'}"}
    )
    assert response.status_code == 401
    
async def test_all_401_bodies_are_identical(client):
    responses = await _gather_responses(client)
    for response in responses:
        assert response.status_code == 401
    bodies = {response.text for response in responses}
    assert len(bodies) == 1
    
async def _gather_responses(client):
    """Собирает несколько 401-ответов для сравнения."""
    return [
        await client.get(PROTECTED_ENDPOINT),
        await client.get(PROTECTED_ENDPOINT, headers={"Authorization": "Bearer wrong"}),
        await client.get(PROTECTED_ENDPOINT, headers={"Authorization": "Basic wrong"}),
    ]