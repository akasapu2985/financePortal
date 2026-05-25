# Kaladin Decision: pipeline scheduler path with backend compatibility

- **Date:** 2026-05-25T15:28:43-07:00
- **By:** Kaladin
- **Decision:** Treat `pipeline/src/scheduler.py` plus `pipeline/schedule.yaml` as the canonical scheduler entrypoint for the intelligence-pipeline architecture, while keeping `backend/src/collectors/scheduler.py` as a compatibility export for current imports, tests, and bootstrap scripts.
- **Why:** Issue #81 targets a pipeline scheduler, but the existing codebase still references the backend collector path. Moving the orchestration logic to `pipeline/` aligns the runtime with the Hermes/MCP pivot without forcing a risky all-at-once import migration across the backend today.
