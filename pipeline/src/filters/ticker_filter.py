from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

_BOUNDARY_CLASS = r"A-Z0-9"
_SHORT_TICKER_LENGTH = 2


def _normalize_tickers(portfolio_tickers: Sequence[str]) -> list[str]:
    normalized_tickers: list[str] = []
    seen_tickers: set[str] = set()

    for ticker in portfolio_tickers:
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker or normalized_ticker in seen_tickers:
            continue
        seen_tickers.add(normalized_ticker)
        normalized_tickers.append(normalized_ticker)

    return normalized_tickers


def _compile_ticker_regex(tickers: Sequence[str], *, ignore_case: bool) -> re.Pattern[str] | None:
    if not tickers:
        return None

    alternation = "|".join(re.escape(ticker) for ticker in sorted(tickers, key=len, reverse=True))
    pattern = rf"(?<![{_BOUNDARY_CLASS}])(?:{alternation})(?![{_BOUNDARY_CLASS}])"
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


class TickerFilter:
    def __init__(self, portfolio_tickers: Sequence[str]) -> None:
        self._ordered_tickers = _normalize_tickers(portfolio_tickers)
        self._short_ticker_regex = _compile_ticker_regex(
            [ticker for ticker in self._ordered_tickers if len(ticker) <= _SHORT_TICKER_LENGTH],
            ignore_case=False,
        )
        self._long_ticker_regex = _compile_ticker_regex(
            [ticker for ticker in self._ordered_tickers if len(ticker) > _SHORT_TICKER_LENGTH],
            ignore_case=True,
        )

    def match_text(self, headline: str | None, body: str | None) -> list[str]:
        search_text = "\n".join(part for part in (headline, body) if part)
        if not search_text or not self._ordered_tickers:
            return []

        matched_tickers: set[str] = set()
        for ticker_regex in (self._short_ticker_regex, self._long_ticker_regex):
            if ticker_regex is None:
                continue
            matched_tickers.update(
                match.group(0).upper() for match in ticker_regex.finditer(search_text)
            )

        return [ticker for ticker in self._ordered_tickers if ticker in matched_tickers]

    def match_article(self, article: Mapping[str, Any]) -> dict[str, Any] | None:
        matched_tickers = self.match_text(
            self._get_article_text(article, "headline"),
            self._get_article_text(article, "body"),
        )
        if not matched_tickers:
            return None

        return {**article, "matched_tickers": matched_tickers}

    def filter_articles(self, articles: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        matched_articles: list[dict[str, Any]] = []
        append_match = matched_articles.append

        for article in articles:
            matched_article = self.match_article(article)
            if matched_article is not None:
                append_match(matched_article)

        return matched_articles

    @staticmethod
    def _get_article_text(article: Mapping[str, Any], field_name: str) -> str | None:
        value = article.get(field_name)
        if isinstance(value, str):
            return value
        return None
