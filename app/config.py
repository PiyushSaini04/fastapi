"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central settings object.

    Values are read from the environment / .env file at startup.
    Sensitive fields (SECRET_KEY, DATABASE_URL) should never be
    hard-coded; set them in the .env file.
    """

    DATABASE_URL: str = "sqlite://./dev.db"
    SECRET_KEY: str = "change-me-in-production"
    APP_ENV: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application settings (reads .env once)."""
    return Settings()
