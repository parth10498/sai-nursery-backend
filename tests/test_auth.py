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
    data = response.json()
    assert data["success"] is False
    assert "message" in data
    assert "detail" in data


@pytest.mark.anyio
async def test_validation_error_format(async_client: AsyncClient):
    # Send empty body to login
    response = await async_client.post("/api/v1/auth/login/json", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "Validation error:" in data["message"]
    assert isinstance(data["errors"], list)
    assert len(data["errors"]) > 0
    assert "field" in data["errors"][0]
    assert "message" in data["errors"][0]
