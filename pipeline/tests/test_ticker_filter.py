from __future__ import annotations

import time

from intelligence.ticker_filter import TickerFilter


def test_matches_cashtag_in_headline() -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT"])

    matched = ticker_filter.matches("$AAPL jumps after earnings beat")

    assert matched == {"AAPL"}


def test_filter_articles_matches_body_text() -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT"])
    articles = [
        {
            "id": 1,
            "title": "Market recap",
            "body": "Analysts said Microsoft (MSFT) could benefit from enterprise AI demand.",
        }
    ]

    filtered_articles = ticker_filter.filter_articles(articles)

    assert filtered_articles == [
        {
            "id": 1,
            "title": "Market recap",
            "body": "Analysts said Microsoft (MSFT) could benefit from enterprise AI demand.",
            "matched_tickers": ["MSFT"],
        }
    ]


def test_filter_articles_returns_multiple_matched_tickers() -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT", "NVDA"])
    articles = [
        {
            "id": 1,
            "title": "$AAPL suppliers rally",
            "body": "MSFT and NVDA were also mentioned by analysts.",
        }
    ]

    filtered_articles = ticker_filter.filter_articles(articles)

    assert filtered_articles[0]["matched_tickers"] == ["AAPL", "MSFT", "NVDA"]


def test_filter_articles_returns_empty_when_no_tickers_match() -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT"])

    filtered_articles = ticker_filter.filter_articles(
        [{"id": 1, "title": "Macro update", "body": "Treasury yields rose modestly."}]
    )

    assert filtered_articles == []


def test_matches_are_case_insensitive_for_non_ambiguous_tickers() -> None:
    ticker_filter = TickerFilter(["AAPL"])

    matched = ticker_filter.matches("aapl suppliers gained after the product launch")

    assert matched == {"AAPL"}


def test_word_boundaries_do_not_match_partial_words() -> None:
    ticker_filter = TickerFilter(["AMP"])

    matched = ticker_filter.matches("SAMPLE portfolios rotated between sectors")

    assert matched == set()


def test_short_or_common_word_tickers_require_cashtag_or_exact_uppercase_symbol() -> None:
    ticker_filter = TickerFilter(["A", "IT", "ALL"])

    assert ticker_filter.matches("We discussed it all during the meeting.") == set()
    assert ticker_filter.matches("$A rose after the open while $IT stayed flat.") == {"A", "IT"}
    assert ticker_filter.matches("ALL raised its dividend guidance.") == {"ALL"}


def test_filter_articles_processes_one_thousand_articles_within_one_second() -> None:
    ticker_filter = TickerFilter(["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"])
    articles = [
        {
            "id": index,
            "title": "Portfolio update",
            "body": f"Analysts mentioned AAPL and NVDA in article {index}.",
        }
        for index in range(1000)
    ]

    started_at = time.perf_counter()
    filtered_articles = ticker_filter.filter_articles(articles)
    elapsed_seconds = time.perf_counter() - started_at

    assert len(filtered_articles) == 1000
    assert elapsed_seconds < 1.0
