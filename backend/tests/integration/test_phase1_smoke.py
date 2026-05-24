from __future__ import annotations

import importlib
import inspect
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

import api.app as app_module
from api.routes import health as health_route
from api.routes import instruments as instruments_route
from api.routes import news as news_route
from api.routes import prices as prices_route
from seed import INSTRUMENTS


class FakeConnection:
    def __init__(self) -> None:
        created_at = datetime(2026, 5, 24, 12, 47, 40, tzinfo=UTC)
        price_time = datetime(2026, 5, 23, 20, 0, tzinfo=UTC)
        published_at = datetime(2026, 5, 24, 12, 0, tzinfo=UTC)
        fetched_at = datetime(2026, 5, 24, 12, 5, tzinfo=UTC)
        symbol, name, sector = INSTRUMENTS[0]
        self.instruments = [
            {
                "symbol": symbol,
                "name": name,
                "type": "stock",
                "sector": sector,
                "is_owned": False,
                "created_at": created_at,
            }
        ]
        self.intraday_prices = [
            {
                "time": price_time,
                "open": Decimal("189.12"),
                "high": Decimal("190.45"),
                "low": Decimal("188.97"),
                "close": Decimal("190.11"),
                "volume": 1250000,
            }
        ]
        self.daily_prices = [
            {
                "time": price_time,
                "open": Decimal("187.01"),
                "high": Decimal("191.25"),
                "low": Decimal("186.75"),
                "close": Decimal("190.11"),
                "volume": 5400000,
            }
        ]
        self.news = [
            {
                "symbol": symbol,
                "source": "finnhub",
                "title": f"{symbol} extends Phase 1 smoke test coverage",
                "summary": "Integration verification exercises the Phase 1 API surface.",
                "url": f"https://example.com/{symbol.lower()}-phase1",
                "published_at": published_at,
                "fetched_at": fetched_at,
            }
        ]

    async def fetchval(self, query: str):
        if query.strip() == "SELECT 1":
            return 1
        raise AssertionError(f"Unexpected fetchval query: {query}")

    async def fetch(self, query: str, *args: object):
        normalized_query = " ".join(query.split())
        if "FROM instruments" in normalized_query:
            return self.instruments
        if "FROM prices_intraday" in normalized_query:
            return self.intraday_prices
        if "FROM prices_daily" in normalized_query:
            return self.daily_prices
        if "FROM news" in normalized_query:
            if "WHERE symbol = $1" in normalized_query and args:
                return [row for row in self.news if row["symbol"] == args[0]]
            return self.news
        raise AssertionError(f"Unexpected fetch query: {normalized_query}")


class FakeAcquire:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> FakeConnection:
        return self.connection

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakePool:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    def acquire(self) -> FakeAcquire:
        return FakeAcquire(self.connection)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    pool = FakePool()

    async def get_pool() -> FakePool:
        return pool

    async def close_pool() -> None:
        return None

    monkeypatch.setattr(app_module, "load_environment", lambda: None)
    monkeypatch.setattr(app_module, "get_pool", get_pool)
    monkeypatch.setattr(app_module, "close_pool", close_pool)
    monkeypatch.setattr(health_route, "get_pool", get_pool)
    monkeypatch.setattr(instruments_route, "get_pool", get_pool)
    monkeypatch.setattr(prices_route, "get_pool", get_pool)
    monkeypatch.setattr(news_route, "get_pool", get_pool)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_health_endpoint_returns_200_and_connected_database(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_instruments_endpoint_returns_seeded_instrument_data(client: TestClient) -> None:
    response = client.get("/instruments")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "type": "stock",
            "sector": "Technology",
            "is_owned": False,
            "created_at": "2026-05-24T12:47:40Z",
        }
    ]


def test_prices_endpoint_returns_expected_price_series_schema(client: TestClient) -> None:
    response = client.get("/prices/aapl")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert list(body.keys()) == ["symbol", "intraday", "daily"]
    assert body["intraday"] == [
        {
            "time": "2026-05-23T20:00:00Z",
            "open": 189.12,
            "high": 190.45,
            "low": 188.97,
            "close": 190.11,
            "volume": 1250000,
        }
    ]
    assert body["daily"] == [
        {
            "time": "2026-05-23T20:00:00Z",
            "open": 187.01,
            "high": 191.25,
            "low": 186.75,
            "close": 190.11,
            "volume": 5400000,
        }
    ]


def test_news_endpoint_returns_expected_news_schema(client: TestClient) -> None:
    response = client.get("/news", params={"symbol": "AAPL", "limit": 5})

    assert response.status_code == 200
    assert response.json() == [
        {
            "symbol": "AAPL",
            "source": "finnhub",
            "title": "AAPL extends Phase 1 smoke test coverage",
            "summary": "Integration verification exercises the Phase 1 API surface.",
            "url": "https://example.com/aapl-phase1",
            "published_at": "2026-05-24T12:00:00Z",
            "fetched_at": "2026-05-24T12:05:00Z",
        }
    ]


@pytest.mark.asyncio
async def test_price_collector_runs_with_mocked_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prices_module = importlib.import_module("collectors.prices")
    intraday_rows = [
        (datetime(2026, 5, 23, 20, 0, tzinfo=UTC), "AAPL", 189.12, 190.45, 188.97, 190.11, 1250000)
    ]
    daily_rows = [
        (datetime(2026, 5, 23, 20, 0, tzinfo=UTC), "AAPL", 187.01, 191.25, 186.75, 190.11, 5400000)
    ]
    stored_tables: list[tuple[str, list[object]]] = []

    def fake_get_env(name: str, default: str | None = None) -> str | None:
        if name == "YAHOO_FINANCE_ENABLED":
            return "true"
        return default

    def fake_fetch_symbol_prices(symbol: str) -> tuple[list[object], list[object]]:
        assert symbol == "AAPL"
        return intraday_rows, daily_rows

    async def fake_store_prices(table_name: str, rows: list[object]) -> None:
        stored_tables.append((table_name, rows))

    monkeypatch.setattr(prices_module, "get_env", fake_get_env)
    monkeypatch.setattr(prices_module, "_fetch_symbol_prices", fake_fetch_symbol_prices)
    monkeypatch.setattr(prices_module, "_store_prices", fake_store_prices)

    summary = await prices_module.collect_prices(["aapl"])

    assert summary == {"processed": 1, "intraday": 1, "daily": 1}
    assert stored_tables == [
        ("prices_intraday", intraday_rows),
        ("prices_daily", daily_rows),
    ]
    assert inspect.iscoroutinefunction(prices_module.collect_prices)


def test_collectors_are_importable_and_expose_callable_entrypoints() -> None:
    prices_module = importlib.import_module("collectors.prices")
    news_module = importlib.import_module("collectors.news")

    assert inspect.iscoroutinefunction(prices_module.collect_prices)
    assert inspect.iscoroutinefunction(news_module.collect_news)
    assert callable(prices_module.collect_prices)
    assert callable(news_module.collect_news)
