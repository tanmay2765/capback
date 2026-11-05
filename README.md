# Voice Impersonation Detection Backend

Backend for **AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks**.

This repository currently contains **Phase 1 only**: FastAPI application skeleton, configuration, logging, centralized errors, and a health endpoint.

## Architecture (Phase 1)

```text
Client
  → FastAPI (app/main.py)
      → RequestContextMiddleware (request_id, latency)
      → CORS
      → Route adapters (app/api)
      → Structured error handlers
```

Business logic will live in `app/services`. ML models will plug in through `app/ml` adapters. PostgreSQL will persist completed records; Redis will hold short-lived session state. Those layers are reserved as packages and are **not implemented yet**.

### Structure changes vs. the original sketch

- `app/api/router.py` aggregates routes so `main.py` stays thin.
- `app/core/errors.py`, `middleware.py`, `metrics.py`, and `context.py` keep cross-cutting concerns out of routes.
- Later-phase packages (`db`, `services`, `ml`, `websocket`) exist as empty modules so team members can work in known locations without a rewrite.

## Requirements

- Python 3.11+
- pip

PostgreSQL, Redis, FFmpeg, and Docker are **not required** for Phase 1.

## Local run (non-Docker)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

## Implemented in Phase 1

| Area | Status |
| --- | --- |
| FastAPI app factory | Done |
| Configuration via `.env` | Done |
| Structured logging | Done |
| Request ID middleware | Done |
| Centralized error envelope | Done |
| CORS | Done |
| Optional API-key auth hook | Done (disabled by default) |
| `GET /health` | Done |
| OpenAPI `/docs` | Done |
| Lightweight metrics registry | Done (in-process counters) |
| PostgreSQL / Alembic | Phase 2 |
| Redis | Phase 3 |
| Session REST APIs | Phase 4 |
| Audio ingestion | Phase 5 |
| ML interfaces and mocks | Phase 6 |
| Fusion + risk engine | Phase 7 |
| WebSocket streaming | Phase 8 |
| Broader test suite | Phase 9 |
| Docker Compose | Phase 10 |

## Privacy

Phase 1 does not ingest audio. Logging redacts keys such as `audio`, `data`, `password`, and `api_key`. Do not log raw audio in later phases.

## Next phase

Phase 2: PostgreSQL, SQLAlchemy 2.x, Alembic, and session / analysis / risk / alert models.
