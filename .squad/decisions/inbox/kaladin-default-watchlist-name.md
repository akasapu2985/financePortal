# Default Watchlist Seed Name

- **Date:** 2026-05-24T16:43:37-07:00
- **By:** Kaladin
- **Decision:** Treat `My Watchlist` as the canonical seeded default watchlist name in backend seeding.
- **Why:** The active backend watchlist schema does not carry an `is_default` flag, so the seed needs a stable, idempotent way to find-or-create the starter watchlist before attaching dashboard symbols.
