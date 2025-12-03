"""
Configuration module for OCR KTP application.

This module handles all application configuration using pydantic-settings
for type-safe environment variable loading and validation.
"""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    DEFAULT_ALLOWED_EXTENSIONS,
    DEFAULT_MAX_FILE_SIZE_MB,
)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        gemini_api_key: API key for Google Gemini service.
        max_file_size_mb: Maximum allowed file size in megabytes.
        allowed_extensions: Tuple of allowed file extensions.
        api_title: Title of the API for documentation.
        api_description: Description of the API.
        api_version: Current API version.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
    # Gemini API Configuration
    gemini_api_key: Annotated[
        str,
        Field(default="", description="Google Gemini API Key")
    ]
    
    # File Upload Configuration
    max_file_size_mb: Annotated[
        int,
        Field(
            default=DEFAULT_MAX_FILE_SIZE_MB,
            ge=1,
            le=50,
            description="Maximum file size in MB"
        )
    ]
    
    # Store as string internally, convert via property
    allowed_extensions_str: Annotated[
        str,
        Field(
            default="jpg,jpeg,png,webp",
            alias="ALLOWED_EXTENSIONS",
            description="Comma-separated allowed file extensions"
        )
    ]
    
    # API Configuration (read-only, not from env)
    api_title: str = API_TITLE
    api_description: str = API_DESCRIPTION
    api_version: str = API_VERSION
    
    @property
    def allowed_extensions(self) -> tuple[str, ...]:
        """Parse extensions from comma-separated string."""
        if not self.allowed_extensions_str:
            return DEFAULT_ALLOWED_EXTENSIONS
        return tuple(ext.strip().lower() for ext in self.allowed_extensions_str.split(","))
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def is_gemini_configured(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.gemini_api_key and self.gemini_api_key.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings singleton.
    
    Note:
        Uses lru_cache to ensure only one settings instance is created.
    """
    return Settings()
