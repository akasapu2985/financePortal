"""Seed the instruments table with popular stocks."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence

from db.connection import close_pool, get_pool

logger = logging.getLogger(__name__)

DEFAULT_WATCHLIST_NAME = "My Watchlist"
DEFAULT_WATCHLIST_DESCRIPTION = "Starter symbols for the dashboard"
DEFAULT_WATCHLIST_SYMBOLS = ("MSFT", "MRAM", "DELL", "AMZN")

INSTRUMENTS: list[tuple[str, str, str | None]] = [
    ("AAPL", "Apple Inc.", "Technology"),
    ("MSFT", "Microsoft Corporation", "Technology"),
    ("GOOGL", "Alphabet Inc.", "Communication Services"),
    ("AMZN", "Amazon.com, Inc.", "Consumer Discretionary"),
    ("TSLA", "Tesla, Inc.", "Consumer Discretionary"),
    ("NVDA", "NVIDIA Corporation", "Technology"),
    ("META", "Meta Platforms, Inc.", "Communication Services"),
    ("JPM", "JPMorgan Chase & Co.", "Financials"),
    ("V", "Visa Inc.", "Financials"),
    ("JNJ", "Johnson & Johnson", "Health Care"),
    ("WMT", "Walmart Inc.", "Consumer Staples"),
    ("PG", "Procter & Gamble Co.", "Consumer Staples"),
    ("UNH", "UnitedHealth Group Incorporated", "Health Care"),
    ("HD", "Home Depot, Inc.", "Consumer Discretionary"),
    ("BAC", "Bank of America Corporation", "Financials"),
    ("DIS", "The Walt Disney Company", "Communication Services"),
    ("NFLX", "Netflix, Inc.", "Communication Services"),
    ("AMD", "Advanced Micro Devices, Inc.", "Technology"),
    ("CRM", "Salesforce, Inc.", "Technology"),
    ("PYPL", "PayPal Holdings, Inc.", "Financials"),
    ("MRAM", "Everspin Technologies, Inc.", "Technology"),
    ("DELL", "Dell Technologies Inc.", "Technology"),
]


async def _ensure_default_watchlist(connection: object) -> int:
    existing_row = await connection.fetchrow(
        """
        SELECT id
        FROM watchlists
        WHERE name = $1
        ORDER BY id
        LIMIT 1
        """,
        DEFAULT_WATCHLIST_NAME,
    )
    if existing_row is not None:
        return int(existing_row["id"])

    created_row = await connection.fetchrow(
        """
        INSERT INTO watchlists (name, description)
        VALUES ($1, $2)
        RETURNING id
        """,
        DEFAULT_WATCHLIST_NAME,
        DEFAULT_WATCHLIST_DESCRIPTION,
    )
    if created_row is None:
        raise RuntimeError("Failed to create default watchlist during seed")
    return int(created_row["id"])


async def _add_instruments_to_watchlist(
    connection: object,
    watchlist_id: int,
    symbols: Sequence[str],
) -> int:
    instrument_rows = await connection.fetch(
        """
        SELECT id, symbol
        FROM instruments
        WHERE symbol = ANY($1::varchar[])
        """,
        list(symbols),
    )
    instrument_ids = [int(row["id"]) for row in instrument_rows]
    if len(instrument_ids) != len(symbols):
        found_symbols = {str(row["symbol"]) for row in instrument_rows}
        missing_symbols = sorted(set(symbols) - found_symbols)
        raise RuntimeError(
            "Missing seeded instruments for default watchlist: "
            f"{', '.join(missing_symbols)}"
        )

    await connection.executemany(
        """
        INSERT INTO watchlist_items (watchlist_id, instrument_id)
        VALUES ($1, $2)
        ON CONFLICT (watchlist_id, instrument_id) DO NOTHING
        """,
        [(watchlist_id, instrument_id) for instrument_id in instrument_ids],
    )
    return len(instrument_ids)


async def seed_instruments() -> int:
    """Insert the default instrument universe into PostgreSQL."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        await connection.executemany(
            """
            INSERT INTO instruments (symbol, name, sector)
            VALUES ($1, $2, $3)
            ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                sector = EXCLUDED.sector,
                updated_at = NOW()
            """,
            INSTRUMENTS,
        )
        watchlist_id = await _ensure_default_watchlist(connection)
        seeded_watchlist_items = await _add_instruments_to_watchlist(
            connection,
            watchlist_id,
            DEFAULT_WATCHLIST_SYMBOLS,
        )

    logger.info("Seeded %s instruments", len(INSTRUMENTS))
    logger.info(
        "Ensured default watchlist %s contains %s symbols",
        DEFAULT_WATCHLIST_NAME,
        seeded_watchlist_items,
    )
    return len(INSTRUMENTS)


async def main() -> None:
    """Run the seeding workflow when executed as a script."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        await seed_instruments()
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
