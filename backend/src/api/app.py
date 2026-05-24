"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import router as health_router
from api.routes.instruments import router as instruments_router
from api.routes.news import router as news_router
from api.routes.prices import router as prices_router
from api.routes.watchlists import router as watchlists_router
from config import load_environment
from db.connection import close_pool, get_pool


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize shared resources for the API."""
    load_environment()
    await get_pool()
    try:
        yield
    finally:
        await close_pool()


app = FastAPI(
    title="financePortal API",
    version="0.1.0",
    description="Phase 1 backend foundation for market data and news.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(instruments_router)
app.include_router(prices_router)
app.include_router(news_router)
app.include_router(watchlists_router)
