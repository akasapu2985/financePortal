from __future__ import annotations

import json
from pathlib import Path

import pytest

from intelligence.extractor import (
    AmbiguousSignal,
    MalformedExtractionResponse,
    NoSignalFound,
    Signal,
    SignalExtractor,
    parse_extraction_payload,
)
from intelligence.prompts.v1_signal_extraction import PROMPT_VERSION, build_signal_extraction_messages


class FakeOpenRouterClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def create_chat_completion(self, messages: list[dict[str, str]], **request_options: object) -> dict[str, object]:
        self.calls.append({"messages": messages, "request_options": request_options})
        return self.response


@pytest.mark.asyncio
async def test_extract_builds_versioned_prompt_and_parses_signal_response() -> None:
    article_text = "AAPL posted quarterly revenue ahead of consensus and raised iPhone guidance for next quarter."
    fake_client = FakeOpenRouterClient(
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "status": "signal",
                                "signal": {
                                    "ticker": "AAPL",
                                    "signal_type": "earnings_surprise",
                                    "sentiment": "bullish",
                                    "confidence": 0.94,
                                    "summary": "Apple beat revenue expectations and lifted near-term guidance.",
                                    "catalysts": ["Revenue beat", "Raised iPhone guidance"],
                                    "risks": ["Services growth slowed in China"],
                                    "time_horizon": "short_term",
                                },
                            }
                        )
                    }
                }
            ]
        }
    )
    extractor = SignalExtractor(fake_client)

    result = await extractor.extract(article_text)

    assert isinstance(result, Signal)
    assert result.ticker == "AAPL"
    assert result.signal_type == "earnings_surprise"
    assert result.sentiment == "bullish"
    assert fake_client.calls[0]["messages"] == build_signal_extraction_messages(article_text)
    assert fake_client.calls[0]["messages"][0]["content"].startswith("You are an elite sell-side financial event extraction analyst")
    assert PROMPT_VERSION in fake_client.calls[0]["messages"][1]["content"]
    assert fake_client.calls[0]["request_options"] == {"response_format": {"type": "json_object"}}


@pytest.mark.asyncio
async def test_extract_returns_no_signal_result() -> None:
    fake_client = FakeOpenRouterClient(
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "status": "no_signal",
                                "reason": "The article is a routine leadership profile without a tradable catalyst.",
                            }
                        )
                    }
                }
            ]
        }
    )

    result = await SignalExtractor(fake_client).extract("Article text")

    assert result == NoSignalFound(
        status="no_signal",
        reason="The article is a routine leadership profile without a tradable catalyst.",
    )


@pytest.mark.asyncio
async def test_extract_returns_ambiguous_result() -> None:
    fake_client = FakeOpenRouterClient(
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "status": "ambiguous",
                                "reason": "The article references conflicting takeover targets and does not isolate one primary ticker.",
                                "candidate_tickers": ["MSFT", "ATVI"],
                            }
                        )
                    }
                }
            ]
        }
    )

    result = await SignalExtractor(fake_client).extract("Article text")

    assert result == AmbiguousSignal(
        status="ambiguous",
        reason="The article references conflicting takeover targets and does not isolate one primary ticker.",
        candidate_tickers=["MSFT", "ATVI"],
    )


@pytest.mark.asyncio
async def test_extract_raises_on_malformed_response() -> None:
    fake_client = FakeOpenRouterClient({"choices": [{"message": {"content": "not-json"}}]})

    with pytest.raises(MalformedExtractionResponse, match="valid JSON"):
        await SignalExtractor(fake_client).extract("Malformed article")


def test_eval_cases_cover_twenty_articles_with_valid_expected_outputs() -> None:
    cases_path = Path(__file__).resolve().parent / "eval" / "signal_extraction" / "cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    assert len(cases) == 20
    assert {case["expected"]["status"] for case in cases} == {"signal", "no_signal", "ambiguous"}

    for case in cases:
        expected = parse_extraction_payload(case["expected"])
        assert isinstance(expected, Signal | NoSignalFound | AmbiguousSignal)
        assert case["headline"]
        assert case["body"]
