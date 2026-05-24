# Shallan Decision: Tailwind theme tokens use CSS variables as the source of truth

- Recorded: 2026-05-24T12:51:37-07:00
- Requested by: Giakas

## Decision

Keep the approved dashboard dark-theme values in `frontend/src/styles/tokens.css` as CSS custom properties, then mirror those values into `frontend/tailwind.config.ts` and `frontend/src/styles/index.css` so Tailwind utilities and shared semantic classes both point at the same token set.

## Rationale

The design spec is already token-driven, and CSS variables keep those values reusable for Tailwind utilities, chart libraries, and any non-Tailwind styling without duplicating ad hoc hex values through components. This also keeps semantic gain/loss/warning/info styling centralized for dense dashboard surfaces.

## Consequences

- Shared theme and status styling can be reused without inline color literals.
- Future chart, watchlist, and alerts work can consume the same dark-theme tokens from CSS or Tailwind.
