# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **[Adolin] GitHub issue restructure for intelligence pipeline pivot**: Closed 12 obsolete issues (#32-35, #42-44, #54-56, #65-66). Created 25 new issues (#76-100) covering Phases 1-4 of the new pipeline architecture (Foundation, Intelligence, Hermes MCP, Advanced Signals). Updated 18 existing issues (#47-53, #58-61, #69-75) with pivot context. Updated phase label descriptions. Recorded architecture pivot decision in decisions.md.
- **[Jasnah] Scheduler requirements-based test coverage**: Expanded `backend/tests/test_scheduler.py` with YAML config loading, env overrides, market-hours gating, overlap protection, graceful shutdown, scheduler state logging, startup failure handling, and collector crash coverage. Added explicit skipped tests only for env-only fallback when the schedule YAML is missing and zero-interval validation that still await implementation.
- **[Jasnah] Scheduler YAML dependency**: Added `PyYAML` to `backend/pyproject.toml` so the pipeline scheduler module can import and execute during backend test runs.
- **[Kaladin] Pipeline scheduler defaults + compatibility bridge**: Added `pipeline/src/scheduler.py` plus `pipeline/schedule.yaml` as the pipeline-facing APScheduler runner for issue #81, with YAML defaults, env-var overrides, cron/interval support, graceful startup/shutdown handling, and per-job state logging.
- **[Kaladin] OpenRouter DeepSeek client**: Added `pipeline/src/intelligence/openrouter.py` with an async OpenRouter chat completions client that reads `OPENROUTER_API_KEY`, defaults to `deepseek/deepseek-r1`, retries transient failures with exponential backoff, and logs per-request token usage. Added mocked HTTP coverage in `pipeline/tests/test_openrouter.py` for success, configuration, and retry behavior for issue #85.
- **[Kaladin] Structured signal extraction prompts + extractor**: Added versioned prompts in `pipeline/src/intelligence/prompts/v1_signal_extraction.py` plus `pipeline/src/intelligence/extractor.py` for OpenRouter-backed article-to-signal extraction, schema validation, and explicit `no_signal`/`ambiguous` handling. Added a 20-case synthetic eval set in `pipeline/tests/eval/signal_extraction/cases.json` and mocked coverage in `pipeline/tests/test_extractor.py` for issue #86.

### Added (previously)
- Added root `setup.ps1` to bootstrap fresh Windows machines with prerequisite checks, winget-based installs for Docker Desktop/Python 3.12/Node.js LTS/GitHub CLI, official `uv` installation, Playwright Chromium setup, PATH fixups, `npm install`, and an end-of-run summary
- Kaladin recorded the PATH persistence decision for setup bootstrap behavior in `.squad/decisions/inbox/kaladin-setup-path-fixups.md`
- Seeded a default backend watchlist with MSFT, MRAM, DELL, and AMZN so the dashboard has starter data on first load
- **[Dalinar] Architecture pivot**: Rewrote `Plans/architecture.html` to reflect the intelligence pipeline design (Gather → Filter → Analyze → Serve). Covers Signal Store schema, FinBERT pre-filter, DeepSeek batched analysis, Context Builder, MCP server tools, and Telegram delivery. Explicit scope exclusions: no dashboard, no FastAPI, no Docker/TimescaleDB.
- **[Dalinar] Implementation plan updated**: Rewrote `Plans/implementation-plan.html` with new 4-phase breakdown (Foundation → Intelligence → Hermes → Advanced Signals). Removed 6-phase dashboard plan entirely.
- **[Dalinar] Decision recorded**: `.squad/decisions/inbox/dalinar-architecture-pivot.md` documents all pivot decisions for the Scribe to merge.

