"""Pytest configuration for PitchCube tests."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    return MagicMock(
        PROJECT_NAME="PitchCube Test",
        DEBUG=True,
        JWT_SECRET_KEY="test-secret-key",
        STEPFUN_API_KEY="test-stepfun-key",
        OPENAI_API_KEY="test-openai-key",
    )


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB client."""
    mock_db = MagicMock()
    mock_db.users = MagicMock()
    mock_db.products = MagicMock()
    return mock_db


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def sample_product():
    """Sample product data for tests."""
    return {
        "id": "prod_123",
        "name": "Test Product",
        "description": "A test product for development",
        "features": ["Feature 1", "Feature 2"],
        "github_url": "https://github.com/test/repo",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_user():
    """Sample user data for tests."""
    return {
        "id": "user_123",
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True,
    }
