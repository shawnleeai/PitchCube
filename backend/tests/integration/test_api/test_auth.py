"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint returns project info."""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_health_check(self, async_client: AsyncClient):
        """Test API health check endpoint."""
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(self, async_client: AsyncClient):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User",
        }
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code in [201, 200]
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]

    @pytest.mark.asyncio
    async def test_login_with_json(self, async_client: AsyncClient):
        """Test JSON login endpoint."""
        login_data = {"email": "demo@example.com", "password": "password"}
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {"email": "wrong@example.com", "password": "wrongpassword"}
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
