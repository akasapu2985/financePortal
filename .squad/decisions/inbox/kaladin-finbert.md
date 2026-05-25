# Kaladin — FinBERT Sentiment Scoring

- **Date:** 2026-05-25T15:28:43-07:00
- **Issue:** #83
- **Decision:** Implement FinBERT sentiment scoring in `pipeline/src/intelligence/finbert.py` as a lazy-loaded `ProsusAI/finbert` wrapper that batches CPU headline inference, annotates article dictionaries with `finbert_label` and `finbert_score`, and flags low-confidence neutral headlines with `should_forward_to_llm = false` so only passing articles continue to downstream LLM analysis.
- **Why:** The pipeline pivot makes MCP the only interface, so sentiment gating needs to happen inside the pipeline flow before OpenRouter analysis. Keeping the model load lazy avoids startup cost for collectors and scheduler processes that may import intelligence helpers without needing immediate inference.
- **Dependency Note:** The active Python runtime is still synced through `backend/pyproject.toml`, so `transformers` and `torch` are registered there even though the scorer module lives under `pipeline/src/`.
