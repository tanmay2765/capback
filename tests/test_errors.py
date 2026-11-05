from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.errors import error_envelope
from app.core.context import set_request_id


def test_app_error_uses_structured_envelope(client: TestClient) -> None:
    response = client.get("/__test/app-error")
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "INVALID_AUDIO_FORMAT"
    assert body["error"]["message"] == "Unsupported audio format."
    assert body["error"]["request_id"]


def test_validation_error_envelope(client: TestClient) -> None:
    response = client.post("/__test/echo", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in body["error"]


def test_not_found_envelope(client: TestClient) -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_unhandled_error_does_not_leak_exception(client: TestClient) -> None:
    response = client.get("/__test/crash")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert body["error"]["message"] == "An unexpected error occurred."
    assert "boom-secret" not in str(body)


def test_error_envelope_includes_context() -> None:
    set_request_id("fixed-id")
    payload = error_envelope("SESSION_NOT_FOUND", "Session was not found.")
    assert payload["error"]["request_id"] == "fixed-id"
    assert payload["error"]["code"] == "SESSION_NOT_FOUND"
