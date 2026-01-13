"""
============================================
SAHAYAK AI - Core Configuration
============================================

📌 WHAT IS THIS FILE?
This file manages all environment variables and application settings.
We use Pydantic Settings for type-safe configuration management.

🎓 LEARNING POINT:
- Pydantic Settings automatically reads from environment variables
- It validates types and provides defaults
- It's the modern, Pythonic way to handle configuration
============================================
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    How it works:
    1. Pydantic looks for environment variables matching field names
    2. Field names are case-insensitive (APP_NAME matches app_name)
    3. Nested classes with model_config define behavior
    """
    
    # --------------------------------------------
    # Application Settings
    # --------------------------------------------
    app_name: str = "SAHAYAK AI"
    app_env: str = "development"
    debug: bool = True
    api_version: str = "v1"
    
    # --------------------------------------------
    # Security Settings
    # --------------------------------------------
    secret_key: str = "change-this-in-production-use-secrets-token"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # --------------------------------------------
    # MongoDB Settings
    # --------------------------------------------
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "sahayak_ai"
    
    # --------------------------------------------
    # Gemini AI Settings
    # --------------------------------------------
    gemini_api_key: str = ""
    
    # --------------------------------------------
    # CORS Settings
    # --------------------------------------------
    # In production, set CORS_ORIGINS env var to: ["*"] or your specific domains
    cors_origins: List[str] = [
        "*",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # --------------------------------------------
    # Logging
    # --------------------------------------------
    log_level: str = "INFO"
    
    class Config:
        """
        Pydantic configuration for settings.
        
        env_file: Path to .env file
        env_file_encoding: File encoding
        case_sensitive: Whether env var names are case-sensitive
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    🎓 LEARNING POINT:
    @lru_cache() ensures we only create one Settings instance.
    This is efficient because reading .env file is done once.
    
    Returns:
        Settings: The application settings
    """
    return Settings()


# Export a convenient reference
settings = get_settings()
