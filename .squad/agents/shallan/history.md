# Project Context

- **Owner:** Giakas
- **Project:** financePortal — Personal financial intelligence dashboard. Custom watchlists, real-time alerts, market news aggregation, analyst ratings, sentiment tracking, unusual event notifications. Fast, customizable interface with charts and visualizations.
- **Stack:** TypeScript/React (dashboard), Python backend APIs, PostgreSQL
- **Key responsibilities:** Dashboard UI, charts, watchlist components, alert configuration UI, responsive design
- **Created:** 2026-05-24

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->
- 2026-05-24T12:51:37-07:00 — Tailwind CSS v4 is wired through the Vite frontend, with design-spec tokens centralized in `frontend/src/styles/tokens.css` and shared theme/status classes in `frontend/src/styles/index.css`.
- The frontend lives in `frontend/` as a Vite + React + TypeScript app with strict mode enabled.
- The frontend uses an `@/` path alias that maps to `frontend/src/`.
- React Query is wired at the app entry point from the initial scaffold, and the Vite dev server proxies `/api` requests to `http://localhost:8000`.
- 2026-05-24T19:51:02Z — Team update: Renarin design spec complete (HTML conversion in progress), Kaladin backend ready, Adolin backlog ready. Frontend scaffold dependencies materializing. Await Renarin HTML + Phase 1 verification.
