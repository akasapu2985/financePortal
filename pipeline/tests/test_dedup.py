from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from intelligence.dedup import HeadlineDeduplicator


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def set(self, now: datetime) -> None:
        self._now = now

    def __call__(self) -> datetime:
        return self._now


def _build_model_factory(
    embeddings_by_headline: dict[str, list[float]],
    encode_calls: list[list[str]] | None = None,
):
    def model_factory():
        class FakeSentenceTransformer:
            def encode(self, headlines: str | list[str], *, normalize_embeddings: bool):
                assert normalize_embeddings is True
                items = [headlines] if isinstance(headlines, str) else list(headlines)
                if encode_calls is not None:
                    encode_calls.append(items)
                return [embeddings_by_headline[item] for item in items]

        return FakeSentenceTransformer()

    return model_factory


def test_is_duplicate_lazy_loads_sentence_transformer_on_first_use(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import_calls: list[str] = []

    def fake_import_module(name: str) -> SimpleNamespace:
        import_calls.append(name)
        return SimpleNamespace(
            SentenceTransformer=lambda model_name: _build_model_factory(
                {
                    "Revenue jumps after earnings": [1.0, 0.0, 0.0],
                    "Revenue climbs after quarterly results": [0.9, 0.435889894, 0.0],
                }
            )()
        )

    monkeypatch.setattr("intelligence.dedup.import_module", fake_import_module)

    deduplicator = HeadlineDeduplicator()

    assert import_calls == []

    deduplicator.add("Revenue jumps after earnings")

    assert import_calls == ["sentence_transformers"]
    assert deduplicator.is_duplicate("Revenue climbs after quarterly results") is True

    assert import_calls == ["sentence_transformers"]


def test_is_duplicate_detects_exact_headline_match() -> None:
    deduplicator = HeadlineDeduplicator(
        model_factory=_build_model_factory(
            {
                "Microsoft beats expectations": [1.0, 0.0, 0.0],
            }
        )
    )

    deduplicator.add("Microsoft beats expectations")

    assert deduplicator.is_duplicate("Microsoft beats expectations") is True


def test_is_duplicate_detects_semantically_similar_headline() -> None:
    deduplicator = HeadlineDeduplicator(
        model_factory=_build_model_factory(
            {
                "Tesla shares surge after deliveries report": [1.0, 0.0, 0.0],
                "Tesla stock jumps after strong delivery numbers": [0.9, 0.435889894, 0.0],
            }
        )
    )

    deduplicator.add("Tesla shares surge after deliveries report")

    assert deduplicator.is_duplicate("Tesla stock jumps after strong delivery numbers") is True


def test_is_duplicate_allows_dissimilar_headlines() -> None:
    deduplicator = HeadlineDeduplicator(
        model_factory=_build_model_factory(
            {
                "Oil prices climb on supply concerns": [1.0, 0.0, 0.0],
                "Retail sales disappoint in May": [0.0, 1.0, 0.0],
            }
        )
    )

    deduplicator.add("Oil prices climb on supply concerns")

    assert deduplicator.is_duplicate("Retail sales disappoint in May") is False


def test_is_duplicate_uses_configurable_similarity_threshold() -> None:
    embeddings = {
        "Nvidia rallies on AI demand": [1.0, 0.0, 0.0],
        "Nvidia rises as AI demand stays strong": [0.8, 0.6, 0.0],
    }

    strict_deduplicator = HeadlineDeduplicator(
        similarity_threshold=0.85,
        model_factory=_build_model_factory(embeddings),
    )
    lenient_deduplicator = HeadlineDeduplicator(
        similarity_threshold=0.75,
        model_factory=_build_model_factory(embeddings),
    )

    strict_deduplicator.add("Nvidia rallies on AI demand")
    lenient_deduplicator.add("Nvidia rallies on AI demand")

    assert strict_deduplicator.is_duplicate("Nvidia rises as AI demand stays strong") is False
    assert lenient_deduplicator.is_duplicate("Nvidia rises as AI demand stays strong") is True


def test_is_duplicate_evicts_entries_outside_the_time_window() -> None:
    start_time = datetime(2025, 7, 26, tzinfo=UTC)
    clock = FakeClock(start_time)
    deduplicator = HeadlineDeduplicator(
        window_days=7,
        model_factory=_build_model_factory(
            {
                "Apple launches new buyback": [1.0, 0.0, 0.0],
            }
        ),
        clock=clock,
    )

    deduplicator.add("Apple launches new buyback")
    clock.set(start_time + timedelta(days=8))

    assert deduplicator.is_duplicate("Apple launches new buyback") is False


def test_filter_articles_returns_only_non_duplicates_and_adds_embeddings() -> None:
    deduplicator = HeadlineDeduplicator(
        model_factory=_build_model_factory(
            {
                "Meta tops ad revenue forecasts": [1.0, 0.0, 0.0],
                "Meta beats advertising revenue expectations": [0.9, 0.435889894, 0.0],
                "Fed leaves rates unchanged": [0.0, 1.0, 0.0],
            }
        )
    )
    articles = [
        {"id": 1, "title": "Meta tops ad revenue forecasts"},
        {"id": 2, "title": "Meta beats advertising revenue expectations"},
        {"id": 3, "title": "Fed leaves rates unchanged"},
    ]

    filtered_articles = deduplicator.filter_articles(articles)

    assert [article["id"] for article in filtered_articles] == [1, 3]
    assert filtered_articles[0]["headline_embedding"] == [1.0, 0.0, 0.0]
    assert filtered_articles[1]["headline_embedding"] == [0.0, 1.0, 0.0]
    assert all("headline_embedding" not in article for article in articles)
