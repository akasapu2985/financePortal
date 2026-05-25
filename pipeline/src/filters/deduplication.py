from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_SIMILARITY_THRESHOLD = 0.85
DEFAULT_LOOKBACK_DAYS = 7


class EmbeddingModel(Protocol):
    def encode(self, headline: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class StoredArticle:
    article_id: str | int
    headline: str
    embedding: Sequence[float] | str
    published_at: datetime


@dataclass(frozen=True)
class SimilarHeadlineMatch:
    article_id: str | int
    headline: str
    similarity: float
    published_at: datetime


@dataclass(frozen=True)
class DeduplicationResult:
    is_duplicate: bool
    embedding: list[float]
    match: SimilarHeadlineMatch | None


def load_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> EmbeddingModel:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _to_embedding_list(raw_embedding: Sequence[float] | str) -> list[float]:
    if isinstance(raw_embedding, str):
        parsed_embedding = json.loads(raw_embedding)
    else:
        parsed_embedding = raw_embedding
    return [float(value) for value in parsed_embedding]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embeddings must have the same dimensions")

    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0

    dot_product = sum(
        left_value * right_value
        for left_value, right_value in zip(left, right, strict=True)
    )
    return dot_product / (left_norm * right_norm)


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class HeadlineDeduplicator:
    def __init__(
        self,
        *,
        model_name: str = DEFAULT_MODEL_NAME,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
        model: EmbeddingModel | None = None,
    ) -> None:
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.lookback_days = lookback_days
        self._model = model

    @property
    def model(self) -> EmbeddingModel:
        if self._model is None:
            self._model = load_embedding_model(self.model_name)
        return self._model

    def generate_embedding(self, headline: str) -> list[float]:
        raw_embedding = self.model.encode(
            headline,
            convert_to_numpy=False,
            normalize_embeddings=False,
        )
        return [float(value) for value in raw_embedding]

    def evaluate(
        self,
        headline: str,
        recent_articles: Sequence[StoredArticle],
        *,
        now: datetime | None = None,
    ) -> DeduplicationResult:
        embedding = self.generate_embedding(headline)
        comparison_time = _normalize_timestamp(now or datetime.now(UTC))
        cutoff = comparison_time - timedelta(days=self.lookback_days)
        most_similar_match: SimilarHeadlineMatch | None = None

        for article in recent_articles:
            published_at = _normalize_timestamp(article.published_at)
            if published_at < cutoff:
                continue

            similarity = cosine_similarity(embedding, _to_embedding_list(article.embedding))
            if most_similar_match is not None and similarity <= most_similar_match.similarity:
                continue

            most_similar_match = SimilarHeadlineMatch(
                article_id=article.article_id,
                headline=article.headline,
                similarity=similarity,
                published_at=published_at,
            )

        is_duplicate = (
            most_similar_match is not None
            and most_similar_match.similarity >= self.similarity_threshold
        )
        return DeduplicationResult(
            is_duplicate=is_duplicate,
            embedding=embedding,
            match=most_similar_match if is_duplicate else None,
        )
