"""Version 1 prompt for extracting structured financial signals from articles."""

from __future__ import annotations

import json
from typing import Any

PROMPT_VERSION = "v1"
SIGNAL_TYPES = (
    "earnings_surprise",
    "guidance_change",
    "m&a",
    "regulatory",
    "macro",
    "insider",
)

_OUTPUT_SCHEMA: dict[str, Any] = {
    "success": {
        "status": "signal",
        "signal": {
            "ticker": "string",
            "signal_type": list(SIGNAL_TYPES),
            "sentiment": ["bullish", "bearish", "neutral"],
            "confidence": "float between 0 and 1",
            "summary": "string",
            "catalysts": ["string"],
            "risks": ["string"],
            "time_horizon": ["immediate", "short_term", "medium_term", "long_term"],
        },
    },
    "no_signal": {
        "status": "no_signal",
        "reason": "string",
    },
    "ambiguous": {
        "status": "ambiguous",
        "reason": "string",
        "candidate_tickers": ["string"],
    },
}

SYSTEM_PROMPT = """You are an elite sell-side financial event extraction analyst. Read one article at a time and decide whether it contains a single clear market signal for a publicly traded ticker. Return JSON only. Do not add markdown, commentary, or extra keys. Prefer no_signal when the article lacks a tradable catalyst. Prefer ambiguous when the article mixes multiple conflicting signals or does not support one primary ticker. When a signal exists, keep the summary to 1-2 sentences, list concrete catalysts and risks, and set confidence between 0 and 1."""


def build_signal_extraction_messages(article_text: str) -> list[dict[str, str]]:
    schema_json = json.dumps(_OUTPUT_SCHEMA, indent=2)
    user_prompt = (
        f"Prompt version: {PROMPT_VERSION}\n"
        "Task: extract a structured market signal from the article below.\n"
        "Allowed signal types: "
        f"{', '.join(SIGNAL_TYPES)}\n"
        "Success schema fields: ticker, signal_type, sentiment, confidence, summary, catalysts, risks, time_horizon.\n"
        "Failure cases must use either the no_signal or ambiguous schema exactly as defined below.\n"
        f"Schema:\n{schema_json}\n\n"
        f"Article:\n{article_text.strip()}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
