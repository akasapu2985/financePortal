"""FinBERT headline scoring helpers for the intelligence pipeline."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from importlib import import_module
from typing import Any

_DEFAULT_MODEL_NAME = "ProsusAI/finbert"
_DEFAULT_NEUTRAL_THRESHOLD = 0.6
_DEFAULT_BATCH_SIZE = 16


@dataclass(frozen=True, slots=True)
class FinBertScore:
    """Sentiment score for a single headline."""

    label: str
    confidence: float
    should_forward: bool


class FinBertScorer:
    """Lazy-loading FinBERT sentiment scorer for article headlines."""

    def __init__(
        self,
        *,
        model_name: str = _DEFAULT_MODEL_NAME,
        neutral_threshold: float = _DEFAULT_NEUTRAL_THRESHOLD,
        batch_size: int = _DEFAULT_BATCH_SIZE,
        pipeline_factory: Callable[[], Callable[..., Any]] | None = None,
    ) -> None:
        if not 0 <= neutral_threshold <= 1:
            raise ValueError("neutral_threshold must be between 0 and 1")
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")

        self._model_name = model_name
        self._neutral_threshold = neutral_threshold
        self._batch_size = batch_size
        self._pipeline_factory = pipeline_factory
        self._classifier: Callable[..., Any] | None = None

    def score_headline(self, headline: str) -> FinBertScore:
        """Score a single headline."""
        return self.score_headlines([headline])[0]

    def score_headlines(self, headlines: Sequence[str]) -> list[FinBertScore]:
        """Score many headlines in batches while preserving input order."""
        scores = [self._empty_score() for _ in headlines]
        pending = [
            (index, headline.strip())
            for index, headline in enumerate(headlines)
            if headline and headline.strip()
        ]

        for start in range(0, len(pending), self._batch_size):
            batch = pending[start : start + self._batch_size]
            batch_headlines = [headline for _, headline in batch]
            raw_outputs = self._normalize_outputs(
                self._get_classifier()(
                    batch_headlines,
                    truncation=True,
                    padding=True,
                    batch_size=self._batch_size,
                )
            )
            for (index, _), raw_output in zip(batch, raw_outputs, strict=True):
                scores[index] = self._to_score(raw_output)

        return scores

    def annotate_articles(
        self,
        articles: Sequence[Mapping[str, Any]],
        *,
        headline_key: str = "title",
    ) -> list[dict[str, Any]]:
        """Attach FinBERT label/score metadata to article dictionaries."""
        headlines = [self._resolve_headline(article, headline_key) for article in articles]
        scores = self.score_headlines(headlines)

        return [
            {
                **dict(article),
                "finbert_label": score.label,
                "finbert_score": score.confidence,
                "should_forward_to_llm": score.should_forward,
            }
            for article, score in zip(articles, scores, strict=True)
        ]

    def filter_articles_for_llm(
        self,
        articles: Sequence[Mapping[str, Any]],
        *,
        headline_key: str = "title",
    ) -> list[dict[str, Any]]:
        """Return only the articles that should continue to LLM analysis."""
        return [
            article
            for article in self.annotate_articles(articles, headline_key=headline_key)
            if article["should_forward_to_llm"]
        ]

    def _get_classifier(self) -> Callable[..., Any]:
        if self._classifier is None:
            if self._pipeline_factory is not None:
                self._classifier = self._pipeline_factory()
            else:
                transformers = import_module("transformers")
                self._classifier = transformers.pipeline(
                    "text-classification",
                    model=self._model_name,
                    tokenizer=self._model_name,
                    device=-1,
                )
        return self._classifier

    def _resolve_headline(self, article: Mapping[str, Any], headline_key: str) -> str:
        headline = article.get(headline_key) or article.get("headline") or article.get("title")
        return str(headline or "")

    def _empty_score(self) -> FinBertScore:
        return FinBertScore(label="neutral", confidence=0.0, should_forward=False)

    def _normalize_outputs(self, outputs: Any) -> list[Mapping[str, Any]]:
        if isinstance(outputs, Mapping):
            return [outputs]
        return list(outputs)

    def _to_score(self, output: Mapping[str, Any]) -> FinBertScore:
        label = str(output.get("label", "neutral")).lower()
        confidence = float(output.get("score", 0.0))
        should_forward = label != "neutral" or confidence >= self._neutral_threshold
        return FinBertScore(label=label, confidence=confidence, should_forward=should_forward)
