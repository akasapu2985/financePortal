# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Custom watchlists, real-time alerts, market news aggregation, analyst ratings, sentiment tracking, unusual event notifications. Gathers data from free sources (RSS, financial APIs, X/Twitter, SEC filings, insider trading, politician disclosures). Runs locally on Windows PC.
- **Stack:** Python (data collection, APIs, processing), TypeScript/React (dashboard), PostgreSQL (local storage), MCP server (for Hermes agent), Telegram notifications
- **Key responsibilities:** Data collection services, API integrations, scraping, MCP server, Telegram bot
- **Created:** 2026-05-24

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-24T12:51:37-07:00 — Watchlist persistence now lives in `backend/src/db/migrations/003_watchlists.sql`, with FastAPI CRUD + membership routes implemented in `backend/src/api/routes/watchlists.py` against the shared asyncpg pool.
- 2026-05-24T12:26:16-07:00 — Phase 1 backend runs as a uv-managed Python service under `backend/`, with source modules loaded from `backend/src` via `PYTHONPATH`.
- 2026-05-24T12:26:16-07:00 — Database bootstrap uses `backend/src/db/migrate.py` plus SQL files in `backend/src/db/migrations/`, and `backend/src/seed.py` seeds the default instrument universe.
- 2026-05-24T12:26:16-07:00 — Market data collection uses Yahoo Finance for prices, Finnhub for news, and APScheduler for recurring jobs gated by US market hours.
- 2026-05-24T19:51:02Z — Team update: Navani schema + migrations ready, Renarin design spec ready, Adolin 75-issue backlog ready. Awaiting Phase 1 smoke test from Jasnah.
- 2026-05-25T15:28:43-07:00 — Scheduler ownership now lives at `pipeline/src/scheduler.py` with YAML defaults in `pipeline/schedule.yaml`, while `backend/src/collectors/scheduler.py` remains a compatibility bridge so existing tests/imports keep working during the pipeline pivot.
- 2026-05-25T15:28:43-07:00 — Scheduler config now prefers YAML defaults and only switches cadence via explicit env overrides like `PRICES_COLLECTION_INTERVAL_MINUTES` or `*_SCHEDULE_CRON`, preventing `.env.example` from silently overriding the pipeline schedule.
- 2026-05-25T15:28:43-07:00 — Team update: Issue #81 pipeline scheduler complete. PR #101 opened. Jasnah's test suite passing (18 tests, 2 skipped). Ready for review. Decisions archived.
- 2026-05-25T15:28:43-07:00 — OpenRouter intelligence calls now live under `pipeline/src/intelligence/openrouter.py` as an async `httpx` client with injectable transport/sleep hooks for mocked tests, DeepSeek default model selection, retry/backoff behavior, and per-request token-usage logging.
- 2026-05-25T15:28:43-07:00 — Structured article extraction now lives in `pipeline/src/intelligence/extractor.py`, which pairs the versioned prompt at `pipeline/src/intelligence/prompts/v1_signal_extraction.py` with schema-validated parsing so downstream MCP flows receive either a typed signal or explicit `no_signal`/`ambiguous` outcomes.
- 2026-05-25T15:28:43-07:00 — Intelligence eval coverage for signal extraction is stored as synthetic fixtures in `pipeline/tests/eval/signal_extraction/cases.json`, giving future prompt iterations a stable 20-case benchmark across earnings, guidance, M&A, regulatory, macro, insider, and failure scenarios.
- 2026-05-25T15:28:43-07:00 — FinBERT headline scoring now lives in `pipeline/src/intelligence/finbert.py` as a lazy-loaded `ProsusAI/finbert` wrapper that batches headlines, writes `finbert_score`/`finbert_label` onto article dictionaries, and skips low-confidence neutral items before LLM forwarding.
- 2026-05-25T15:35:00-07:00 — Phase 2 intelligence milestone complete: Issue #85 (OpenRouter client) PR #102, Issue #82 (ticker-aware pre-filter) PR #103, Issue #84 (headline deduplication) PR #104 all opened and passing. Pipeline now has signal filtering (ticker regex + semantic dedup) before LLM analysis.

