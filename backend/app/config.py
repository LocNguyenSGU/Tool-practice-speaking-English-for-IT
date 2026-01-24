from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./test.db"  # Default for testing
    db_pool_size: int = 20
    db_max_overflow: int = 10
    
    # JWT
    secret_key: str = "development-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # TTS
    tts_engine: str = "gtts"
    audio_dir: str = "./audio"
    max_audio_size_mb: int = 5
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100
    
    # Admin
    first_admin_email: str = "admin@example.com"
    first_admin_password: str = "changeme123"
    
    # Server
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    project_name: str = "VI→EN Reflex Trainer API"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
