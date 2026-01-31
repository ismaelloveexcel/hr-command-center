"""
Application configuration using environment variables.

This module uses pydantic settings to load configuration from environment variables.
All sensitive values should be set via .env file or environment variables.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables can be set in a .env file in the backend directory.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database configuration
    database_url: str = "sqlite:///./hr_portal.db"
    
    # Azure configuration (for future Azure integrations)
    azure_secret_key: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    
    # Twilio configuration (for SMS notifications)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Email configuration (for email notifications)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    
    # Application settings
    app_name: str = "UAE HR Portal API"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"
    
    # Secret key for JWT or other security features
    secret_key: Optional[str] = None
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
