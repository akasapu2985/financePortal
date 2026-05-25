from __future__ import annotations

import logging

import httpx
import pytest

from intelligence.openrouter import OpenRouterClient


@pytest.mark.asyncio
async def test_create_chat_completion_uses_default_model_and_logs_token_usage(
    caplog: pytest.LogCaptureFixture,
) -> None:
    captured_request: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_request["authorization"] = request.headers["Authorization"]
        captured_request["path"] = request.url.path
        captured_request["payload"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={
                "id": "gen-123",
                "choices": [
                    {"message": {"role": "assistant", "content": "Buy signal detected."}}
                ],
                "usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://openrouter.ai/api/v1",
    ) as http_client:
        client = OpenRouterClient(api_key="test-key", http_client=http_client)

        with caplog.at_level(logging.INFO):
            response = await client.create_chat_completion(
                [{"role": "user", "content": "Summarize AAPL news."}]
            )

    assert response["usage"]["total_tokens"] == 20
    assert captured_request["authorization"] == "Bearer test-key"
    assert captured_request["path"] == "/api/v1/chat/completions"
    assert '"model":"deepseek/deepseek-r1"' in captured_request["payload"]
    assert "OpenRouter token usage model=deepseek/deepseek-r1 prompt_tokens=12 completion_tokens=8 total_tokens=20" in caplog.text


@pytest.mark.asyncio
async def test_create_chat_completion_uses_configured_model() -> None:
    captured_request: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_request["payload"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"choices": [], "usage": {}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://openrouter.ai/api/v1",
    ) as http_client:
        client = OpenRouterClient(
            api_key="test-key",
            model="deepseek/deepseek-chat",
            http_client=http_client,
        )

        await client.create_chat_completion([{"role": "user", "content": "Test"}])

    assert '"model":"deepseek/deepseek-chat"' in captured_request["payload"]


@pytest.mark.asyncio
async def test_create_chat_completion_retries_with_exponential_backoff() -> None:
    sleep_calls: list[float] = []
    attempts = 0

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(500, json={"error": {"message": "temporary outage"}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://openrouter.ai/api/v1",
    ) as http_client:
        client = OpenRouterClient(
            api_key="test-key",
            http_client=http_client,
            sleep=fake_sleep,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.create_chat_completion([{"role": "user", "content": "Retry me"}])

    assert attempts == 4
    assert sleep_calls == [1, 2, 4]


def test_openrouter_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        OpenRouterClient()
