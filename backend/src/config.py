"""Shared configuration helpers for the backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ENVIRONMENT_LOADED = False


def get_repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parents[2]


def load_environment() -> None:
    """Load repository environment variables from .env and .env.example."""
    global _ENVIRONMENT_LOADED
    if _ENVIRONMENT_LOADED:
        return

    repo_root = get_repo_root()
    load_dotenv(repo_root / ".env.example", override=False)
    load_dotenv(repo_root / ".env", override=True)
    _ENVIRONMENT_LOADED = True


def get_env(name: str, default: str | None = None) -> str | None:
    """Get an environment variable after loading dotenv files."""
    load_environment()
    return os.getenv(name, default)


def get_env_int(name: str, default: int) -> int:
    """Get an integer environment variable with a fallback value."""
    value = get_env(name)
    if value is None:
        return default
    return int(value)
