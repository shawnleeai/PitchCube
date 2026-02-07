"""Unit tests for configuration module."""

import pytest
from app.core.config import Settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        assert settings.PROJECT_NAME == "PitchCube API"
        assert settings.VERSION == "1.0.0"
        assert settings.DEBUG is True

    def test_cors_origins_parsing(self):
        """Test CORS origins are parsed correctly."""
        settings = Settings()
        origins = settings.CORS_ORIGINS
        assert isinstance(origins, list)
        assert len(origins) > 0

    def test_ai_service_configuration_check(self):
        """Test AI service configuration detection."""
        settings = Settings()

        # Without API keys
        assert settings.is_ai_service_configured("openai") is False
        assert settings.is_ai_service_configured("stepfun") is False

        # Check status dict
        status = settings.get_ai_services_status()
        assert isinstance(status, dict)
        assert "openai" in status
        assert "stepfun" in status


class TestEnvironmentVariables:
    """Test environment variable loading."""

    def test_jwt_configuration(self):
        """Test JWT settings."""
        settings = Settings()
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0

    def test_database_urls(self):
        """Test database configuration."""
        settings = Settings()
        assert "mongodb" in settings.MONGODB_URL
        assert "redis" in settings.REDIS_URL
