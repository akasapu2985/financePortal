# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Custom watchlists, real-time alerts, market news aggregation, analyst ratings, sentiment tracking, unusual event notifications. Fast, customizable interface with charts and visualizations.
- **Stack:** TypeScript/React (dashboard), Python backend APIs, PostgreSQL
- **Key responsibilities:** Dashboard UI, charts, watchlist components, alert configuration UI, responsive design
- **Created:** 2026-05-24

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-24T12:51:37-07:00 — The frontend data layer is split between normalized axios wrappers in `frontend/src/services/api.ts`/`types.ts` and React Query hooks in `frontend/src/hooks/queries/useMarketData.ts`, with app-wide cache defaults centralized in `frontend/src/providers/QueryProvider.tsx`.
- 2026-05-24T12:51:37-07:00 — Tailwind CSS v4 is wired through the Vite frontend, with design-spec tokens centralized in `frontend/src/styles/tokens.css` and shared theme/status classes in `frontend/src/styles/index.css`.
- 2026-05-24T12:51:37-07:00 — Dashboard shell composition now lives in `frontend/src/layouts/DashboardLayout.tsx` and reusable shell components under `frontend/src/components/shell/`, with `App.tsx` responsible only for wiring placeholder panel content.
- The frontend lives in `frontend/` as a Vite + React + TypeScript app with strict mode enabled.
- The frontend uses an `@/` path alias that maps to `frontend/src/`.
- React Query is wired at the app entry point from the initial scaffold, and the Vite dev server proxies `/api` requests to `http://localhost:8000`.
- 2026-05-24T19:51:02Z — Team update: Renarin design spec complete (HTML conversion in progress), Kaladin backend ready, Adolin backlog ready. Frontend scaffold dependencies materializing. Await Renarin HTML + Phase 1 verification.
- 2026-05-24T12:51:37-07:00 — Dashboard symbol coordination now lives in `frontend/src/hooks/useSelectedSymbol.ts`, and both watchlist selection plus future symbol-driven panels are expected to read/write the same global context.
- 2026-05-24T12:51:37-07:00 — The dashboard’s live market UI is split between `frontend/src/components/watchlist/` for tabbed watchlists + per-row quote polling and `frontend/src/components/chart/` for the Lightweight Charts candlestick/volume workspace driven by shared range-aware price helpers in `frontend/src/utils/marketData.ts`.
