from __future__ import annotations

from typing import Any

import pytest

import seed as seed_module


class FakeConnection:
    def __init__(self) -> None:
        self.instrument_ids: dict[str, int] = {"AAPL": 1, "MSFT": 2, "AMZN": 3}
        self.watchlists: dict[int, dict[str, Any]] = {}
        self.watchlist_items: dict[int, set[int]] = {}
        self.next_instrument_id = 4
        self.next_watchlist_id = 1

    async def executemany(self, query: str, rows: list[tuple[Any, ...]]) -> None:
        normalized_query = " ".join(query.split())
        if normalized_query.startswith("INSERT INTO instruments"):
            for symbol, _name, _sector in rows:
                if symbol not in self.instrument_ids:
                    self.instrument_ids[symbol] = self.next_instrument_id
                    self.next_instrument_id += 1
            return
        if normalized_query.startswith("INSERT INTO watchlist_items"):
            for watchlist_id, instrument_id in rows:
                self.watchlist_items.setdefault(int(watchlist_id), set()).add(int(instrument_id))
            return
        raise AssertionError(f"Unexpected executemany query: {normalized_query}")

    async def fetchrow(self, query: str, *args: object) -> dict[str, Any] | None:
        normalized_query = " ".join(query.split())
        if normalized_query.startswith("SELECT id FROM watchlists"):
            target_name = str(args[0])
            return next(
                (
                    {"id": watchlist_id}
                    for watchlist_id, watchlist in self.watchlists.items()
                    if watchlist["name"] == target_name
                ),
                None,
            )
        if normalized_query.startswith("INSERT INTO watchlists"):
            watchlist_id = self.next_watchlist_id
            self.next_watchlist_id += 1
            self.watchlists[watchlist_id] = {
                "id": watchlist_id,
                "name": args[0],
                "description": args[1],
            }
            self.watchlist_items.setdefault(watchlist_id, set())
            return {"id": watchlist_id}
        raise AssertionError(f"Unexpected fetchrow query: {normalized_query}")

    async def fetch(self, query: str, *args: object) -> list[dict[str, Any]]:
        normalized_query = " ".join(query.split())
        if normalized_query.startswith("SELECT id, symbol FROM instruments"):
            requested_symbols = set(args[0])
            return [
                {"id": instrument_id, "symbol": symbol}
                for symbol, instrument_id in self.instrument_ids.items()
                if symbol in requested_symbols
            ]
        raise AssertionError(f"Unexpected fetch query: {normalized_query}")


class FakeAcquire:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> FakeConnection:
        return self.connection

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakePool:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def acquire(self) -> FakeAcquire:
        return FakeAcquire(self.connection)


@pytest.mark.asyncio
async def test_seed_instruments_creates_default_watchlist_with_dashboard_symbols(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = FakeConnection()
    pool = FakePool(connection)

    async def get_pool() -> FakePool:
        return pool

    monkeypatch.setattr(seed_module, "get_pool", get_pool)

    seeded_count = await seed_module.seed_instruments()

    assert seeded_count == len(seed_module.INSTRUMENTS)
    assert {"MSFT", "MRAM", "DELL", "AMZN"}.issubset(connection.instrument_ids)
    assert connection.watchlists == {
        1: {
            "id": 1,
            "name": seed_module.DEFAULT_WATCHLIST_NAME,
            "description": seed_module.DEFAULT_WATCHLIST_DESCRIPTION,
        }
    }
    assert connection.watchlist_items == {
        1: {
            connection.instrument_ids["MSFT"],
            connection.instrument_ids["MRAM"],
            connection.instrument_ids["DELL"],
            connection.instrument_ids["AMZN"],
        }
    }


@pytest.mark.asyncio
async def test_seed_instruments_reuses_existing_default_watchlist_without_duplicates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = FakeConnection()
    connection.watchlists[7] = {
        "id": 7,
        "name": seed_module.DEFAULT_WATCHLIST_NAME,
        "description": "Existing default watchlist",
    }
    connection.watchlist_items[7] = {connection.instrument_ids["MSFT"]}
    connection.next_watchlist_id = 8
    pool = FakePool(connection)

    async def get_pool() -> FakePool:
        return pool

    monkeypatch.setattr(seed_module, "get_pool", get_pool)

    await seed_module.seed_instruments()

    assert set(connection.watchlists) == {7}
    assert connection.watchlist_items[7] == {
        connection.instrument_ids["MSFT"],
        connection.instrument_ids["MRAM"],
        connection.instrument_ids["DELL"],
        connection.instrument_ids["AMZN"],
    }
