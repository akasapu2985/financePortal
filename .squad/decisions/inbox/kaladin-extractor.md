# Kaladin — Signal Extraction Envelope Decision

- **Date:** 2026-05-25T15:28:43-07:00
- **Issue:** #86
- **Decision:** Standardize article extraction responses on a JSON envelope: successful extractions return `{"status":"signal","signal":{...}}`, while failure paths return `{"status":"no_signal",...}` or `{"status":"ambiguous",...}`. The success payload inside `signal` is the canonical schema with `{ticker, signal_type, sentiment, confidence, summary, catalysts, risks, time_horizon}`.
- **Why:** Hermes-facing pipeline code needs deterministic handling for articles that have no tradeable signal or contain conflicting narratives; a status envelope preserves the requested signal schema while making failure states explicit and machine-safe.
- **Follow-up:** Future prompt versions and eval runs should preserve this envelope contract so parser logic and downstream MCP consumers stay stable.