### Changed
- Updated `start.ps1` so `Ensure-Uv` uses Astral's official PowerShell installer instead of `pip install --user uv`, while keeping the `.local\bin` PATH fixup
- Ralph reconciled issue tracker: confirmed #2–#31 closed, labeled #32–#34 as `go:ready` for Phase 2 close-out
- Jasnah ran a Phase 1–3 verification sweep: backend pytest/Ruff passed, frontend TypeScript/lint/build passed, but Vitest and Playwright have no tests and runtime alert features remain absent outside schema definitions
- Kaladin repointed `start.ps1`, `.env.example`, and `README.md` at the new pipeline scheduler flow while keeping `backend/src/collectors/scheduler.py` as a compatibility export for existing imports.
- Shallan fixed the desktop dashboard shell so Tailwind breakpoint variants render the Bloomberg-style three-column layout again, the top bar stays persistent, and the Vite dev proxy rewrites `/api/*` requests to the backend's root-mounted routes.
- Shallan upgraded the watchlist/chart empty-state UX so the frontend auto-creates a starter watchlist from seeded instruments, selects the first symbol, and surfaces a graceful "price history unavailable" state when seeded symbols do not have chart data yet.
- Shallan initialized `shadcn/ui` for the Tailwind v4 frontend and overhauled the dashboard into a polished dark trading workspace with upgraded top bar, watchlist, chart controls, and news cards.

## [2025-07-17]

### Meta
- Ralph (Work Monitor) reconciled GitHub issue tracker against codebase — confirmed issues #2–#31 closed (Phase 1 complete + Phase 2 complete). Issues #32, #33, #34 remain open as Phase 2 remaining work. Issues #35–#75 remain open representing Phases 3–6 backlog.

### Added
- Watchlist CRUD controls in `frontend/src/components/watchlist/WatchlistActions.tsx`, `frontend/src/components/watchlist/WatchlistItem.tsx`, `frontend/src/components/watchlist/WatchlistPanel.tsx`, `frontend/src/hooks/mutations/useWatchlistMutations.ts`, `frontend/src/hooks/queries/useMarketData.ts`, `frontend/src/services/api.ts`, and `backend/src/api/routes/watchlists.py`, including add/remove buttons, cache-syncing mutations, inline success/error feedback, and support for DELETE payloads on `/api/watchlists/{id}/instruments`
- Extended chart time-range controls in `frontend/src/components/chart/TimeRangeSelector.tsx`, `frontend/src/components/chart/ChartPanel.tsx`, `frontend/src/services/api.ts`, `frontend/src/services/types.ts`, and `backend/src/api/routes/prices.py`, including 6M/1Y/ALL ranges and full-history API parameter support
- Dashboard news feed and top bar enhancements in `frontend/src/components/news/NewsFeed.tsx`, `frontend/src/components/shell/TopBar.tsx`, `frontend/src/components/watchlist/WatchlistPanel.tsx`, `frontend/src/hooks/queries/useMarketData.ts`, and `frontend/src/services/api.ts`, including symbol-aware backend news queries, sentiment badges, debounced watchlist search, market indices, and portfolio summary cards
- Watchlist and chart dashboard panels in `frontend/src/components/watchlist/`, `frontend/src/components/chart/`, `frontend/src/hooks/useSelectedSymbol.ts`, and `frontend/src/utils/marketData.ts`, including shared selected-symbol context, live quote rows, time-range controls, and a TradingView Lightweight Charts candlestick + volume canvas
- Typed frontend API service wrappers in `frontend/src/services/api.ts` and `frontend/src/services/types.ts`, including centralized axios config, normalized response models, and structured `ApiClientError` handling for market data and watchlist CRUD
- React Query async-state plumbing in `frontend/src/providers/QueryProvider.tsx`, `frontend/src/hooks/queries/useMarketData.ts`, and `frontend/src/main.tsx`, with market-aware stale times, polling defaults, retry backoff, and reusable query keys/hooks
- Dashboard shell layout in `frontend/src/layouts/DashboardLayout.tsx`, `frontend/src/components/shell/TopBar.tsx`, `frontend/src/components/shell/PanelFrame.tsx`, and `frontend/src/App.tsx`, with a spec-aligned top bar plus left watchlist, center chart, and right news placeholder panels
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
