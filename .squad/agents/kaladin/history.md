# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Custom watchlists, real-time alerts, market news aggregation, analyst ratings, sentiment tracking, unusual event notifications. Gathers data from free sources (RSS, financial APIs, X/Twitter, SEC filings, insider trading, politician disclosures). Runs locally on Windows PC.
- **Stack:** Python (data collection, APIs, processing), TypeScript/React (dashboard), PostgreSQL (local storage), MCP server (for Hermes agent), Telegram notifications
- **Key responsibilities:** Data collection services, API integrations, scraping, MCP server, Telegram bot
- **Created:** 2026-05-24

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-25T15:28:43-07:00 — Portfolio article pre-filtering now lives in `pipeline/src/filters/ticker_filter.py`, where short tickers use case-sensitive boundary regexes and longer tickers use case-insensitive compiled regexes to reduce false positives while returning `matched_tickers` per article.
- 2026-05-24T12:51:37-07:00 — Watchlist persistence now lives in `backend/src/db/migrations/003_watchlists.sql`, with FastAPI CRUD + membership routes implemented in `backend/src/api/routes/watchlists.py` against the shared asyncpg pool.
- 2026-05-24T12:26:16-07:00 — Phase 1 backend runs as a uv-managed Python service under `backend/`, with source modules loaded from `backend/src` via `PYTHONPATH`.
- 2026-05-24T12:26:16-07:00 — Database bootstrap uses `backend/src/db/migrate.py` plus SQL files in `backend/src/db/migrations/`, and `backend/src/seed.py` seeds the default instrument universe.
- 2026-05-24T12:26:16-07:00 — Market data collection uses Yahoo Finance for prices, Finnhub for news, and APScheduler for recurring jobs gated by US market hours.
- 2026-05-24T19:51:02Z — Team update: Navani schema + migrations ready, Renarin design spec ready, Adolin 75-issue backlog ready. Awaiting Phase 1 smoke test from Jasnah.
