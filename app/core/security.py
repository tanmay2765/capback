"""Baseline security helpers.

Authentication is intentionally simple: an optional shared API key that
can later be replaced with JWT/OAuth without changing route signatures.
"""

from __future__ import annotations

from fastapi import Request, Security
from fastapi.security import APIKeyHeader

from app.core.config import Settings
from app.core.errors import AppError

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(settings: Settings, provided_key: str | None) -> None:
    if not settings.auth_enabled:
        return
    if not provided_key or provided_key not in settings.api_key_set:
        raise AppError(
            "UNAUTHORIZED",
            "A valid API key is required.",
            status_code=401,
        )


async def get_authenticated_request(
    request: Request,
    api_key: str | None = Security(api_key_header),
) -> Request:
    require_api_key(request.app.state.settings, api_key)
    return request
