from __future__ import annotations

import importlib
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

import api.app as app_module


class FakeConnection:
    def __init__(self) -> None:
        timestamp = datetime(2026, 5, 24, 12, 47, 40, tzinfo=UTC)
        self.instruments: dict[str, dict[str, Any]] = {
            "AAPL": {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "type": "stock",
                "sector": "Technology",
                "is_owned": False,
                "created_at": timestamp,
            },
            "MSFT": {
                "id": 2,
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "type": "stock",
                "sector": "Technology",
                "is_owned": False,
                "created_at": timestamp,
            },
        }
        self.watchlists: dict[int, dict[str, Any]] = {
            1: {
                "id": 1,
                "name": "Big Tech",
                "description": "Core technology holdings",
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        }
        self.watchlist_items: dict[int, dict[int, datetime]] = {1: {1: timestamp}}
        self.next_watchlist_id = 2

    async def fetch(self, query: str, *args: object) -> list[dict[str, Any]]:
        normalized_query = " ".join(query.split())
        if (
            "FROM watchlists AS w" in normalized_query
            and "COUNT(wi.instrument_id)" in normalized_query
        ):
            rows = []
            for watchlist in sorted(
                self.watchlists.values(),
                key=lambda item: (item["name"], item["id"]),
            ):
                rows.append(
                    {
                        **watchlist,
                        "instrument_count": len(self.watchlist_items.get(watchlist["id"], {})),
                    }
                )
            return rows
        if (
            "FROM watchlist_items AS wi" in normalized_query
            and "JOIN instruments AS i" in normalized_query
        ):
            watchlist_id = int(args[0])
            membership = self.watchlist_items.get(watchlist_id, {})
            rows = []
            for instrument_id, added_at in sorted(membership.items()):
                instrument = next(
                    value for value in self.instruments.values() if value["id"] == instrument_id
                )
                rows.append(
                    {
                        "symbol": instrument["symbol"],
                        "name": instrument["name"],
                        "type": instrument["type"],
                        "sector": instrument["sector"],
                        "is_owned": instrument["is_owned"],
                        "created_at": instrument["created_at"],
                        "added_at": added_at,
                    }
                )
            return rows
        raise AssertionError(f"Unexpected fetch query: {normalized_query}")

    async def fetchrow(self, query: str, *args: object) -> dict[str, Any] | None:
        normalized_query = " ".join(query.split())
        if normalized_query.startswith("INSERT INTO watchlists"):
            watchlist_id = self.next_watchlist_id
            self.next_watchlist_id += 1
            timestamp = datetime(2026, 5, 24, 13, 0, 0, tzinfo=UTC)
            watchlist = {
                "id": watchlist_id,
                "name": args[0],
                "description": args[1],
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            self.watchlists[watchlist_id] = watchlist
            self.watchlist_items[watchlist_id] = {}
            return watchlist
        if normalized_query.startswith("UPDATE watchlists"):
            watchlist_id = int(args[2])
            watchlist = self.watchlists.get(watchlist_id)
            if watchlist is None:
                return None
            timestamp = datetime(2026, 5, 24, 13, 5, 0, tzinfo=UTC)
            watchlist.update(name=args[0], description=args[1], updated_at=timestamp)
            return watchlist
        if "FROM watchlists" in normalized_query and "WHERE id = $1" in normalized_query:
            watchlist_id = int(args[0])
            return self.watchlists.get(watchlist_id)
        if "FROM instruments" in normalized_query and "WHERE symbol = $1" in normalized_query:
            return self.instruments.get(str(args[0]))
        if (
            "FROM watchlist_items" in normalized_query
            and "WHERE watchlist_id = $1" in normalized_query
        ):
            watchlist_id = int(args[0])
            instrument_id = int(args[1])
            if instrument_id in self.watchlist_items.get(watchlist_id, {}):
                return {"exists": 1}
            return None
        raise AssertionError(f"Unexpected fetchrow query: {normalized_query}")

    async def execute(self, query: str, *args: object) -> str:
        normalized_query = " ".join(query.split())
        if normalized_query.startswith("DELETE FROM watchlists"):
            watchlist_id = int(args[0])
            if self.watchlists.pop(watchlist_id, None) is None:
                return "DELETE 0"
            self.watchlist_items.pop(watchlist_id, None)
            return "DELETE 1"
        if normalized_query.startswith("INSERT INTO watchlist_items"):
            watchlist_id = int(args[0])
            instrument_id = int(args[1])
            self.watchlist_items.setdefault(watchlist_id, {})[instrument_id] = datetime(
                2026, 5, 24, 13, 10, 0, tzinfo=UTC
            )
            return "INSERT 0 1"
        if normalized_query.startswith("DELETE FROM watchlist_items"):
            watchlist_id = int(args[0])
            instrument_id = int(args[1])
            membership = self.watchlist_items.get(watchlist_id, {})
            if instrument_id not in membership:
                return "DELETE 0"
            del membership[instrument_id]
            return "DELETE 1"
        raise AssertionError(f"Unexpected execute query: {normalized_query}")


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

    try:
        watchlists_route = importlib.import_module("api.routes.watchlists")
    except ModuleNotFoundError:
        watchlists_route = None

    if watchlists_route is not None:
        monkeypatch.setattr(watchlists_route, "get_pool", get_pool)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_list_watchlists_returns_existing_watchlists(client: TestClient) -> None:
    response = client.get("/watchlists")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Big Tech",
            "description": "Core technology holdings",
            "created_at": "2026-05-24T12:47:40Z",
            "updated_at": "2026-05-24T12:47:40Z",
            "instrument_count": 1,
        }
    ]


