# Squad Decisions

## Active Decisions

### 2026-05-24T09:58:04-07:00: CHANGELOG.md Maintenance
**By:** Giakas (via Copilot)
**What:** Every agent MUST update CHANGELOG.md when making changes. This is a global rule for all agents — always maintain a changelog so there's a track of what actually changed.
**Why:** User request — captured for team memory

### 2026-05-24T11:35:12-07:00: GitHub Access and Permissions
**By:** Giakas (via Copilot)
**What:** The team has permission to push changes to the remote repository and has access to GitHub Issues for this repo (akasapu2985/financePortal).
**Why:** User request — captured for team memory

### 2026-05-24T12:26:16-07:00: Full Project Backlog Created
**By:** Adolin (PM)
**What:** Decomposed all 6 phases into 75 atomic GitHub issues with acceptance criteria, dependencies, and squad assignments. Issues are labeled by phase and assigned agent.
**Why:** Proper production tracking. No implementation without a tracked issue.

### 2026-05-24T12:26:16-07:00: Phase 1 GitHub Issue Creation Blocked
**By:** Dalinar
**What:** Prepared the 10 Phase 1 issue definitions, but could not create them in GitHub from this environment.
**Why:** The authenticated GitHub account is blocked by enterprise policy from creating labels and issues in `akasapu2985/financePortal`.
**Prepared issues:**
- Set up Docker Compose with PostgreSQL + TimescaleDB — `squad,squad:navani,phase-1`
- Set up Python backend project with uv — `squad,squad:kaladin,phase-1`
- Create database migration system + initial schema — `squad,squad:navani,phase-1`
- Build async database connection pool — `squad,squad:navani,phase-1`
- Build Yahoo Finance price collector — `squad,squad:kaladin,phase-1`
- Build Finnhub news collector — `squad,squad:kaladin,phase-1`
- Build APScheduler collector runner — `squad,squad:kaladin,phase-1`
- Build FastAPI app with core API routes — `squad,squad:kaladin,phase-1`
- Create start script and seed data — `squad,squad:kaladin,phase-1`
- Phase 1 integration verification — `squad,squad:jasnah,phase-1`

### 2026-05-24T12:26:16-07:00: Kaladin Backend Foundation
**By:** Kaladin
**What:** Standardize the Phase 1 backend on a uv-managed Python project rooted at `backend/`, with runtime imports resolved from `backend/src`. Use PostgreSQL 16 with TimescaleDB in Docker Compose, with SQL migrations and seeding handled by Python entry points. Persist market data through asyncpg-backed collectors: Yahoo Finance for intraday/daily prices, Finnhub for company news, and APScheduler for recurring collection intervals. Expose the first public backend surface through FastAPI routes for health, instruments, prices, and news, while `start.ps1` orchestrates local setup for cloned environments.

### 2026-05-24T12:26:16-07:00: Navani Schema Design
**By:** Navani
**What:** Phase 1 establishes a PostgreSQL 16 + TimescaleDB foundation for the finance platform with a lightweight SQL migration runner and schema ready for market data, watchlists, news, alerts, and later AI-generated insights.
**Key Decisions:**
1. Separate intraday and daily price storage into dedicated hypertables so each cadence can evolve with different retention, compression, and refresh policies.
2. Keep prices and sentiment in time-oriented tables keyed by instrument and timestamp to favor latest-N and range-query workloads from charts and watchlists.
3. Use exact-decimal price columns instead of floating point to protect portfolio math and downstream analytics from rounding drift.
4. Store alert rule configuration as JSONB so new rule variants can ship without immediate schema churn, while alert executions remain normalized in their own history table.
5. Reserve schema now for filings and AI insights so later phases can integrate new data sources without revisiting core relational boundaries.

### 2026-05-24T12:26:16-07:00: Dashboard Design System
**By:** Renarin (via Copilot)
**What:** Standardize the dashboard on a 3-column desktop layout with a persistent top bar, a dominant center chart canvas, a dense watchlist rail on the left, and a contextual news/alerts/AI rail on the right. Adopt a dark layered palette, compact 11px to 13px typography, monospace numerics, semantic gain/loss colors, resizable rails, and component rules for watchlist rows, chart controls, news cards, alerts, and AI briefs.
**Why:** Phase 2 needs a single source of truth that Shallan can implement without reopening design questions. The chosen system preserves Bloomberg-style scan density, TradingView-style chart usability, and enough structure to extend cleanly into alerts and AI insights in later phases.

### 2026-05-24T12:41:54-07:00: GitHub Account Rule
**By:** Giakas (via Copilot)
**What:** This project MUST use the `akasapu2985` personal GitHub account for ALL GitHub interactions (issues, PRs, pushes, gh CLI). Never use the enterprise managed user account (giakas_microsoft). Before any gh command, verify the active account is correct.
**Why:** User directive — EMU account is blocked from writing to this repo. Personal account owns the repo.

### 2026-05-24T12:44:35-07:00: Plans Folder Format Rule
**By:** Giakas (via Copilot)
**What:** All files in the `Plans/` folder MUST be HTML format (styled like the existing architecture.html and implementation-plan.html). No markdown files in Plans/.
**Why:** User directive — consistency in the Plans folder. HTML provides better presentation with dark theme styling.

### 2026-05-24T12:26:16-07:00: Playwright Setup as Root Dependency
**By:** Giakas (via Copilot)
**What:** Added @playwright/test to root package.json with postinstall hook that runs `npx playwright install chromium`. This ensures Playwright MCP works after a fresh clone + `npm install`.
**Why:** User wants self-contained setup. Playwright MCP in agency.toml requires Chromium browser binaries.

### 2026-05-24T12:26:16-07:00: Self-Contained Setup Directive
**By:** Giakas (via Copilot)
**What:** Keep all setup steps super easy and self-contained. The repo will be moved to a different machine by cloning. Everything must work with minimal manual steps.
**Why:** User request — captured for team memory

### 2026-05-24T13:25:00-07:00: Token Efficiency Rule
**By:** Giakas
**What:** ALL agents MUST minimize token usage:
1. Keep responses minimal — no verbose dumps into context
1. Use GitHub Issues (source of truth) + session plan.md for coordination, NOT inline repetition
3. Do NOT re-read files already processed in the same session
4. Agent prompts should be concise — pass only what's needed for the task
5. Recommend `/clear` between independent work items
6. Never repeat large code blocks back to the user — summarize instead
**Why:** Token usage is expensive. Context grows exponentially from older responses. Lean communication is a production team requirement.

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
