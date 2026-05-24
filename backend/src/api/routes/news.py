"""News routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel

from db.connection import get_pool

router = APIRouter(tags=["news"])


class NewsItemResponse(BaseModel):
    symbol: str
    source: str
    title: str
    summary: str | None
    url: str
    published_at: datetime | None
    fetched_at: datetime


@router.get("/news", response_model=list[NewsItemResponse])
async def list_news(
    symbol: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[NewsItemResponse]:
    """Return the latest news articles, optionally filtered by symbol."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        if symbol:
            rows = await connection.fetch(
                """
                SELECT symbol, source, title, summary, url, published_at, fetched_at
                FROM news
                WHERE symbol = $1
                ORDER BY published_at DESC NULLS LAST, fetched_at DESC
                LIMIT $2
                """,
                symbol.upper(),
                limit,
            )
        else:
            rows = await connection.fetch(
                """
                SELECT symbol, source, title, summary, url, published_at, fetched_at
                FROM news
                ORDER BY published_at DESC NULLS LAST, fetched_at DESC
                LIMIT $1
                """,
                limit,
            )

    return [NewsItemResponse(**dict(row)) for row in rows]
