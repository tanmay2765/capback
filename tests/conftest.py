from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import AppError
from app.core.metrics import metrics
from app.main import create_app


class EchoPayload(BaseModel):
    name: str


@pytest.fixture
def settings() -> Settings:
    return Settings(
        environment="test",
        debug=True,
        log_level="WARNING",
        cors_origins="http://localhost:3000",
        auth_enabled=False,
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    application = create_app(settings)

    @application.get("/__test/app-error")
    async def raise_app_error() -> None:
        raise AppError("INVALID_AUDIO_FORMAT", "Unsupported audio format.")

    @application.get("/__test/crash")
    async def raise_crash() -> None:
        raise RuntimeError("boom-secret")

    @application.post("/__test/echo")
    async def echo(payload: EchoPayload) -> EchoPayload:
        return payload

    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    metrics.reset()
    with TestClient(app) as test_client:
        yield test_client
    metrics.reset()
