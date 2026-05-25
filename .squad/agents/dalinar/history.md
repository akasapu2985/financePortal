# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Custom watchlists, real-time alerts, market news aggregation, analyst ratings, sentiment tracking, unusual event notifications. Gathers data from free sources (RSS, financial APIs, X/Twitter, SEC filings, insider trading, politician disclosures). Runs locally on Windows PC.
- **Stack:** Python (data collection, APIs, processing), TypeScript/React (dashboard), PostgreSQL (local storage), MCP server (for Hermes agent), Telegram notifications
- **Architecture layers:** Data collection → Local storage → Processing/caching → AI analysis → Dashboard UI → Agent/MCP integration
- **Created:** 2026-05-24

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-24T22:22:23Z — (SUPERSEDED) Previously replaced `gh` with `Invoke-RestMethod` — reverted. Root cause was `gh` not on PATH, not missing. `gh` v2.92.0 is installed at `C:\Program Files\GitHub CLI` and authenticated as `akasapu2985`. Fix applied to `start.ps1` (PATH fallback) and Ralph's charter (uses `gh` directly).
- 2026-05-25T03:37:13Z — Architecture pivot: financePortal is now an intelligence pipeline for Hermes, not a dashboard. No frontend, no FastAPI, no Docker/TimescaleDB. SQLite-first, FinBERT pre-filter (local/free), DeepSeek via OpenRouter batched every 6h (~$0.01/day), MCP as sole Hermes interface. Plans/ rewritten to reflect 4-phase build (Foundation → Intelligence → Hermes → Advanced Signals). Cost target: ~$0.05/day.
