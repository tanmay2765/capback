"""Centralized application errors and FastAPI exception handlers."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.context import get_request_id
from app.core.logging import get_logger
from app.core.metrics import metrics

logger = get_logger(__name__)


class AppError(Exception):
    """Structured domain error returned as a JSON API error envelope."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class InvalidAudioFormatError(AppError):
    def __init__(self, message: str = "Unsupported audio format.") -> None:
        super().__init__("INVALID_AUDIO_FORMAT", message, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class SessionNotFoundError(AppError):
    def __init__(self, session_id: str) -> None:
        super().__init__(
            "SESSION_NOT_FOUND",
            "Session was not found.",
            status.HTTP_404_NOT_FOUND,
            {"session_id": session_id},
        )


class SessionExpiredError(AppError):
    def __init__(self, session_id: str) -> None:
        super().__init__(
            "SESSION_EXPIRED",
            "Session is no longer active.",
            status.HTTP_410_GONE,
            {"session_id": session_id},
        )


class UploadTooLargeError(AppError):
    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            "UPLOAD_TOO_LARGE",
            "Uploaded file exceeds the configured size limit.",
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            {"max_bytes": max_bytes},
        )


class MalformedMessageError(AppError):
    def __init__(self, message: str = "Malformed message.") -> None:
        super().__init__("MALFORMED_MESSAGE", message, status.HTTP_400_BAD_REQUEST)


class InferenceFailureError(AppError):
    def __init__(self, message: str = "ML inference failed.") -> None:
        super().__init__(
            "INFERENCE_FAILURE",
            message,
            status.HTTP_502_BAD_GATEWAY,
        )


class DependencyFailureError(AppError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message, status.HTTP_503_SERVICE_UNAVAILABLE)


def error_envelope(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": get_request_id(),
        }
    }
    if details:
        payload["error"]["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "application_error",
            extra={"extra_fields": {"code": exc.code, "status_code": exc.status_code}},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("validation_error")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_envelope(
                "VALIDATION_ERROR",
                "Request validation failed.",
                {"errors": exc.errors()},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_envelope(code, str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        metrics.increment("unhandled_exceptions")
        logger.exception("unhandled_exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_envelope("INTERNAL_ERROR", "An unexpected error occurred."),
        )
