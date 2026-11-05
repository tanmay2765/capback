from __future__ import annotations

from app.core.config import Settings
from app.core.logging import SENSITIVE_KEYS, _redact
from app.core.security import require_api_key
from app.core.errors import AppError


def test_cors_origin_list_parses_csv() -> None:
    settings = Settings(cors_origins="http://localhost:3000, http://localhost:5173")
    assert settings.cors_origin_list == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


def test_database_and_redis_urls_are_derived() -> None:
    settings = Settings(
        postgres_user="capstone",
        postgres_password="secret",
        postgres_host="db",
        postgres_port=5432,
        postgres_db="voice_detection",
        redis_host="cache",
        redis_port=6379,
        redis_db=1,
    )
    assert settings.sqlalchemy_database_url.startswith("postgresql+asyncpg://")
    assert "voice_detection" in settings.sqlalchemy_database_url
    assert settings.redis_connection_url == "redis://cache:6379/1"


def test_fusion_weights_and_risk_thresholds_load() -> None:
    settings = Settings(
        synthetic_weight=0.5,
        prosody_weight=0.2,
        speaker_weight=0.3,
        low_max=30,
        medium_max=60,
        high_min=61,
    )
    assert settings.synthetic_weight + settings.prosody_weight + settings.speaker_weight == 1.0
    assert settings.low_max < settings.medium_max < settings.high_min or settings.high_min == settings.medium_max + 1


def test_auth_is_disabled_by_default() -> None:
    settings = Settings()
    require_api_key(settings, provided_key=None)


def test_auth_rejects_missing_key_when_enabled() -> None:
    settings = Settings(auth_enabled=True, api_keys="dev-key")
    try:
        require_api_key(settings, provided_key=None)
        raise AssertionError("expected AppError")
    except AppError as exc:
        assert exc.code == "UNAUTHORIZED"


def test_logging_redacts_sensitive_fields() -> None:
    redacted = _redact({"session_id": "abc", "audio": b"pcm", "api_key": "secret"})
    assert redacted["session_id"] == "abc"
    assert redacted["audio"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert "audio" in SENSITIVE_KEYS
