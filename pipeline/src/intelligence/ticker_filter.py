"""Ticker-aware article pre-filter for the intelligence pipeline."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

_AMBIGUOUS_WORD_TICKERS = frozenset({"A", "ALL", "IT"})
_WORD_CHARS_PATTERN = r"[A-Z0-9]"


@dataclass(frozen=True, slots=True)
class _TickerPatterns:
    """Precompiled regex patterns used during ticker matching."""

    cashtag_pattern: re.Pattern[str] | None
    standard_pattern: re.Pattern[str] | None
    ambiguous_pattern: re.Pattern[str] | None


class TickerFilter:
    """Filter articles to those mentioning portfolio tickers."""

    def __init__(
        self,
        tickers: Iterable[str],
        *,
        headline_keys: Sequence[str] = ("title", "headline"),
        body_keys: Sequence[str] = ("body", "content", "article_body", "text"),
        matched_tickers_key: str = "matched_tickers",
    ) -> None:
        self._tickers = _normalize_tickers(tickers)
        self._headline_keys = tuple(headline_keys)
        self._body_keys = tuple(body_keys)
        self._matched_tickers_key = matched_tickers_key
        self._patterns = _build_patterns(self._tickers)

    def matches(self, text: str) -> set[str]:
        """Return the portfolio tickers found within the supplied text."""
        if not text:
            return set()

        matched_tickers: set[str] = set()
        matched_tickers.update(_collect_matches(text, self._patterns.cashtag_pattern, strip_cashtag=True))
        matched_tickers.update(_collect_matches(text, self._patterns.standard_pattern))
        matched_tickers.update(_collect_matches(text, self._patterns.ambiguous_pattern))
        return matched_tickers

    def filter_articles(self, articles: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        """Return only articles that mention portfolio tickers, annotated with the matches."""
        filtered_articles: list[dict[str, Any]] = []

        for article in articles:
            matched_tickers = self.matches(self._article_text(article))
            if not matched_tickers:
                continue

            filtered_articles.append(
                {
                    **dict(article),
                    self._matched_tickers_key: [
                        ticker for ticker in self._tickers if ticker in matched_tickers
                    ],
                }
            )

        return filtered_articles

    def _article_text(self, article: Mapping[str, Any]) -> str:
        headline = _resolve_text(article, self._headline_keys)
        body = _resolve_text(article, self._body_keys)
        return "\n".join(part for part in (headline, body) if part)


def _normalize_tickers(tickers: Iterable[str]) -> tuple[str, ...]:
    ordered_tickers: list[str] = []
    seen_tickers: set[str] = set()

    for ticker in tickers:
        normalized_ticker = str(ticker).strip().upper()
        if not normalized_ticker or normalized_ticker in seen_tickers:
            continue
        ordered_tickers.append(normalized_ticker)
        seen_tickers.add(normalized_ticker)

    return tuple(ordered_tickers)


def _build_patterns(tickers: Sequence[str]) -> _TickerPatterns:
    standard_tickers = [ticker for ticker in tickers if _supports_standard_matching(ticker)]
    ambiguous_tickers = [ticker for ticker in tickers if _requires_ambiguous_matching(ticker)]

    return _TickerPatterns(
        cashtag_pattern=_compile_pattern(tickers, prefix=r"\$", ignore_case=True),
        standard_pattern=_compile_pattern(standard_tickers, ignore_case=True),
        ambiguous_pattern=_compile_pattern(ambiguous_tickers, ignore_case=False),
    )


def _supports_standard_matching(ticker: str) -> bool:
    return len(ticker) >= 2 and ticker not in _AMBIGUOUS_WORD_TICKERS


def _requires_ambiguous_matching(ticker: str) -> bool:
    return len(ticker) >= 2 and ticker in _AMBIGUOUS_WORD_TICKERS


def _compile_pattern(
    tickers: Sequence[str],
    *,
    prefix: str = "",
    ignore_case: bool,
) -> re.Pattern[str] | None:
    if not tickers:
        return None

    ticker_pattern = "|".join(sorted((re.escape(ticker) for ticker in tickers), key=len, reverse=True))
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(
        rf"(?<!{_WORD_CHARS_PATTERN}){prefix}(?:{ticker_pattern})(?!{_WORD_CHARS_PATTERN})",
        flags,
    )


def _collect_matches(
    text: str,
    pattern: re.Pattern[str] | None,
    *,
    strip_cashtag: bool = False,
) -> set[str]:
    if pattern is None:
        return set()

    return {
        match.group(0).lstrip("$").upper() if strip_cashtag else match.group(0).upper()
        for match in pattern.finditer(text)
    }


def _resolve_text(article: Mapping[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = article.get(key)
        if value:
            return str(value)
    return ""
