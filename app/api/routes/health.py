from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import get_settings_dep
from app.core.config import Settings
from app.schemas.errors import ErrorResponse
from app.schemas.health import HealthCheck, HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Backend health",
    responses={500: {"model": ErrorResponse, "description": "Unexpected server error"}},
)
async def health(settings: Settings = Depends(get_settings_dep)) -> HealthResponse:
    """Return process-level health for the API.

    Database and Redis probes are added when those dependencies are wired
    in later phases. This endpoint stays cheap and does not log audio.
    """
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        checks=HealthCheck(api="ok"),
    )
