from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthCheck(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"api": "ok"}]})

    api: Literal["ok"] = "ok"


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "ok",
                    "service": "Voice Impersonation Detection API",
                    "version": "0.1.0",
                    "environment": "development",
                    "checks": {"api": "ok"},
                }
            ]
        }
    )

    status: Literal["ok"] = Field(description="Overall API process status.")
    service: str
    version: str
    environment: str
    checks: HealthCheck
