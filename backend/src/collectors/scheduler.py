"""APScheduler runner for backend collectors."""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime, time
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from collectors.news import collect_news
from collectors.prices import collect_prices
from config import get_env_int, load_environment
from db.connection import close_pool, get_pool

logger = logging.getLogger(__name__)
_MARKET_TIMEZONE = ZoneInfo("America/New_York")


def is_market_hours(current_time: datetime | None = None) -> bool:
    """Return True when the NYSE is open on a regular trading day."""
    now = (
        current_time.astimezone(_MARKET_TIMEZONE)
        if current_time
        else datetime.now(_MARKET_TIMEZONE)
    )
    if now.weekday() > 4:
        return False
    market_open = time(hour=9, minute=30)
    market_close = time(hour=16, minute=0)
    return market_open <= now.time() < market_close


async def get_symbols() -> list[str]:
    """Load tracked symbols from the instruments table."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT symbol FROM instruments ORDER BY symbol")
    return [row["symbol"] for row in rows]


async def run_price_collection() -> None:
    """Collect prices during US market hours."""
    if not is_market_hours():
        logger.info("Skipping price collection outside market hours")
        return

    symbols = await get_symbols()
    if not symbols:
        logger.info("Skipping price collection because no instruments are seeded")
        return

    await collect_prices(symbols)


async def run_news_collection() -> None:
    """Collect the latest news for tracked symbols."""
    symbols = await get_symbols()
    if not symbols:
        logger.info("Skipping news collection because no instruments are seeded")
        return

    await collect_news(symbols)


async def run_scheduler(stop_event: asyncio.Event | None = None) -> None:
    """Start the scheduler and keep it alive until shutdown is requested."""
    load_environment()
    await get_pool()

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        run_price_collection,
        "interval",
        minutes=get_env_int("PRICES_COLLECTION_INTERVAL_MINUTES", 5),
        max_instances=1,
        coalesce=True,
        id="price-collector",
    )
    scheduler.add_job(
        run_news_collection,
        "interval",
        minutes=get_env_int("NEWS_COLLECTION_INTERVAL_MINUTES", 15),
        max_instances=1,
        coalesce=True,
        id="news-collector",
    )
    scheduler.start()
    logger.info("Collector scheduler started")

    shutdown_event = stop_event or asyncio.Event()
    try:
        await run_price_collection()
        await run_news_collection()
        await shutdown_event.wait()
    finally:
        scheduler.shutdown(wait=False)
        await close_pool()
        logger.info("Collector scheduler stopped")


async def main() -> None:
    """Run the scheduler until the process receives a shutdown signal."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signal_name, stop_event.set)
        except NotImplementedError:
            pass
    await run_scheduler(stop_event)


if __name__ == "__main__":
    asyncio.run(main())
