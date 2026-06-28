import os
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    APP_NAME: str = "Analytics Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - mặc định SQLite cho local dev; đặt DATABASE_URL trong .env cho PostgreSQL
    DATABASE_URL: str = "sqlite:///./analytics.db"
    
    # Service URLs — override in .env; defaults point to localhost for dev
    IOT_SERVICE_URL: str = "http://localhost:8001"
    CAMERA_SERVICE_URL: str = "http://localhost:8002"
    ACCESS_GATE_URL: str = "http://localhost:8003"
    CORE_BUSINESS_URL: str = "http://localhost:8004"
    
    # Data retention (days)
    DATA_RETENTION_DAYS: int = 90
    
    # Batch processing
    BATCH_SIZE: int = 100
    PROCESSING_INTERVAL_SECONDS: int = 300  # 5 minutes

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> bool:
        """Coerce DEBUG from a few common env formats."""
        if isinstance(value, bool):
            return value
        if value is None:
            return False

        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "on", "debug"}:
            return True
        if text in {"0", "false", "no", "off", "release", "prod", "production"}:
            return False

        return False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # bỏ qua các biến env không khai báo trong Settings


settings = Settings()
