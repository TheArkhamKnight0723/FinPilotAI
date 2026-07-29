"""
FinPilot AI – Application Settings
Uses pydantic-settings to load and validate environment variables.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object. All values are loaded from environment
    variables or the .env file in the backend root directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    APP_NAME: str = "FinPilot AI"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Server ────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Security ──────────────────────────────────────────────
    SECRET_KEY: str = "changeme-insecure-default"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ── Logging ───────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Returns a cached singleton instance of Settings."""
    return Settings()
