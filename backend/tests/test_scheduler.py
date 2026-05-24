from datetime import UTC, datetime

from collectors.scheduler import is_market_hours


def test_market_hours_returns_true_during_regular_trading_hours() -> None:
    assert is_market_hours(datetime(2026, 5, 26, 14, 0, tzinfo=UTC))


def test_market_hours_returns_false_before_open() -> None:
    assert not is_market_hours(datetime(2026, 5, 26, 13, 0, tzinfo=UTC))


def test_market_hours_returns_false_on_weekends() -> None:
    assert not is_market_hours(datetime(2026, 5, 24, 15, 0, tzinfo=UTC))
