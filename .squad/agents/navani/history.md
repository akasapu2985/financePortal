# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Stores market data, watchlists, alerts, news, sentiment, analyst ratings locally in PostgreSQL. Needs intelligent caching — only pull incremental updates, keep historical data.
- **Stack:** PostgreSQL (primary store), Python (data pipelines), TypeScript/React (consumer)
- **Key responsibilities:** Database schema, migrations, caching strategy, query optimization, data pipelines
- **Created:** 2026-05-24

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-24T12:26:16-07:00 — Phase 1 stores market prices in separate TimescaleDB hypertables for intraday and daily candles so retention and query tuning can diverge later without reshaping consumers.
- 2026-05-24T12:26:16-07:00 — Alert rules use JSONB parameters with alert history split into a separate fired alerts table, keeping rule configuration flexible while preserving an auditable notification trail.
- 2026-05-24T19:51:02Z — Team update: Kaladin backend foundation complete, Renarin design spec complete, Adolin full backlog ready. Migration system ready for Kaladin integration.
