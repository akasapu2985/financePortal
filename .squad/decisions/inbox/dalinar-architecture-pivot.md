# Architecture Pivot — Intelligence Pipeline for Hermes

**By:** Dalinar  
**Date:** 2026-05-24T20:37:13-07:00  
**Status:** Active

## Decision

financePortal has pivoted from a full financial dashboard to a **financial intelligence pipeline** that feeds Hermes.

## New Architecture

```
[Gather]          [Filter]           [Analyze]          [Serve]
Finnhub/yfinance → Regex + FinBERT → DeepSeek extracts → Hermes reads via MCP
(free APIs)        (zero cost)        (~$0.01/day)        (~2,500 tokens/session)
```

## Key Decisions

1. **No dashboard** — Fidelity Tracker+ handles visualization. We build no frontend.
2. **No FastAPI** — No HTTP REST API for humans. MCP is the only interface.
3. **SQLite-first** — No Docker, no TimescaleDB. Plain SQLite with WAL mode.
4. **FinBERT pre-filter** — Local CPU model eliminates ~80-90% of articles before DeepSeek.
5. **DeepSeek via OpenRouter** — $0.27/1M tokens, batched every 6h, not real-time.
6. **MCP is Phase 3, not Phase 6** — It's the primary deliverable, not an afterthought.
7. **Telegram for push** — morning brief (7am), evening brief (6pm), immediate critical alerts.
8. **Daily cost target: ~$0.05** — well-defined budget constraint.

## Phase Breakdown (4 phases replacing 6)

- **Phase 1:** Foundation — collectors + SQLite schema + APScheduler
- **Phase 2:** Intelligence — FinBERT + DeepSeek + briefs
- **Phase 3:** Hermes — MCP server + Telegram delivery
- **Phase 4:** Advanced signals — Reddit, insider trades, pattern detection

## What Is Abandoned

- React/Vite frontend
- FastAPI REST server
- Docker Compose / TimescaleDB
- Dashboard-facing alert UI
- Multi-phase alert tier system (dashboard panels)

## Rationale

The user already has Fidelity Tracker+ for portfolio visualization. Building a second dashboard
duplicates effort and adds maintenance burden with no incremental value. The intelligence pipeline
delivers the same market awareness through Hermes + Telegram with ~$0.05/day operating cost
and zero frontend maintenance.
