# Kaladin — OpenRouter Client Decision

- **Date:** 2026-05-25T15:28:43-07:00
- **Issue:** #85
- **Decision:** Standardize DeepSeek OpenRouter access in `pipeline/src/intelligence/openrouter.py` on a shared async `httpx.AsyncClient` wrapper with injectable transport and sleep dependencies for deterministic mocked tests.
- **Why:** Phase 2 intelligence work needs one MCP-facing client pattern for LLM calls that is easy to reuse, retries transient 408/429/5xx failures with exponential backoff, and logs token usage on every successful request for cost visibility.
- **Follow-up:** Future intelligence modules should build on this client instead of making raw OpenRouter calls directly.
