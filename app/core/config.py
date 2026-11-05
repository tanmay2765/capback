"""Environment-driven application settings.

Later phases consume audio, fusion, and risk fields. Phase 1 only uses
API, CORS, logging, and authentication-related settings at runtime.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Voice Impersonation Detection API"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    log_level: str = "INFO"
    log_json: bool = False

    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    cors_allow_credentials: bool = True

    api_key_header: str = "X-API-Key"
    api_keys: str = ""
    auth_enabled: bool = False

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "capstone"
    postgres_password: str = "capstone"
    postgres_db: str = "voice_detection"
    database_url: str | None = None

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_url: str | None = None
    redis_session_ttl_seconds: int = 3600
    redis_audio_buffer_ttl_seconds: int = 120

    max_upload_bytes: int = 25 * 1024 * 1024
    audio_target_sample_rate: int = 16000
    audio_target_channels: int = 1
    audio_chunk_duration_ms: int = 1000
    audio_max_duration_seconds: int = 300

    synthetic_weight: float = Field(default=0.4, ge=0.0)
    prosody_weight: float = Field(default=0.2, ge=0.0)
    speaker_weight: float = Field(default=0.4, ge=0.0)

    low_max: int = Field(default=39, ge=0, le=100)
    medium_max: int = Field(default=69, ge=0, le=100)
    high_min: int = Field(default=70, ge=0, le=100)

    ml_provider: Literal["mock", "real"] = "mock"

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def api_key_set(self) -> set[str]:
        return {key.strip() for key in self.api_keys.split(",") if key.strip()}

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_connection_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
