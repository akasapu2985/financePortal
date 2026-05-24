"""Price collection jobs powered by Yahoo Finance."""

from __future__ import annotations

import asyncio
import logging
import math
from datetime import UTC
from typing import Any

import yfinance as yf

from config import get_env
from db.connection import get_pool

logger = logging.getLogger(__name__)

PriceRow = tuple[object, str, float | None, float | None, float | None, float | None, int | None]


def _normalize_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric_value):
        return None
    return numeric_value


def _normalize_volume(value: Any) -> int | None:
    numeric_value = _normalize_number(value)
    if numeric_value is None:
        return None
    return int(numeric_value)


def _frame_to_rows(symbol: str, frame: Any) -> list[PriceRow]:
    rows: list[PriceRow] = []
    if frame.empty:
        return rows

    for timestamp, candle in frame.iterrows():
        price_time = timestamp.to_pydatetime()
        if price_time.tzinfo is None:
            price_time = price_time.replace(tzinfo=UTC)
        else:
            price_time = price_time.astimezone(UTC)

        rows.append(
            (
                price_time,
                symbol,
                _normalize_number(candle.get("Open")),
                _normalize_number(candle.get("High")),
                _normalize_number(candle.get("Low")),
                _normalize_number(candle.get("Close")),
                _normalize_volume(candle.get("Volume")),
            )
        )
    return rows


def _fetch_symbol_prices(symbol: str) -> tuple[list[PriceRow], list[PriceRow]]:
    ticker = yf.Ticker(symbol)
    intraday = ticker.history(period="1d", interval="5m", auto_adjust=False, actions=False)
    daily = ticker.history(period="3mo", interval="1d", auto_adjust=False, actions=False)
    return _frame_to_rows(symbol, intraday), _frame_to_rows(symbol, daily)


async def _store_prices(table_name: str, rows: list[PriceRow]) -> None:
    if not rows:
        return

    pool = await get_pool()
    query = f"""
        INSERT INTO {table_name} (time, symbol, open, high, low, close, volume)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (symbol, time) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume
    """
    async with pool.acquire() as connection:
        await connection.executemany(query, rows)


async def collect_prices(symbols: list[str]) -> dict[str, int]:
    """Collect intraday and daily prices for the provided symbols."""
    if (get_env("YAHOO_FINANCE_ENABLED", "true") or "true").lower() != "true":
        logger.info("Yahoo Finance collector is disabled")
        return {"processed": 0, "intraday": 0, "daily": 0}

    summary = {"processed": 0, "intraday": 0, "daily": 0}

    for raw_symbol in symbols:
        symbol = raw_symbol.upper()
        try:
            intraday_rows, daily_rows = await asyncio.to_thread(_fetch_symbol_prices, symbol)
            await _store_prices("prices_intraday", intraday_rows)
            await _store_prices("prices_daily", daily_rows)
            summary["processed"] += 1
            summary["intraday"] += len(intraday_rows)
            summary["daily"] += len(daily_rows)
            logger.info(
                "Collected prices for %s (intraday=%s, daily=%s)",
                symbol,
                len(intraday_rows),
                len(daily_rows),
            )
        except Exception:
            logger.exception("Failed to collect prices for %s", symbol)

    return summary
