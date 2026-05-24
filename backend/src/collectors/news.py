"""News collection jobs powered by Finnhub."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from config import get_env
from db.connection import get_pool

logger = logging.getLogger(__name__)

_API_URL = "https://finnhub.io/api/v1/company-news"


def _get_date_window() -> tuple[str, str]:
    end_date = datetime.now(tz=UTC).date()
    start_date = end_date - timedelta(days=7)
    return start_date.isoformat(), end_date.isoformat()


def _to_timestamp(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=UTC)
    except (TypeError, ValueError, OSError):
        return None


async def _store_articles(symbol: str, articles: list[dict[str, Any]]) -> int:
    rows: list[tuple[str, str, str, str | None, str, str, datetime | None]] = []
    for article in articles:
        url = article.get("url")
        title = article.get("headline") or article.get("title")
        if not url or not title:
            continue

        metadata = {
            "category": article.get("category"),
            "id": article.get("id"),
            "image": article.get("image"),
            "related": article.get("related"),
            "source_url": url,
        }
        rows.append(
            (
                symbol,
                article.get("source") or "finnhub",
                title,
                article.get("summary"),
                url,
                json.dumps(metadata),
                _to_timestamp(article.get("datetime")),
            )
        )

    if not rows:
        return 0

    inserted_count = 0
    pool = await get_pool()
    async with pool.acquire() as connection:
        for row in rows:
            result = await connection.execute(
                """
                INSERT INTO news (symbol, source, title, summary, url, metadata, published_at)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7)
                ON CONFLICT (url) DO NOTHING
                """,
                *row,
            )
            if result.endswith("1"):
                inserted_count += 1

    return inserted_count


async def collect_news(symbols: list[str]) -> dict[str, int]:
    """Collect news for the provided symbols from Finnhub."""
    api_key = get_env("FINNHUB_API_KEY")
    if not api_key or api_key == "your_key_here":
        logger.warning("Finnhub API key is not configured; skipping news collection")
        return {"processed": 0, "stored": 0}

    start_date, end_date = _get_date_window()
    summary = {"processed": 0, "stored": 0}

    async with httpx.AsyncClient(timeout=30) as client:
        for raw_symbol in symbols:
            symbol = raw_symbol.upper()
            try:
                response = await client.get(
                    _API_URL,
                    params={
                        "symbol": symbol,
                        "from": start_date,
                        "to": end_date,
                        "token": api_key,
                    },
                )
                response.raise_for_status()
                articles = response.json()
                stored_count = await _store_articles(symbol, articles)
                summary["processed"] += 1
                summary["stored"] += stored_count
                logger.info("Collected news for %s (%s articles)", symbol, stored_count)
            except Exception:
                logger.exception("Failed to collect news for %s", symbol)

    return summary
