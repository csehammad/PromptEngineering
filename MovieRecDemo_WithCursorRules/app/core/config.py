from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    # API Configuration
    api_v1_str: str = Field(default="/api/v1", env="API_V1_STR")
    project_name: str = Field(default="Movie Recommendation Service", env="PROJECT_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    
    # Security Configuration
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("rate_limit_per_minute")
    def validate_rate_limit(cls, v):
        if v < 1:
            raise ValueError("Rate limit must be at least 1 request per minute")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 