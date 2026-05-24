"""Seed the instruments table with popular stocks."""

from __future__ import annotations

import asyncio
import logging

from db.connection import close_pool, get_pool

logger = logging.getLogger(__name__)

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
]


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

    logger.info("Seeded %s instruments", len(INSTRUMENTS))
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
