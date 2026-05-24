# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
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
