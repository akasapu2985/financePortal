"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.connection import get_pool

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    database: str


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Return the API and database health state."""
    try:
        pool = await get_pool()
        async with pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
    except Exception as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error

    return HealthResponse(status="ok", database="connected")
