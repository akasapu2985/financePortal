from __future__ import annotations

from types import SimpleNamespace

import pytest

from intelligence.finbert import FinBertScore, FinBertScorer


def _build_pipeline_factory(
    results_by_headline: dict[str, dict[str, float | str]],
    batch_calls: list[list[str]] | None = None,
):
    def pipeline_factory():
        def classify(
            headlines: str | list[str],
            *,
            truncation: bool,
            padding: bool,
            batch_size: int,
        ):
            del truncation, padding, batch_size
            items = [headlines] if isinstance(headlines, str) else list(headlines)
            if batch_calls is not None:
                batch_calls.append(items)
            outputs = [results_by_headline[item] for item in items]
            return outputs[0] if isinstance(headlines, str) else outputs

        return classify

    return pipeline_factory


def test_score_headline_lazy_loads_transformers_pipeline_on_first_use(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import_calls: list[str] = []

    def fake_import_module(name: str) -> SimpleNamespace:
        import_calls.append(name)
        return SimpleNamespace(
            pipeline=lambda task, model, tokenizer, device: _build_pipeline_factory(
                {"Revenue jumps after earnings": {"label": "positive", "score": 0.91}}
            )()
        )

    monkeypatch.setattr("intelligence.finbert.import_module", fake_import_module)

    scorer = FinBertScorer()

    assert import_calls == []

    score = scorer.score_headline("Revenue jumps after earnings")

    assert import_calls == ["transformers"]
    assert score == FinBertScore(label="positive", confidence=0.91, should_forward=True)

    scorer.score_headline("Revenue jumps after earnings")

    assert import_calls == ["transformers"]


def test_score_headlines_batches_requests_and_preserves_order() -> None:
    batch_calls: list[list[str]] = []
    scorer = FinBertScorer(
        batch_size=2,
        pipeline_factory=_build_pipeline_factory(
            {
                "Banks rally": {"label": "positive", "score": 0.81},
                "Stock trades flat": {"label": "neutral", "score": 0.64},
                "Guidance cut": {"label": "negative", "score": 0.88},
            },
            batch_calls=batch_calls,
        ),
    )

    scores = scorer.score_headlines(["Banks rally", "Stock trades flat", "Guidance cut"])

    assert scores == [
        FinBertScore(label="positive", confidence=0.81, should_forward=True),
        FinBertScore(label="neutral", confidence=0.64, should_forward=True),
        FinBertScore(label="negative", confidence=0.88, should_forward=True),
    ]
    assert batch_calls == [["Banks rally", "Stock trades flat"], ["Guidance cut"]]


def test_filter_articles_for_llm_skips_low_confidence_neutral_articles() -> None:
    scorer = FinBertScorer(
        neutral_threshold=0.6,
        pipeline_factory=_build_pipeline_factory(
            {
                "Quiet trading session": {"label": "neutral", "score": 0.55},
                "Company beats revenue estimates": {"label": "positive", "score": 0.93},
                "Regulator opens investigation": {"label": "negative", "score": 0.79},
            }
        ),
    )
    articles = [
        {"id": 1, "title": "Quiet trading session"},
        {"id": 2, "title": "Company beats revenue estimates"},
        {"id": 3, "title": "Regulator opens investigation"},
    ]

    annotated_articles = scorer.annotate_articles(articles)
    forwarded_articles = scorer.filter_articles_for_llm(articles)

    assert annotated_articles[0]["finbert_label"] == "neutral"
    assert annotated_articles[0]["finbert_score"] == pytest.approx(0.55)
    assert annotated_articles[0]["should_forward_to_llm"] is False
    assert [article["id"] for article in forwarded_articles] == [2, 3]
    assert all("finbert_score" not in article for article in articles)
