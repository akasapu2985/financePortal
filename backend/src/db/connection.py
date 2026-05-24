"""Database connection helpers backed by asyncpg."""

from __future__ import annotations

import logging
from typing import Final
from urllib.parse import quote_plus

import asyncpg

from config import get_env, load_environment

logger = logging.getLogger(__name__)

_POOL_MIN_SIZE: Final[int] = 2
_POOL_MAX_SIZE: Final[int] = 10
_pool: asyncpg.Pool | None = None


def build_connection_string() -> str:
    """Build a PostgreSQL connection string from environment variables."""
    load_environment()
    host = get_env("POSTGRES_HOST", "localhost") or "localhost"
    port = int(get_env("POSTGRES_PORT", "5432") or "5432")
    database = get_env("POSTGRES_DB", "financeportal") or "financeportal"
    user = get_env("POSTGRES_USER", "finance") or "finance"
    password = quote_plus(get_env("POSTGRES_PASSWORD", "localdev123") or "localdev123")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


async def get_pool() -> asyncpg.Pool:
    """Create and return the shared asyncpg pool."""
    global _pool
    if _pool is None:
        logger.info("Creating PostgreSQL pool")
        _pool = await asyncpg.create_pool(
            dsn=build_connection_string(),
            min_size=_POOL_MIN_SIZE,
            max_size=_POOL_MAX_SIZE,
            command_timeout=60,
        )
    return _pool


async def close_pool() -> None:
    """Close the shared asyncpg pool if it exists."""
    global _pool
    if _pool is not None:
        logger.info("Closing PostgreSQL pool")
        await _pool.close()
        _pool = None
