import logging

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional, List
from enum import Enum


class Environment(str, Enum):
    """Environment enumeration"""

    LOCAL = "local"
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class AppSettings(BaseSettings):
    """Main application settings"""

    # Environment
    environment: Environment = Field(
        default=Environment.LOCAL, description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # API Configuration
    api_title: str = Field(default="Graph API", description="API title")
    api_description: str = Field(
        default="API for accessing graph database and healthcare data with token authentication",
        description="API description",
    )
    api_version: str = Field(default="1.0.0", description="API version")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload for development")

    # CORS Configuration
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_credentials: bool = Field(
        default=True, description="Allow credentials in CORS"
    )
    cors_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")

    # Documentation
    docs_url: Optional[str] = Field(default="/docs", description="Swagger docs URL")
    redoc_url: Optional[str] = Field(default="/redoc", description="ReDoc URL")
    openapi_url: Optional[str] = Field(
        default="/openapi.json", description="OpenAPI schema URL"
    )

    # Security
    secret_key: str = Field(
        default="development-secret-key", description="Secret key for encryption"
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Token expiration time"
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100, description="Rate limit requests per minute"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )

    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        env = values.get("environment")
        if env == Environment.PROD and (not v or len(v) < 32):
            raise ValueError("Production secret key must be at least 32 characters")
        return v

    @validator("cors_origins")
    def validate_cors_origins(cls, v, values):
        env = values.get("environment")
        if env == Environment.PROD and "*" in v:
            raise ValueError("Wildcard CORS origins not allowed in production")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate that log_level is a valid logging level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of: {valid_levels}")
        return v.upper()

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PROD

    @property
    def is_development(self) -> bool:
        return self.environment in [Environment.LOCAL, Environment.DEV]

    @property
    def log_level_int(self) -> int:
        """Convert string log level to integer"""
        return getattr(logging, self.log_level)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global instance
app_settings = AppSettings()
