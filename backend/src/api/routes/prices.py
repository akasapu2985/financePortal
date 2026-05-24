"""Price routes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db.connection import get_pool

router = APIRouter(tags=["prices"])


class PricePoint(BaseModel):
    time: datetime
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: int | None


class PriceSeriesResponse(BaseModel):
    symbol: str
    intraday: list[PricePoint]
    daily: list[PricePoint]


def _to_float(value: Decimal | float | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _to_price_point(row: dict[str, object]) -> PricePoint:
    return PricePoint(
        time=row["time"],
        open=_to_float(row["open"]),
        high=_to_float(row["high"]),
        low=_to_float(row["low"]),
        close=_to_float(row["close"]),
        volume=row["volume"],
    )


@router.get("/prices/{symbol}", response_model=PriceSeriesResponse)
async def get_prices(
    symbol: str,
    intraday_limit: int = Query(default=78, ge=1, le=500),
    daily_limit: int = Query(default=90, ge=1, le=365),
) -> PriceSeriesResponse:
    """Return intraday and daily price history for a symbol."""
    normalized_symbol = symbol.upper()
    pool = await get_pool()
    async with pool.acquire() as connection:
        intraday_rows = await connection.fetch(
            """
            SELECT time, open, high, low, close, volume
            FROM prices_intraday
            WHERE symbol = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            normalized_symbol,
            intraday_limit,
        )
        daily_rows = await connection.fetch(
            """
            SELECT time, open, high, low, close, volume
            FROM prices_daily
            WHERE symbol = $1
            ORDER BY time DESC
            LIMIT $2
            """,
            normalized_symbol,
            daily_limit,
        )

    if not intraday_rows and not daily_rows:
        raise HTTPException(status_code=404, detail=f"No prices found for {normalized_symbol}")

    return PriceSeriesResponse(
        symbol=normalized_symbol,
        intraday=[_to_price_point(dict(row)) for row in intraday_rows],
        daily=[_to_price_point(dict(row)) for row in daily_rows],
    )
