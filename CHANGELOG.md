# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
