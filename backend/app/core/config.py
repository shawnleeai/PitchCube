"""
Application Configuration
All sensitive configuration should be loaded from environment variables.
NEVER hardcode API keys or secrets in this file.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

# 确定 .env 文件路径
# 优先从后端目录加载，如果找不到则使用当前目录
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Info
    PROJECT_NAME: str = "PitchCube API"
    PROJECT_DESCRIPTION: str = "AI-driven路演展示智能魔方平台 API"
    VERSION: str = "1.0.0"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True  # 启用调试模式以便可以访问 API 文档

    # Security
    SECRET_KEY: str = "change-this-in-production"
    JWT_SECRET_KEY: str = "change-this-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Demo Account (for testing only, change in production!)
    DEMO_EMAIL: str = "demo@example.com"
    DEMO_PASSWORD: str = "password"
    DEMO_USERNAME: str = "Demo User"

    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"

    @field_validator("CORS_ORIGINS_STR")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        return v

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "pitchcube"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"

    # Generated Files
    GENERATED_FILES_EXPIRY_HOURS: int = 24 * 7  # 7 days

    # =============================================================================
    # AI 服务 API 密钥 (可选，用于增强功能)
    # =============================================================================

    # StepFun (阶跃星辰) - 语音合成 + 大语言模型
    STEPFUN_API_KEY: Optional[str] = None
    STEPFUN_TTS_MODEL: str = "step-tts-mini"  # 或 step-tts-2
    STEPFUN_LLM_MODEL: str = "step-1-8k"  # 大语言模型

    # Minimax (稀宇科技) - 语音合成 + 大语言模型
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_GROUP_ID: Optional[str] = None
    MINIMAX_LLM_MODEL: str = "abab6.5s-chat"  # 或 abab6.5-chat, abab6-chat
    MINIMAX_TTS_MODEL: str = "speech-01-turbo"  # TTS模型

    # OpenAI - 文案生成、视频脚本、DALL-E图像
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # 或 gpt-4o

    # Stability AI - 海报图像生成/增强
    STABILITY_API_KEY: Optional[str] = None
    STABILITY_MODEL: str = "stable-diffusion-xl-1024-v1-0"

    # Replicate - 视频生成
    REPLICATE_API_TOKEN: Optional[str] = None

    # Runway ML - 视频编辑
    RUNWAY_API_KEY: Optional[str] = None

    # Azure Speech Services - 备选语音合成
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # =============================================================================
    # Email Configuration
    # =============================================================================

    # Resend API (推荐，免费额度：每天100封)
    RESEND_API_KEY: Optional[str] = None
    RESEND_FROM_EMAIL: str = "noreply@pitchcube.ai"

    # SMTP Configuration (备用)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "PitchCube"
    SMTP_USE_TLS: bool = True

    # Frontend URL (用于邮件中的链接)
    FRONTEND_URL: str = "http://localhost:3000"

    # =============================================================================
    # 多媒体处理配置
    # =============================================================================

    # FFmpeg 路径 (用于视频处理)
    FFMPEG_PATH: str = "ffmpeg"

    # 视频生成配置
    VIDEO_DEFAULT_RESOLUTION: str = "1080p"  # 720p, 1080p, 4k
    VIDEO_DEFAULT_FPS: int = 30
    VIDEO_MAX_DURATION_SECONDS: int = 300  # 最大5分钟

    class Config:
        # 从后端目录加载 .env 文件
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in env file

    def is_ai_service_configured(self, service: str) -> bool:
        """Check if an AI service is configured."""
        service_keys = {
            "openai": self.OPENAI_API_KEY,
            "stability": self.STABILITY_API_KEY,
            "azure_speech": self.AZURE_SPEECH_KEY and self.AZURE_SPEECH_REGION,
            "stepfun": self.STEPFUN_API_KEY,
            "stepfun_tts": self.STEPFUN_API_KEY,
            "stepfun_llm": self.STEPFUN_API_KEY,
            "minimax": self.MINIMAX_API_KEY and self.MINIMAX_GROUP_ID,
            "minimax_tts": self.MINIMAX_API_KEY and self.MINIMAX_GROUP_ID,
            "minimax_llm": self.MINIMAX_API_KEY and self.MINIMAX_GROUP_ID,
            "replicate": self.REPLICATE_API_TOKEN,
            "runway": self.RUNWAY_API_KEY,
        }
        return bool(service_keys.get(service.lower()))

    def get_ai_services_status(self) -> dict:
        """获取所有 AI 服务的配置状态"""
        return {
            "stepfun_tts": self.is_ai_service_configured("stepfun_tts"),
            "stepfun_llm": self.is_ai_service_configured("stepfun_llm"),
            "minimax_tts": self.is_ai_service_configured("minimax_tts"),
            "minimax_llm": self.is_ai_service_configured("minimax_llm"),
            "openai": self.is_ai_service_configured("openai"),
            "stability": self.is_ai_service_configured("stability"),
            "replicate": self.is_ai_service_configured("replicate"),
            "runway": self.is_ai_service_configured("runway"),
            "azure_speech": self.is_ai_service_configured("azure_speech"),
        }


# Global settings instance
settings = Settings()
