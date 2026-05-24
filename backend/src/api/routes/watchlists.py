"""Watchlist CRUD routes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from db.connection import get_pool

router = APIRouter(prefix="/watchlists", tags=["watchlists"])

NonEmptyWatchlistName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]
NonEmptySymbol = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=16),
]

_LIST_WATCHLISTS_QUERY = """
SELECT w.id, w.name, w.description, w.created_at, w.updated_at,
       COUNT(wi.instrument_id)::int AS instrument_count
FROM watchlists AS w
LEFT JOIN watchlist_items AS wi ON wi.watchlist_id = w.id
GROUP BY w.id
ORDER BY w.name, w.id
"""
_GET_WATCHLIST_QUERY = """
SELECT id, name, description, created_at, updated_at
FROM watchlists
WHERE id = $1
"""
_CREATE_WATCHLIST_QUERY = """
INSERT INTO watchlists (name, description)
VALUES ($1, $2)
RETURNING id, name, description, created_at, updated_at
"""
_UPDATE_WATCHLIST_QUERY = """
UPDATE watchlists
SET name = $1,
    description = $2,
    updated_at = NOW()
WHERE id = $3
RETURNING id, name, description, created_at, updated_at
"""
_LIST_WATCHLIST_INSTRUMENTS_QUERY = """
SELECT i.symbol, i.name, i.type, i.sector, i.is_owned, i.created_at, wi.added_at
FROM watchlist_items AS wi
JOIN instruments AS i ON i.id = wi.instrument_id
WHERE wi.watchlist_id = $1
ORDER BY i.symbol
"""
_GET_INSTRUMENT_QUERY = """
SELECT id, symbol, name, type, sector, is_owned, created_at
FROM instruments
WHERE symbol = $1
"""
_GET_WATCHLIST_MEMBERSHIP_QUERY = """
SELECT 1 AS exists
FROM watchlist_items
WHERE watchlist_id = $1 AND instrument_id = $2
"""
_INSERT_WATCHLIST_INSTRUMENT_QUERY = """
INSERT INTO watchlist_items (watchlist_id, instrument_id)
VALUES ($1, $2)
"""
_DELETE_WATCHLIST_QUERY = """
DELETE FROM watchlists
WHERE id = $1
"""
_DELETE_WATCHLIST_INSTRUMENT_QUERY = """
DELETE FROM watchlist_items
WHERE watchlist_id = $1 AND instrument_id = $2
"""


class WatchlistWriteRequest(BaseModel):
    """Payload used to create or update a watchlist."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: NonEmptyWatchlistName
    description: str | None = None


class WatchlistInstrumentWriteRequest(BaseModel):
    """Payload used to add an instrument to a watchlist."""

    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: NonEmptySymbol

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        """Store instrument symbols in uppercase."""
        return value.upper()


class WatchlistInstrumentResponse(BaseModel):
    symbol: str
    name: str
    type: str
    sector: str | None
    is_owned: bool
    created_at: datetime
    added_at: datetime


class WatchlistSummaryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    instrument_count: int


class WatchlistDetailResponse(WatchlistSummaryResponse):
    instruments: list[WatchlistInstrumentResponse]


async def _fetch_watchlist_row(connection: Any, watchlist_id: int) -> dict[str, Any]:
    watchlist_row = await connection.fetchrow(_GET_WATCHLIST_QUERY, watchlist_id)
    if watchlist_row is None:
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
    return dict(watchlist_row)


async def _fetch_instrument_row(connection: Any, symbol: str) -> dict[str, Any]:
    instrument_row = await connection.fetchrow(_GET_INSTRUMENT_QUERY, symbol)
    if instrument_row is None:
        raise HTTPException(status_code=404, detail=f"Instrument {symbol} not found")
    return dict(instrument_row)


