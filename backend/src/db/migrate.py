"""Apply SQL migrations for the backend database."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import asyncpg

from db.connection import build_connection_string

logger = logging.getLogger(__name__)


def get_migrations_path() -> Path:
    """Return the directory containing SQL migration files."""
    return Path(__file__).resolve().parent / "migrations"


def get_migration_files(migrations_path: Path | None = None) -> list[Path]:
    """Return migration files in filename order."""
    target_path = migrations_path or get_migrations_path()
    return sorted(target_path.glob("*.sql"))


async def ensure_migrations_table(connection: asyncpg.Connection) -> None:
    """Ensure the schema migration tracking table exists."""
    await connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            name TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )


async def get_applied_migrations(connection: asyncpg.Connection) -> set[str]:
    """Return the set of applied migration file names."""
    rows = await connection.fetch("SELECT name FROM schema_migrations")
    return {row["name"] for row in rows}


async def apply_migrations() -> None:
    """Apply any pending SQL migrations in filename order."""
    connection = await asyncpg.connect(dsn=build_connection_string())
    try:
        await ensure_migrations_table(connection)
        applied = await get_applied_migrations(connection)
        migration_files = get_migration_files()

        for migration_file in migration_files:
            if migration_file.name in applied:
                continue

            logger.info("Applying migration %s", migration_file.name)
            sql = migration_file.read_text(encoding="utf-8")
            await connection.execute(sql)
            await connection.execute(
                "INSERT INTO schema_migrations (name) VALUES ($1)",
                migration_file.name,
            )

    finally:
        await connection.close()


async def main() -> None:
    """Run migrations when executed as a script."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    await apply_migrations()


if __name__ == "__main__":
    asyncio.run(main())
