"""Structured financial signal extraction powered by OpenRouter."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from intelligence.prompts.v1_signal_extraction import build_signal_extraction_messages

SignalType = Literal[
    "earnings_surprise",
    "guidance_change",
    "m&a",
    "regulatory",
    "macro",
    "insider",
]
Sentiment = Literal["bullish", "bearish", "neutral"]
TimeHorizon = Literal["immediate", "short_term", "medium_term", "long_term"]


class Signal(BaseModel):
    ticker: str
    signal_type: SignalType
    sentiment: Sentiment
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str = Field(min_length=1)
    catalysts: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    time_horizon: TimeHorizon


class SignalEnvelope(BaseModel):
    status: Literal["signal"]
    signal: Signal


class NoSignalFound(BaseModel):
    status: Literal["no_signal"]
    reason: str = Field(min_length=1)


class AmbiguousSignal(BaseModel):
    status: Literal["ambiguous"]
    reason: str = Field(min_length=1)
    candidate_tickers: list[str] = Field(default_factory=list)


ExtractionPayload = SignalEnvelope | NoSignalFound | AmbiguousSignal
ExtractionResult = Signal | NoSignalFound | AmbiguousSignal
_EXCTRACTION_PAYLOAD_ADAPTER = TypeAdapter(ExtractionPayload)


class ChatCompletionClient(Protocol):
    async def create_chat_completion(
        self,
        messages: Sequence[dict[str, str]],
        **request_options: Any,
    ) -> dict[str, Any]: ...


class MalformedExtractionResponse(ValueError):
    """Raised when the model response cannot be parsed into an extraction result."""


class SignalExtractor:
    def __init__(self, client: ChatCompletionClient) -> None:
        self._client = client

    async def extract(self, article_text: str) -> ExtractionResult:
        response = await self._client.create_chat_completion(
            build_signal_extraction_messages(article_text),
            response_format={"type": "json_object"},
        )
        content = _extract_message_content(response)
        return parse_extraction_payload(content)


def parse_extraction_payload(payload: str | dict[str, Any]) -> ExtractionResult:
    parsed_payload = _coerce_payload(payload)

    try:
        validated_payload = _EXCTRACTION_PAYLOAD_ADAPTER.validate_python(parsed_payload)
    except ValidationError as exc:
        raise MalformedExtractionResponse(f"Model response did not match the extraction schema: {exc}") from exc

    if isinstance(validated_payload, SignalEnvelope):
        return validated_payload.signal
    return validated_payload


def _coerce_payload(payload: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload

    candidate = payload.strip()
    if candidate.startswith("```"):
        candidate = _strip_code_fence(candidate)

    try:
        loaded_payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise MalformedExtractionResponse("Model response was not valid JSON") from exc

    if not isinstance(loaded_payload, dict):
        raise MalformedExtractionResponse("Model response JSON must be an object")
    return loaded_payload


def _strip_code_fence(payload: str) -> str:
    stripped_payload = payload.strip()
    if stripped_payload.startswith("```json"):
        stripped_payload = stripped_payload[len("```json") :]
    elif stripped_payload.startswith("```"):
        stripped_payload = stripped_payload[3:]

    if stripped_payload.endswith("```"):
        stripped_payload = stripped_payload[:-3]
    return stripped_payload.strip()


def _extract_message_content(response: dict[str, Any]) -> str:
    try:
        message = response["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise MalformedExtractionResponse("OpenRouter response did not include a message choice") from exc

    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content

    if isinstance(content, list):
        text_chunks = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") in {None, "text"}
        ]
        joined_content = "".join(chunk for chunk in text_chunks if chunk)
        if joined_content.strip():
            return joined_content

    raise MalformedExtractionResponse("OpenRouter response content was empty")
