"""Async OpenRouter client for DeepSeek-backed chat completion requests."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any, Self

import httpx

logger = logging.getLogger(__name__)

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/"
_DEFAULT_MODEL = "deepseek/deepseek-r1"
_RETRY_DELAYS_SECONDS = (1, 2, 4)
_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class OpenRouterClient:
    """Small async wrapper around the OpenRouter chat completions endpoint."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        base_url: str = _OPENROUTER_BASE_URL,
        timeout: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        resolved_api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not resolved_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        self._api_key = resolved_api_key
        self._model = model
        self._base_url = base_url
        self._timeout = timeout
        self._http_client = http_client
        self._owns_http_client = http_client is None
        self._sleep = sleep

    async def __aenter__(self) -> Self:
        self._get_http_client()
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_http_client and self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def create_chat_completion(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        model: str | None = None,
        **request_options: Any,
    ) -> dict[str, Any]:
        payload = {
            "model": model or self._model,
            "messages": [dict(message) for message in messages],
            **request_options,
        }

        max_attempts = len(_RETRY_DELAYS_SECONDS) + 1
        for attempt in range(1, max_attempts + 1):
            retry_delay = (
                None if attempt > len(_RETRY_DELAYS_SECONDS) else _RETRY_DELAYS_SECONDS[attempt - 1]
            )
            try:
                response = await self._get_http_client().post(
                    "chat/completions",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                response_data = response.json()
                self._log_token_usage(payload["model"], response_data.get("usage"))
                return response_data
            except httpx.HTTPStatusError as exc:
                if retry_delay is None or exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                    raise
                logger.warning(
                    "OpenRouter request failed with status=%s attempt=%s retrying_in=%ss",
                    exc.response.status_code,
                    attempt,
                    retry_delay,
                )
            except httpx.HTTPError as exc:
                if retry_delay is None:
                    raise
                logger.warning(
                    "OpenRouter request failed attempt=%s retrying_in=%ss error=%s",
                    attempt,
                    retry_delay,
                    str(exc),
                )
            await self._sleep(retry_delay)

        raise RuntimeError("OpenRouter request failed after all retry attempts")

    def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        return self._http_client

    def _log_token_usage(self, model: str, usage: Mapping[str, Any] | None) -> None:
        usage_mapping = usage or {}
        logger.info(
            "OpenRouter token usage model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            model,
            usage_mapping.get("prompt_tokens"),
            usage_mapping.get("completion_tokens"),
            usage_mapping.get("total_tokens"),
        )
