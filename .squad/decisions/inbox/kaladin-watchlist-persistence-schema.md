# Kaladin Decision: Persist watchlists with dedicated relational tables

- Recorded: 2026-05-24T12:51:37-07:00
- Requested by: Giakas

## Decision

Implement watchlist persistence with a dedicated `watchlists` table plus a `watchlist_items` join table keyed by `watchlist_id` and `instrument_id`, and expose CRUD + membership mutation endpoints from a FastAPI router at `/watchlists`.

## Rationale

The backend already treats `instruments` as the canonical symbol catalog, so referencing `instrument_id` preserves referential integrity and lets watchlists survive app restarts without duplicating instrument metadata. Returning watchlists with embedded instrument rows gives the frontend a single API shape for read, create, update, and membership edits.

## Consequences

- Watchlist membership now validates against the seeded `instruments` table before inserts or deletes.
- Deleting a watchlist cascades to membership rows automatically through foreign keys.
