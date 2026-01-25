"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    PROJECT_NAME: str = "Dash Intelligence"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Supabase Configuration
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    
    # Security (we can add JWT settings here later)
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