def test_create_watchlist_requires_non_empty_name_and_returns_created_watchlist(
    client: TestClient,
) -> None:
    invalid_response = client.post("/watchlists", json={"name": "  "})
    response = client.post(
        "/watchlists",
        json={"name": "Dividend Ideas", "description": "Income-focused setup"},
    )

    assert invalid_response.status_code == 422
    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "name": "Dividend Ideas",
        "description": "Income-focused setup",
        "created_at": "2026-05-24T13:00:00Z",
        "updated_at": "2026-05-24T13:00:00Z",
        "instrument_count": 0,
        "instruments": [],
    }


def test_get_watchlist_returns_instruments_and_404_for_missing_watchlist(
    client: TestClient,
) -> None:
    response = client.get("/watchlists/1")
    missing_response = client.get("/watchlists/999")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Big Tech",
        "description": "Core technology holdings",
        "created_at": "2026-05-24T12:47:40Z",
        "updated_at": "2026-05-24T12:47:40Z",
        "instrument_count": 1,
        "instruments": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "type": "stock",
                "sector": "Technology",
                "is_owned": False,
                "created_at": "2026-05-24T12:47:40Z",
                "added_at": "2026-05-24T12:47:40Z",
            }
        ],
    }
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Watchlist 999 not found"}


def test_update_watchlist_updates_name_and_description(client: TestClient) -> None:
    response = client.put(
        "/watchlists/1",
        json={"name": "Mega Cap Tech", "description": "Updated description"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Mega Cap Tech"
    assert response.json()["description"] == "Updated description"
    assert response.json()["updated_at"] == "2026-05-24T13:05:00Z"


def test_delete_watchlist_returns_204_and_removes_the_watchlist(client: TestClient) -> None:
    delete_response = client.delete("/watchlists/1")
    get_response = client.get("/watchlists/1")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_add_instrument_validates_symbol_and_rejects_duplicates(client: TestClient) -> None:
    invalid_response = client.post("/watchlists/1/instruments", json={"symbol": "  "})
    missing_response = client.post("/watchlists/1/instruments", json={"symbol": "NVDA"})
    duplicate_response = client.post("/watchlists/1/instruments", json={"symbol": "AAPL"})
    success_response = client.post("/watchlists/1/instruments", json={"symbol": "MSFT"})

    assert invalid_response.status_code == 422
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Instrument NVDA not found"}
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "Instrument AAPL already exists in watchlist 1"}
    assert success_response.status_code == 200
    assert [instrument["symbol"] for instrument in success_response.json()["instruments"]] == [
        "AAPL",
        "MSFT",
    ]
    assert success_response.json()["instrument_count"] == 2


def test_remove_instrument_removes_membership_and_handles_missing_records(
    client: TestClient,
) -> None:
    missing_watchlist = client.request(
        "DELETE",
        "/watchlists/999/instruments",
        json={"symbol": "AAPL"},
    )
    missing_instrument = client.request(
        "DELETE",
        "/watchlists/1/instruments",
        json={"symbol": "NVDA"},
    )
    missing_membership = client.request(
        "DELETE",
        "/watchlists/1/instruments",
        json={"symbol": "MSFT"},
    )
    success_response = client.request(
        "DELETE",
        "/watchlists/1/instruments",
        json={"symbol": "AAPL"},
    )
    legacy_success_response = client.delete("/watchlists/1/instruments/AAPL")

    assert missing_watchlist.status_code == 404
    assert missing_watchlist.json() == {"detail": "Watchlist 999 not found"}
    assert missing_instrument.status_code == 404
    assert missing_instrument.json() == {"detail": "Instrument NVDA not found"}
    assert missing_membership.status_code == 404
    assert missing_membership.json() == {"detail": "Instrument MSFT is not in watchlist 1"}
    assert success_response.status_code == 200
    assert success_response.json()["instrument_count"] == 0
    assert success_response.json()["instruments"] == []
    assert legacy_success_response.status_code == 404
    assert legacy_success_response.json() == {"detail": "Instrument AAPL is not in watchlist 1"}
