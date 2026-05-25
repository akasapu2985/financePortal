# Kaladin Decision — Headline Deduplication

- **Date:** 2026-05-25T15:28:43-07:00
- **Issue:** #84
- **Decision:** Implement headline deduplication in `pipeline/src/filters/deduplication.py` with sentence-transformers `all-MiniLM-L6-v2`, cosine similarity over stored embeddings from the prior 7 days, and a default similarity threshold of `0.85` that callers can override.
- **Why:** The pipeline needs semantic headline matching before FinBERT so near-duplicate news does not consume downstream filter/analyzer capacity. Returning embeddings as plain `list[float]` keeps them directly storable in an `articles.embedding` JSON column without extra serialization helpers at the call site.
- **Notes:** The filter lazy-loads the model so unit tests can inject a fake encoder and avoid heavyweight model downloads in CI.
