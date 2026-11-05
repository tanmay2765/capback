"""Request-scoped context available to logging and error handlers."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional
from uuid import uuid4

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
session_id_ctx: ContextVar[Optional[str]] = ContextVar("session_id", default=None)


def new_request_id() -> str:
    return str(uuid4())


def get_request_id() -> str:
    return request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    request_id_ctx.set(request_id)


def get_session_id() -> Optional[str]:
    return session_id_ctx.get()


def set_session_id(session_id: Optional[str]) -> None:
    session_id_ctx.set(session_id)
