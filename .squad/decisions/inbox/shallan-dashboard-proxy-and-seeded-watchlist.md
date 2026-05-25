# Shallan Decision Note

- **Date:** 2026-05-24T16:42:34-07:00
- **Agent:** Shallan
- **Topic:** Dashboard proxy + starter watchlist bootstrap

## Decision
The frontend dashboard will treat `/api/*` as a client-only namespace and rely on the Vite dev proxy to rewrite requests onto the backend's root-mounted routes. When the watchlist service returns no watchlists, the UI will auto-create a starter watchlist from the seeded instruments so the desktop dashboard opens with a usable left rail instead of an empty state.

## Why
The backend currently serves `watchlists`, `instruments`, `news`, and `prices` without an `/api` prefix, which caused the frontend to load permanent 404 states in development. Auto-bootstrapping the first watchlist keeps the dashboard aligned with the three-column Bloomberg-style design by ensuring the chart/news rails have an active symbol immediately.

## Trade-offs
This keeps local development self-healing and removes first-run confusion, but it means the frontend owns a small amount of bootstrap behavior until the backend guarantees a default watchlist and seeded prices.
