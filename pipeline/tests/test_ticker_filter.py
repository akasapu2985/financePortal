from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter

import pytest

PIPELINE_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PIPELINE_SRC) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SRC))

from filters.ticker_filter import TickerFilter  # noqa: E402


@pytest.fixture
def sample_article() -> dict[str, str]:
    return {
        "headline": "Analysts say Apple can keep climbing",
        "body": "AAPL rose after the company beat revenue expectations.",
        "url": "https://example.com/article",
    }


def test_match_article_returns_article_with_exact_matches(sample_article: dict[str, str]) -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT"])

    matched_article = ticker_filter.match_article(sample_article)

    assert matched_article == {
        "headline": sample_article["headline"],
        "body": sample_article["body"],
        "url": sample_article["url"],
        "matched_tickers": ["AAPL"],
    }


def test_match_article_avoids_word_boundary_false_positives_for_short_tickers() -> None:
    ticker_filter = TickerFilter(["A", "AA", "AAPL"])
    article = {
        "headline": "A upgrades AAPL while Alpha expands",
        "body": "Analysts expect AA to recover after a difficult quarter.",
    }

    matched_article = ticker_filter.match_article(article)

    assert matched_article is not None
    assert matched_article["matched_tickers"] == ["A", "AA", "AAPL"]


def test_filter_articles_returns_multiple_tickers_in_portfolio_order() -> None:
    ticker_filter = TickerFilter(["MSFT", "AAPL", "NVDA"])
    articles = [
        {
            "headline": "NVDA and AAPL rally while MSFT holds steady",
            "body": "MSFT closed flat after AAPL extended gains.",
            "id": "article-1",
        }
    ]

    matched_articles = ticker_filter.filter_articles(articles)

    assert matched_articles == [
        {
            "headline": "NVDA and AAPL rally while MSFT holds steady",
            "body": "MSFT closed flat after AAPL extended gains.",
            "id": "article-1",
            "matched_tickers": ["MSFT", "AAPL", "NVDA"],
        }
    ]


def test_filter_articles_skips_articles_without_matches() -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT"])
    articles = [
        {"headline": "Treasury yields rise", "body": "Macro concerns weighed on sentiment."},
        {"headline": "Commodities pull back", "body": "Oil and copper slipped overnight."},
    ]

    assert ticker_filter.filter_articles(articles) == []


def test_filter_articles_processes_at_least_one_thousand_articles_per_second() -> None:
    tickers = [f"TKR{index:03d}" for index in range(50)]
    ticker_filter = TickerFilter(tickers)
    articles = [
        {
            "headline": f"Market update for TKR{index % 50:03d}",
            "body": "Momentum stays positive while earnings estimates improve. " * 4,
            "id": str(index),
        }
        for index in range(5000)
    ]

    ticker_filter.filter_articles(articles[:100])

    started_at = perf_counter()
    matched_articles = ticker_filter.filter_articles(articles)
    elapsed_seconds = perf_counter() - started_at
    throughput = len(articles) / elapsed_seconds

    assert len(matched_articles) == len(articles)
    assert throughput >= 1000, f"Expected >= 1000 articles/sec, got {throughput:.2f}"
