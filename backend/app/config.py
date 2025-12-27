"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "AI Stock Intelligence Platform"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/dash"
    
    # Auth
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Yahoo Finance
    yahoo_rate_limit_delay: float = 0.5  # seconds between requests
    
    # Snapshot settings
    snapshot_lookback_days: int = 90  # days of price data for snapshot
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
