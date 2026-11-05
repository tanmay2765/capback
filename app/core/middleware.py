"""ASGI middleware for request IDs and latency. Avoid BaseHTTPMiddleware so
FastAPI exception handlers still receive unhandled errors.
"""

from __future__ import annotations

import time
from typing import Any

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.context import new_request_id, set_request_id, set_session_id
from app.core.errors import error_envelope
from app.core.logging import get_logger
from app.core.metrics import metrics

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        header_map = {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in scope.get("headers", [])}
        request_id = header_map.get("x-request-id") or new_request_id()
        set_request_id(request_id)
        set_session_id(_session_id_from_path(scope.get("path", "")))

        started = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                headers = MutableHeaders(raw=message.setdefault("headers", []))
                headers[REQUEST_ID_HEADER] = request_id
                headers["X-Response-Time-ms"] = str(elapsed_ms)
                logger.info(
                    "http_request",
                    extra={
                        "extra_fields": {
                            "method": scope.get("method"),
                            "path": scope.get("path"),
                            "status_code": status_code,
                            "latency_ms": elapsed_ms,
                        }
                    },
                )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
            metrics.increment("http_requests")
        except Exception:
            metrics.increment("http_errors")
            metrics.increment("unhandled_exceptions")
            logger.exception("unhandled_exception")
            response = JSONResponse(
                status_code=500,
                content=error_envelope("INTERNAL_ERROR", "An unexpected error occurred."),
            )
            await response(scope, receive, send_wrapper)


def _session_id_from_path(path: str) -> str | None:
    parts = path.split("/")
    if "sessions" in parts:
        index = parts.index("sessions")
        if index + 1 < len(parts) and parts[index + 1]:
            return parts[index + 1]
    return None
