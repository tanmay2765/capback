from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorBody(BaseModel):
    code: str = Field(examples=["INVALID_AUDIO_FORMAT"])
    message: str = Field(examples=["Unsupported audio format."])
    request_id: str = Field(examples=["2c7c3b2e-3f4a-4d1c-9e1a-1a2b3c4d5e6f"])
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": {
                        "code": "INVALID_AUDIO_FORMAT",
                        "message": "Unsupported audio format.",
                        "request_id": "2c7c3b2e-3f4a-4d1c-9e1a-1a2b3c4d5e6f",
                    }
                }
            ]
        }
    )

    error: ErrorBody