async def _build_watchlist_detail(connection: Any, watchlist_id: int) -> WatchlistDetailResponse:
    watchlist_row = await _fetch_watchlist_row(connection, watchlist_id)
    instrument_rows = await connection.fetch(
        _LIST_WATCHLIST_INSTRUMENTS_QUERY,
        watchlist_id,
    )
    instruments = [
        WatchlistInstrumentResponse(**dict(instrument_row))
        for instrument_row in instrument_rows
    ]
    return WatchlistDetailResponse(
        **watchlist_row,
        instrument_count=len(instruments),
        instruments=instruments,
    )


@router.get("", response_model=list[WatchlistSummaryResponse])
async def list_watchlists() -> list[WatchlistSummaryResponse]:
    """Return all watchlists with instrument counts."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch(_LIST_WATCHLISTS_QUERY)

    return [WatchlistSummaryResponse(**dict(row)) for row in rows]


@router.post("", response_model=WatchlistDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(payload: WatchlistWriteRequest) -> WatchlistDetailResponse:
    """Create a new watchlist."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        created_row = await connection.fetchrow(
            _CREATE_WATCHLIST_QUERY,
            payload.name,
            payload.description,
        )
        if created_row is None:
            raise HTTPException(status_code=500, detail="Failed to create watchlist")
        return await _build_watchlist_detail(connection, int(created_row["id"]))


@router.get("/{watchlist_id}", response_model=WatchlistDetailResponse)
async def get_watchlist(watchlist_id: int) -> WatchlistDetailResponse:
    """Return a watchlist and its instruments."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        return await _build_watchlist_detail(connection, watchlist_id)


@router.put("/{watchlist_id}", response_model=WatchlistDetailResponse)
async def update_watchlist(
    watchlist_id: int,
    payload: WatchlistWriteRequest,
) -> WatchlistDetailResponse:
    """Update a watchlist's metadata."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        updated_row = await connection.fetchrow(
            _UPDATE_WATCHLIST_QUERY,
            payload.name,
            payload.description,
            watchlist_id,
        )
        if updated_row is None:
            raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
        return await _build_watchlist_detail(connection, watchlist_id)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(watchlist_id: int) -> Response:
    """Delete a watchlist."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        result = await connection.execute(_DELETE_WATCHLIST_QUERY, watchlist_id)

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{watchlist_id}/instruments", response_model=WatchlistDetailResponse)
async def add_instrument_to_watchlist(
    watchlist_id: int,
    payload: WatchlistInstrumentWriteRequest,
) -> WatchlistDetailResponse:
    """Add an instrument to a watchlist by symbol."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        await _fetch_watchlist_row(connection, watchlist_id)
        instrument_row = await _fetch_instrument_row(connection, payload.symbol)
        existing_row = await connection.fetchrow(
            _GET_WATCHLIST_MEMBERSHIP_QUERY,
            watchlist_id,
            instrument_row["id"],
        )
        if existing_row is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Instrument {payload.symbol} already exists in watchlist {watchlist_id}",
            )
        await connection.execute(
            _INSERT_WATCHLIST_INSTRUMENT_QUERY,
            watchlist_id,
            instrument_row["id"],
        )
        return await _build_watchlist_detail(connection, watchlist_id)


@router.delete("/{watchlist_id}/instruments/{symbol}", response_model=WatchlistDetailResponse)
async def remove_instrument_from_watchlist(
    watchlist_id: int,
    symbol: str,
) -> WatchlistDetailResponse:
    """Remove an instrument from a watchlist by symbol."""
    normalized_symbol = symbol.strip().upper()
    pool = await get_pool()
    async with pool.acquire() as connection:
        await _fetch_watchlist_row(connection, watchlist_id)
        instrument_row = await _fetch_instrument_row(connection, normalized_symbol)
        result = await connection.execute(
            _DELETE_WATCHLIST_INSTRUMENT_QUERY,
            watchlist_id,
            instrument_row["id"],
        )
        if result == "DELETE 0":
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {normalized_symbol} is not in watchlist {watchlist_id}",
            )
        return await _build_watchlist_detail(connection, watchlist_id)
