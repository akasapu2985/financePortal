# Jasnah Decision: Phase 1 smoke test uses mocked backend dependencies

- Recorded: 2026-05-24T12:47:40-07:00
- Requested by: Giakas

## Decision

Implement the Phase 1 smoke test as a pytest integration suite that exercises the FastAPI app with `TestClient`, a mocked asyncpg pool, and mocked collector dependencies instead of requiring Docker-backed Postgres or live market/news APIs.

## Rationale

This keeps the verification command runnable in a clean developer environment and in CI without external infrastructure. It still validates the API contracts, seeded-data responses, and collector orchestration paths needed for Phase 1 production-track confidence.

## Consequences

- The smoke test is fast and deterministic.
- Live container wiring remains covered by the documented startup flow rather than this automated smoke suite.
