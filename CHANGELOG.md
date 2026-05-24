# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Watchlist CRUD backend support via `backend/src/api/routes/watchlists.py`, including request/response validation, async membership mutation endpoints, and persisted schema migration `backend/src/db/migrations/003_watchlists.sql`
- Tailwind dark-theme token plumbing in `frontend/` with a Tailwind theme extension, CSS custom properties in `frontend/src/styles/tokens.css`, shared status/surface classes, and a themed shell in `frontend/src/App.tsx`
- Scaffolded `frontend/` with a Vite + React + TypeScript app, React Query provider wiring, `/api` dev proxy, strict TypeScript path aliases, and initial source folders for components, services, hooks, and types
- Phase 1 integration smoke test coverage in `backend/tests/integration/test_phase1_smoke.py` for FastAPI startup, health, instruments, prices, news, and mocked collector execution
- Root `README.md` with prerequisites, setup flow, test commands, project structure, and the documented Phase 1 verification command
- Jasnah decision note documenting the mocked smoke-test strategy in `.squad/decisions/inbox/jasnah-phase1-smoke-test-mock-db.md`
- Created the full financePortal GitHub backlog as 75 atomic issues across phases 1-6, with acceptance criteria, dependencies, and squad ownership
- Recorded Adolin's backlog breakdown summary in `.squad/decisions/inbox/adolin-backlog-breakdown.md`
- Initial Squad team setup with Stormlight Archive casting (Dalinar, Kaladin, Shallan, Navani, Jasnah)
- Project scaffolding: `.squad/` directory structure, agent charters, routing rules
- Global rule: all agents must update CHANGELOG.md when making changes
- Adolin (Product Manager) added to team — requirements, PRDs, ideation, research
- Wit (Researcher) added to team — API discovery, data sources, competitive analysis
- Renarin (Designer) added to team — data visualization, dashboard UX, charting patterns
- Playwright browser setup attempted — requires `npx playwright install chromium` or `--channel chrome` flag to use system Chrome
- Phase 1 backend foundation with Docker Compose PostgreSQL + TimescaleDB, uv-managed Python backend metadata, and a PowerShell bootstrap script
- Async backend database layer with SQL migrations, seed data, price/news collectors, APScheduler orchestration, and FastAPI routes for health, instruments, prices, and news
- Backend verification coverage for connection string building, migration discovery, and market-hours scheduler logic
- Renarin added `Plans/dashboard-design-spec.md` as the dashboard source of truth for layout, color, typography, density, and component behavior
- Renarin added a design-system decision note to `.squad/decisions/inbox/renarin-design-system.md` and recorded project learnings in `.squad/agents/renarin/history.md`
- Backend migration system scaffold under `backend/` with a reusable Python runner and numbered SQL migrations
- Phase 1 schema for instruments, watchlists, time-series prices, news, filings, sentiment, alerts, and AI insights
- Backend migration unit tests covering numeric ordering and idempotent re-runs
