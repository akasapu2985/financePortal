from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

CURRENT_TIMESTAMP = datetime.fromisoformat("2026-05-25T15:28:43-07:00")
REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "pipeline" / "src" / "filters" / "deduplication.py"


@dataclass
class FakeModel:
    embeddings: dict[str, list[float]]

    def encode(self, headline: str, **_: Any) -> list[float]:
        return self.embeddings[headline]


def load_deduplication_module():
    assert MODULE_PATH.exists(), f"Expected deduplication module at {MODULE_PATH}"

    spec = importlib.util.spec_from_file_location("pipeline_deduplication", MODULE_PATH)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_unique_articles_pass_through() -> None:
    module = load_deduplication_module()
    deduplicator = module.HeadlineDeduplicator(
        model=FakeModel(
            {
                "Nvidia launches new enterprise AI platform": [1.0, 0.0, 0.0],
                "Apple opens new retail store in Miami": [0.0, 1.0, 0.0],
            }
        )
    )
    recent_articles = [
        module.StoredArticle(
            article_id="article-1",
            headline="Apple opens new retail store in Miami",
            embedding=[0.0, 1.0, 0.0],
            published_at=CURRENT_TIMESTAMP - timedelta(days=1),
        )
    ]

    result = deduplicator.evaluate(
        "Nvidia launches new enterprise AI platform",
        recent_articles,
        now=CURRENT_TIMESTAMP,
    )

    assert result.is_duplicate is False
    assert result.match is None
    assert result.embedding == [1.0, 0.0, 0.0]


def test_similar_headlines_are_detected_as_duplicates() -> None:
    module = load_deduplication_module()
    deduplicator = module.HeadlineDeduplicator(
        model=FakeModel(
            {
                "Tesla shares rally after delivery report": [1.0, 0.0, 0.0],
            }
        )
    )
    recent_articles = [
        module.StoredArticle(
            article_id="article-2",
            headline="Tesla stock jumps after strong delivery numbers",
            embedding=[0.92, 0.08, 0.0],
            published_at=CURRENT_TIMESTAMP - timedelta(hours=6),
        )
    ]

    result = deduplicator.evaluate(
        "Tesla shares rally after delivery report",
        recent_articles,
        now=CURRENT_TIMESTAMP,
    )

    assert result.is_duplicate is True
    assert result.match is not None
    assert result.match.article_id == "article-2"
    assert result.match.headline == "Tesla stock jumps after strong delivery numbers"
    assert result.match.similarity > 0.85


def test_similarity_threshold_is_configurable() -> None:
    module = load_deduplication_module()
    recent_articles = [
        module.StoredArticle(
            article_id="article-3",
            headline="Microsoft expands cloud security offering",
            embedding=[0.9, 0.4358898943540673, 0.0],
            published_at=CURRENT_TIMESTAMP - timedelta(days=2),
        )
    ]

    strict_deduplicator = module.HeadlineDeduplicator(
        similarity_threshold=0.95,
        model=FakeModel(
            {
                "Microsoft launches new cloud security tool": [1.0, 0.0, 0.0],
            }
        ),
    )
    relaxed_deduplicator = module.HeadlineDeduplicator(
        similarity_threshold=0.85,
        model=FakeModel(
            {
                "Microsoft launches new cloud security tool": [1.0, 0.0, 0.0],
            }
        ),
    )

    strict_result = strict_deduplicator.evaluate(
        "Microsoft launches new cloud security tool",
        recent_articles,
        now=CURRENT_TIMESTAMP,
    )
    relaxed_result = relaxed_deduplicator.evaluate(
        "Microsoft launches new cloud security tool",
        recent_articles,
        now=CURRENT_TIMESTAMP,
    )

    assert strict_result.is_duplicate is False
    assert relaxed_result.is_duplicate is True
    assert relaxed_result.match is not None
    assert 0.85 < relaxed_result.match.similarity < 0.95


def test_empty_corpus_returns_non_duplicate_result() -> None:
    module = load_deduplication_module()
    deduplicator = module.HeadlineDeduplicator(
        model=FakeModel(
            {
                "Amazon announces warehouse robotics upgrade": [0.2, 0.8, 0.0],
            }
        )
    )

    result = deduplicator.evaluate(
        "Amazon announces warehouse robotics upgrade",
        [],
        now=CURRENT_TIMESTAMP,
    )

    assert result.is_duplicate is False
    assert result.match is None
    assert result.embedding == [0.2, 0.8, 0.0]


def test_ignores_articles_older_than_lookback_window() -> None:
    module = load_deduplication_module()
    deduplicator = module.HeadlineDeduplicator(
        model=FakeModel(
            {
                "Meta debuts AI ad targeting tools": [1.0, 0.0, 0.0],
            }
        )
    )
    recent_articles = [
        module.StoredArticle(
            article_id="article-4",
            headline="Meta unveils AI tools for advertisers",
            embedding=[0.99, 0.01, 0.0],
            published_at=CURRENT_TIMESTAMP - timedelta(days=8),
        )
    ]

    result = deduplicator.evaluate(
        "Meta debuts AI ad targeting tools",
        recent_articles,
        now=CURRENT_TIMESTAMP,
    )

    assert result.is_duplicate is False
    assert result.match is None


def test_naive_published_at_values_do_not_crash_lookback_comparison() -> None:
    module = load_deduplication_module()
    deduplicator = module.HeadlineDeduplicator(
        model=FakeModel(
            {
                "Broadcom raises full-year AI revenue outlook": [1.0, 0.0, 0.0],
            }
        )
    )
    recent_articles = [
        module.StoredArticle(
            article_id="article-5",
            headline="Broadcom lifts annual AI revenue forecast",
            embedding=[0.99, 0.01, 0.0],
            published_at=(CURRENT_TIMESTAMP - timedelta(hours=1)).replace(tzinfo=None),
        )
    ]

    result = deduplicator.evaluate(
        "Broadcom raises full-year AI revenue outlook",
        recent_articles,
        now=CURRENT_TIMESTAMP,
    )

    assert result.is_duplicate is True
    assert result.match is not None
    assert result.match.article_id == "article-5"
