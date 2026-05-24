"""Instrument routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_pool

router = APIRouter(tags=["instruments"])


class InstrumentResponse(BaseModel):
    symbol: str
    name: str
    type: str
    sector: str | None
    is_owned: bool
    created_at: datetime


@router.get("/instruments", response_model=list[InstrumentResponse])
async def list_instruments() -> list[InstrumentResponse]:
    """Return all seeded instruments."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT symbol, name, type, sector, is_owned, created_at
            FROM instruments
            ORDER BY symbol
            """
        )

    return [InstrumentResponse(**dict(row)) for row in rows]
