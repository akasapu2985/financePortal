# Shallan Decision Note

- **Date:** 2026-05-24T17:10:08-07:00
- **Agent:** Shallan
- **Topic:** shadcn/ui + token-driven dashboard overhaul

## Decision
The frontend dashboard will standardize on `shadcn/ui` primitives layered on top of the existing Tailwind CSS v4 token system. New UI work should compose `frontend/src/components/ui/` building blocks first, then apply the finance dashboard palette and density rules through the shared CSS tokens instead of continuing with raw one-off HTML styling.

## Why
`npx shadcn@latest init` completed successfully in the Vite frontend even with Tailwind v4, which removes the compatibility risk called out at handoff. Using shared primitives gives the dashboard consistent spacing, hover states, badges, buttons, and cards while still preserving the dark financial design system Renarin defined.

## Trade-offs
This adds a small dependency footprint and requires maintaining the custom token mapping in `frontend/src/index.css`, but it prevents the UI from drifting back into wireframe-level bespoke markup and keeps future dashboard polish work faster and more consistent.
