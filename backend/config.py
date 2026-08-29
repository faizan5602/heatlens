import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    FORTYGUARD_API_KEY: str = ""
    FORTYGUARD_BASE_URL: str = "https://api.fortyguard.com/v1"
    FORTYGUARD_POLL_INTERVAL_SEC: float = 3.0
    FORTYGUARD_MAX_POLL_ATTEMPTS: int = 30

    GEMINI_API_KEY: str = ""
    GEMINI_API_KEYS: str = ""

    CACHE_DIR: Path = Path("./data/cache")
    CACHE_TTL_SECONDS: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
