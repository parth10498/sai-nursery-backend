import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Sai Nursery API" in data["app"]


@pytest.mark.anyio
async def test_unauthorized_me_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
