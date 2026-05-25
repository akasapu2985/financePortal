# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Multiple data sources (APIs, scrapers, feeds), local PostgreSQL, React dashboard, MCP server. Many potential failure modes: API outages, malformed data, rate limits, stale caches.
- **Stack:** Python (pytest for backend), TypeScript (Vitest for frontend), PostgreSQL
- **Key responsibilities:** Test strategy, unit/integration/load tests, edge case hunting, quality gates
- **Created:** 2026-05-24

## Learnings

- Phase 1 backend verification can run through `backend/tests/integration/test_phase1_smoke.py` using FastAPI `TestClient`, a mocked asyncpg pool, and collector doubles instead of Docker-backed Postgres.

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-24T19:51:02Z — Team update: Kaladin backend ready, Navani schema ready. Phase 1 smoke test dependencies satisfied. Ready to begin test implementation.
- 2026-05-24T16:03:34-07:00 — Verification baseline: backend pytest and Ruff pass from `backend/`, frontend TypeScript/lint/build pass from `frontend/`, but there are no Vitest specs, no Playwright tests, and alert functionality is only represented in schema (`backend/migrations/002_news_alerts.sql`) rather than runtime API/UI code.
