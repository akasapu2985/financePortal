"""Semantic headline deduplication helpers for the intelligence pipeline."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any

import numpy as np

_DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
_DEFAULT_SIMILARITY_THRESHOLD = 0.85
_DEFAULT_WINDOW_DAYS = 7
_DEFAULT_EMBEDDING_KEY = "headline_embedding"


@dataclass(frozen=True, slots=True)
class StoredHeadline:
    """In-memory record for a recently processed headline embedding."""

    embedding: np.ndarray
    timestamp: datetime
    headline: str


class HeadlineDeduplicator:
    """Lazy-loading sentence-transformer deduplicator for article headlines."""

    def __init__(
        self,
        *,
        model_name: str = _DEFAULT_MODEL_NAME,
        similarity_threshold: float = _DEFAULT_SIMILARITY_THRESHOLD,
        window_days: int = _DEFAULT_WINDOW_DAYS,
        model_factory: Callable[[], Any] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1")
        if window_days <= 0:
            raise ValueError("window_days must be greater than 0")

        self._model_name = model_name
        self._similarity_threshold = similarity_threshold
        self._window_days = window_days
        self._model_factory = model_factory
        self._clock = clock or _utc_now
        self._model: Any | None = None
        self._recent_headlines: list[StoredHeadline] = []

    def is_duplicate(self, headline: str) -> bool:
        """Return whether the headline is semantically similar to a recent article."""
        normalized_headline = headline.strip()
        if not normalized_headline:
            return False

        self._evict_old()
        embedding = self._encode_headline(normalized_headline)
        return self._find_duplicate(embedding) is not None

    def add(self, headline: str) -> None:
        """Store a headline embedding in the recent in-memory window."""
        normalized_headline = headline.strip()
        if not normalized_headline:
            return

        self._evict_old()
        embedding = self._encode_headline(normalized_headline)
        self._remember(normalized_headline, embedding)

    def filter_articles(
        self,
        articles: Sequence[Mapping[str, Any]],
        *,
        headline_key: str = "title",
    ) -> list[dict[str, Any]]:
        """Return only non-duplicate articles and attach their embeddings."""
        self._evict_old()
        headlines = [self._resolve_headline(article, headline_key) for article in articles]
        embeddings = self._encode_headlines(headlines)
        filtered_articles: list[dict[str, Any]] = []

        for article, headline, embedding in zip(articles, headlines, embeddings, strict=True):
            if not headline:
                filtered_articles.append(
                    {
                        **dict(article),
                        _DEFAULT_EMBEDDING_KEY: embedding.tolist(),
                    }
                )
                continue

            if self._find_duplicate(embedding) is not None:
                continue

            self._remember(headline, embedding)
            filtered_articles.append(
                {
                    **dict(article),
                    _DEFAULT_EMBEDDING_KEY: embedding.tolist(),
                }
            )

        return filtered_articles

    def _evict_old(self) -> None:
        """Remove stored headlines that fall outside the recency window."""
        cutoff = self._clock() - timedelta(days=self._window_days)
        self._recent_headlines = [
            entry for entry in self._recent_headlines if entry.timestamp >= cutoff
        ]

    def _get_model(self) -> Any:
        if self._model is None:
            if self._model_factory is not None:
                self._model = self._model_factory()
            else:
                sentence_transformers = import_module("sentence_transformers")
                self._model = sentence_transformers.SentenceTransformer(self._model_name)
        return self._model

    def _encode_headline(self, headline: str) -> np.ndarray:
        return self._encode_headlines([headline])[0]

    def _encode_headlines(self, headlines: Sequence[str]) -> list[np.ndarray]:
        if not headlines:
            return []

        raw_embeddings = self._get_model().encode(list(headlines), normalize_embeddings=True)
        return [np.asarray(embedding, dtype=float) for embedding in raw_embeddings]

    def _find_duplicate(self, embedding: np.ndarray) -> StoredHeadline | None:
        for entry in self._recent_headlines:
            similarity = float(np.dot(embedding, entry.embedding))
            if similarity >= self._similarity_threshold:
                return entry
        return None

    def _remember(self, headline: str, embedding: np.ndarray) -> None:
        self._recent_headlines.append(
            StoredHeadline(
                embedding=embedding,
                timestamp=self._clock(),
                headline=headline,
            )
        )

    def _resolve_headline(self, article: Mapping[str, Any], headline_key: str) -> str:
        headline = article.get(headline_key) or article.get("headline") or article.get("title")
        return str(headline or "").strip()


def _utc_now() -> datetime:
    return datetime.now(UTC)
