# Kaladin Decision: Persist setup PATH fixups for uv and GitHub CLI

- Recorded: 2026-05-24T16:14:12-07:00
- Requested by: Giakas

## Decision

Have `setup.ps1` add `C:\Users\{user}\.local\bin` and `C:\Program Files\GitHub CLI` to the current session PATH and the user PATH when those directories exist.

## Rationale

Fresh Windows shells often do not see `uv` or `gh` immediately after installation, which breaks the self-contained setup flow. Persisting the fixups makes the bootstrap idempotent and keeps follow-up commands like `npm install`, `npx playwright install chromium`, and `start.ps1` working without manual PATH edits.

## Consequences

- New shells can resolve `uv` and `gh` after setup without extra user action.
- Re-running `setup.ps1` remains safe because duplicate PATH entries are skipped.
