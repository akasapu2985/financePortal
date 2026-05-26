from __future__ import annotations

import asyncio
import logging
import os
import signal
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from collectors import scheduler as scheduler_module

scheduler_impl = scheduler_module._pipeline_scheduler


@pytest.fixture(autouse=True)
def clear_scheduler_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "PRICES_COLLECTION_INTERVAL_MINUTES",
        "NEWS_COLLECTION_INTERVAL_MINUTES",
        "PRICES_SCHEDULE_CRON",
        "NEWS_SCHEDULE_CRON",
        "PRICES_SCHEDULE_TIMEZONE",
        "NEWS_SCHEDULE_TIMEZONE",
        "PRICES_MARKET_HOURS_ONLY",
        "NEWS_MARKET_HOURS_ONLY",
        "PRICES_RUN_ON_STARTUP",
        "NEWS_RUN_ON_STARTUP",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        scheduler_impl,
        "get_env",
        lambda name, default=None: os.environ.get(name, default),
    )
    monkeypatch.setattr(scheduler_impl, "load_environment", lambda: None)


@dataclass
class FakeJob:
    id: str
    name: str
    trigger: str
    kwargs: dict[str, Any]
    next_run_time: datetime | None = None


@dataclass
class FakeScheduler:
    timezone: str
    jobs: list[FakeJob] = field(default_factory=list)
    is_started: bool = False
    shutdown_wait_values: list[bool] = field(default_factory=list)

    def add_job(self, func: Any, trigger: str, **kwargs: Any) -> None:
        self.jobs.append(
            FakeJob(
                id=kwargs["id"],
                name=kwargs["name"],
                trigger=trigger,
                kwargs=kwargs,
                next_run_time=datetime(2026, 5, 26, 20, 0, tzinfo=UTC),
            )
        )

    def get_jobs(self) -> list[FakeJob]:
        return self.jobs

    def start(self) -> None:
        self.is_started = True

    def shutdown(self, wait: bool) -> None:
        self.shutdown_wait_values.append(wait)


class FakeLoop:
    def __init__(self) -> None:
        self.signal_handlers: dict[signal.Signals, Any] = {}

    def add_signal_handler(self, signal_name: signal.Signals, handler: Any) -> None:
        self.signal_handlers[signal_name] = handler


def test_market_hours_returns_true_during_regular_trading_hours() -> None:
    assert scheduler_module.is_market_hours(datetime(2026, 5, 26, 14, 0, tzinfo=UTC))


def test_market_hours_returns_false_before_open() -> None:
    assert not scheduler_module.is_market_hours(datetime(2026, 5, 26, 13, 0, tzinfo=UTC))


def test_market_hours_returns_true_at_market_close_for_end_of_day_collection() -> None:
    assert scheduler_module.is_market_hours(datetime(2026, 5, 26, 20, 0, tzinfo=UTC))


def test_market_hours_returns_false_on_weekends() -> None:
    assert not scheduler_module.is_market_hours(datetime(2026, 5, 24, 15, 0, tzinfo=UTC))


def test_load_scheduler_settings_uses_yaml_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scheduler_impl, "load_environment", lambda: None)
    monkeypatch.setattr(scheduler_impl, "get_env", lambda _name, default=None: default)

    settings = scheduler_module.load_scheduler_settings()

    prices = settings.collectors["prices"]
    assert prices.trigger == "cron"
    assert prices.trigger_args == {"day_of_week": "mon-fri", "hour": 16, "minute": 0}
    assert prices.timezone == "America/New_York"
    assert prices.market_hours_only is True
    assert prices.run_on_startup is True

    news = settings.collectors["news"]
    assert news.trigger == "interval"
    assert news.trigger_args == {"minutes": 15}
    assert news.run_on_startup is True


def test_load_scheduler_settings_applies_env_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scheduler_impl, "load_environment", lambda: None)
    monkeypatch.setenv("PRICES_COLLECTION_INTERVAL_MINUTES", "5")
    monkeypatch.setenv("NEWS_SCHEDULE_CRON", "*/10 * * * *")
    monkeypatch.setenv("NEWS_SCHEDULE_TIMEZONE", "America/New_York")
    monkeypatch.setenv("PRICES_RUN_ON_STARTUP", "false")

    settings = scheduler_module.load_scheduler_settings()

    prices = settings.collectors["prices"]
    assert prices.trigger == "interval"
    assert prices.trigger_args == {"minutes": 5}
    assert prices.run_on_startup is False
    assert prices.market_hours_only is True

    news = settings.collectors["news"]
    assert news.trigger == "cron"
    assert news.trigger_args == {
        "minute": "*/10",
        "hour": "*",
        "day": "*",
        "month": "*",
        "day_of_week": "*",
    }
    assert news.timezone == "America/New_York"


def test_load_scheduler_settings_raises_when_yaml_is_missing() -> None:
    missing_path = Path(
        "C:\\Users\\giakas\\Source\\financePortal\\backend\\tests\\missing-schedule.yaml"
    )

    with pytest.raises(FileNotFoundError, match="Scheduler config not found"):
        scheduler_module.load_scheduler_settings(missing_path)


def test_load_scheduler_settings_rejects_invalid_trigger_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target_path = Path(
        "C:\\Users\\giakas\\Source\\financePortal\\backend\\tests\\invalid-schedule.yaml"
    )
    original_exists = Path.exists
    original_read_text = Path.read_text

    monkeypatch.setattr(
        Path,
        "exists",
        lambda self: True if self == target_path else original_exists(self),
    )
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding="utf-8": "collectors: {}"
        if self == target_path
        else original_read_text(self, encoding=encoding),
    )
    monkeypatch.setattr(
        scheduler_impl.yaml,
        "safe_load",
        lambda _text: {
            "timezone": "UTC",
            "collectors": {"prices": {"trigger": "bogus"}},
        },
    )

    with pytest.raises(ValueError, match="Unsupported trigger type: bogus"):
        scheduler_module.load_scheduler_settings(target_path)


@pytest.mark.asyncio
async def test_run_price_collection_skips_outside_market_hours(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    collect_calls: list[list[str]] = []

    async def fake_collect_prices(symbols: list[str]) -> None:
        collect_calls.append(symbols)

    monkeypatch.setattr(scheduler_impl, "is_market_hours", lambda: False)
    monkeypatch.setattr(scheduler_impl, "collect_prices", fake_collect_prices)

    with caplog.at_level(logging.INFO):
        await scheduler_module.run_price_collection()

    assert collect_calls == []
    assert "Skipping price collection outside market hours" in caplog.text


@pytest.mark.asyncio
async def test_run_price_collection_collects_when_market_hours_gate_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collect_calls: list[list[str]] = []

    async def fake_get_symbols() -> list[str]:
        return ["AAPL", "MSFT"]

    async def fake_collect_prices(symbols: list[str]) -> None:
        collect_calls.append(symbols)

    monkeypatch.setattr(scheduler_impl, "is_market_hours", lambda: False)
    monkeypatch.setattr(scheduler_impl, "get_symbols", fake_get_symbols)
    monkeypatch.setattr(scheduler_impl, "collect_prices", fake_collect_prices)

    await scheduler_module.run_price_collection(market_hours_only=False)

    assert collect_calls == [["AAPL", "MSFT"]]


@pytest.mark.asyncio
async def test_run_news_collection_skips_when_no_instruments_are_seeded(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    collect_calls: list[list[str]] = []

    async def fake_collect_news(symbols: list[str]) -> None:
        collect_calls.append(symbols)

    async def fake_get_symbols() -> list[str]:
        return []

    monkeypatch.setattr(scheduler_impl, "get_symbols", fake_get_symbols)
    monkeypatch.setattr(scheduler_impl, "collect_news", fake_collect_news)

    with caplog.at_level(logging.INFO):
        await scheduler_module.run_news_collection()

    assert collect_calls == []
    assert "Skipping news collection because no instruments are seeded" in caplog.text


@pytest.mark.asyncio
async def test_configure_scheduler_registers_jobs_with_overlap_protection() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    settings = scheduler_module.SchedulerSettings(
        timezone="UTC",
        collectors={
            "prices": scheduler_module.CollectorSchedule(
                name="prices",
                job_id="price-collector",
                trigger="cron",
                trigger_args={"day_of_week": "mon-fri", "hour": 16, "minute": 0},
                timezone="America/New_York",
                market_hours_only=True,
            ),
            "news": scheduler_module.CollectorSchedule(
                name="news",
                job_id="news-collector",
                trigger="interval",
                trigger_args={"minutes": 15},
            ),
        },
    )
    job_states: dict[str, scheduler_module.SchedulerJobState] = {}

    scheduler_module.configure_scheduler(scheduler, settings, job_states)
    scheduler.start()
    jobs = {job.id: job for job in scheduler.get_jobs()}
    snapshot = scheduler_module.build_scheduler_state_snapshot(scheduler, job_states)
    scheduler.shutdown(wait=False)

    assert set(jobs) == {"price-collector", "news-collector"}
    assert jobs["price-collector"].max_instances == 1
    assert jobs["price-collector"].coalesce is True
    assert jobs["news-collector"].max_instances == 1
    assert jobs["news-collector"].coalesce is True
    assert {item["job_id"] for item in snapshot} == {"price-collector", "news-collector"}
    assert all(item["next_run_time"] is not None for item in snapshot)


@pytest.mark.asyncio
async def test_run_job_updates_success_status_and_logs_scheduler_state(
    caplog: pytest.LogCaptureFixture,
) -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    settings = scheduler_module.SchedulerSettings(
        timezone="UTC",
        collectors={
            "news": scheduler_module.CollectorSchedule(
                name="news",
                job_id="news-collector",
                trigger="interval",
                trigger_args={"minutes": 15},
            )
        },
    )
    job_states: dict[str, scheduler_module.SchedulerJobState] = {}
    scheduler_module.configure_scheduler(scheduler, settings, job_states)
    scheduler.start()

    async def successful_job() -> None:
        return None

    caplog.set_level(logging.INFO)
    await scheduler_module.run_job("news-collector", "news", successful_job, job_states, scheduler)
    scheduler.shutdown(wait=False)

    assert job_states["news-collector"].last_status == "succeeded"
    assert any(
        "job_id=news-collector" in record.getMessage()
        and "last_status=succeeded" in record.getMessage()
        and "next_run_time=" in record.getMessage()
        for record in caplog.records
    )


@pytest.mark.asyncio
async def test_run_job_updates_failure_status_before_reraising() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    settings = scheduler_module.SchedulerSettings(
        timezone="UTC",
        collectors={
            "news": scheduler_module.CollectorSchedule(
                name="news",
                job_id="news-collector",
                trigger="interval",
                trigger_args={"minutes": 15},
            )
        },
    )
    job_states: dict[str, scheduler_module.SchedulerJobState] = {}
    scheduler_module.configure_scheduler(scheduler, settings, job_states)
    scheduler.start()

    async def failing_job() -> None:
        raise RuntimeError("collector unavailable")

    with pytest.raises(RuntimeError, match="collector unavailable"):
        await scheduler_module.run_job("news-collector", "news", failing_job, job_states, scheduler)

    scheduler.shutdown(wait=False)
    assert job_states["news-collector"].last_status == "failed"
    assert job_states["news-collector"].last_error == "collector unavailable"


@pytest.mark.asyncio
async def test_run_scheduler_registers_jobs_logs_state_and_shuts_down_cleanly(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    fake_scheduler = FakeScheduler(timezone="UTC")
    close_pool_calls: list[str] = []
    startup_calls: list[str] = []
    stop_event = asyncio.Event()
    stop_event.set()
    settings = scheduler_module.load_scheduler_settings()

    async def fake_get_pool() -> object:
        return object()

    async def fake_close_pool() -> None:
        close_pool_calls.append("closed")

    async def fake_run_startup_jobs(*_args: Any) -> None:
        startup_calls.append("started")

    monkeypatch.setattr(scheduler_impl, "AsyncIOScheduler", lambda timezone: fake_scheduler)
    monkeypatch.setattr(scheduler_impl, "load_environment", lambda: None)
    monkeypatch.setattr(scheduler_impl, "load_scheduler_settings", lambda: settings)
    monkeypatch.setattr(scheduler_impl, "get_pool", fake_get_pool)
    monkeypatch.setattr(scheduler_impl, "close_pool", fake_close_pool)
    monkeypatch.setattr(scheduler_impl, "_run_startup_jobs", fake_run_startup_jobs)

    caplog.set_level(logging.INFO)
    await scheduler_module.run_scheduler(stop_event)

    assert fake_scheduler.is_started is True
    assert fake_scheduler.shutdown_wait_values == [True]
    assert close_pool_calls == ["closed"]
    assert startup_calls == ["started"]
    assert [(job.id, job.trigger) for job in fake_scheduler.jobs] == [
        ("price-collector", "cron"),
        ("news-collector", "interval"),
    ]
    assert all(job.kwargs["max_instances"] == 1 for job in fake_scheduler.jobs)
    assert all(job.kwargs["coalesce"] is True for job in fake_scheduler.jobs)
    assert "Collector scheduler started" in caplog.text
    assert "Scheduler state job_id=price-collector" in caplog.text
    assert "Collector scheduler stopped" in caplog.text


@pytest.mark.asyncio
async def test_run_scheduler_propagates_database_startup_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scheduler_created = False

    async def fake_get_pool() -> object:
        raise ConnectionError("database unavailable")

    def fake_scheduler_factory(timezone: str) -> FakeScheduler:
        nonlocal scheduler_created
        scheduler_created = True
        return FakeScheduler(timezone=timezone)

    monkeypatch.setattr(scheduler_impl, "AsyncIOScheduler", fake_scheduler_factory)
    monkeypatch.setattr(scheduler_impl, "load_environment", lambda: None)
    monkeypatch.setattr(scheduler_impl, "get_pool", fake_get_pool)

    with pytest.raises(ConnectionError, match="database unavailable"):
        await scheduler_module.run_scheduler(asyncio.Event())

    assert scheduler_created is False


@pytest.mark.asyncio
async def test_run_scheduler_closes_pool_when_scheduler_start_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_scheduler = FakeScheduler(timezone="UTC")
    close_pool_calls: list[str] = []
    settings = scheduler_module.load_scheduler_settings()

    async def fake_get_pool() -> object:
        return object()

    async def fake_close_pool() -> None:
        close_pool_calls.append("closed")

    def fail_start() -> None:
        raise RuntimeError("scheduler start failed")

    fake_scheduler.start = fail_start

    monkeypatch.setattr(scheduler_impl, "AsyncIOScheduler", lambda timezone: fake_scheduler)
    monkeypatch.setattr(scheduler_impl, "load_environment", lambda: None)
    monkeypatch.setattr(scheduler_impl, "load_scheduler_settings", lambda: settings)
    monkeypatch.setattr(scheduler_impl, "get_pool", fake_get_pool)
    monkeypatch.setattr(scheduler_impl, "close_pool", fake_close_pool)

    with pytest.raises(RuntimeError, match="scheduler start failed"):
        await scheduler_module.run_scheduler(asyncio.Event())

    assert close_pool_calls == ["closed"]


@pytest.mark.asyncio
async def test_run_startup_jobs_logs_warning_and_continues_after_collector_failure(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = scheduler_module.SchedulerSettings(
        timezone="UTC",
        collectors={
            "prices": scheduler_module.CollectorSchedule(
                name="prices",
                job_id="price-collector",
                trigger="interval",
                trigger_args={"minutes": 5},
            ),
            "news": scheduler_module.CollectorSchedule(
                name="news",
                job_id="news-collector",
                trigger="interval",
                trigger_args={"minutes": 15},
            ),
        },
    )
    job_states: dict[str, scheduler_module.SchedulerJobState] = {}
    scheduler = FakeScheduler(timezone="UTC")
    run_attempts: list[tuple[str, str]] = []

    async def fake_run_job(
        job_id: str,
        collector_name: str,
        collector_job: Any,
        states: dict[str, scheduler_module.SchedulerJobState],
        active_scheduler: FakeScheduler,
    ) -> None:
        run_attempts.append((job_id, collector_name))
        states.setdefault(job_id, scheduler_module.SchedulerJobState())
        if collector_name == "prices":
            raise RuntimeError("prices collector crashed")

    monkeypatch.setattr(scheduler_impl, "run_job", fake_run_job)

    caplog.set_level(logging.WARNING)
    await scheduler_impl._run_startup_jobs(settings, job_states, scheduler)

    assert run_attempts == [
        ("price-collector", "prices"),
        ("news-collector", "news"),
    ]
    assert "Startup collector run failed and will be retried on schedule: prices" in caplog.text


@pytest.mark.asyncio
async def test_main_registers_shutdown_signal_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_loop = FakeLoop()
    captured_events: list[asyncio.Event] = []

    async def fake_run_scheduler(stop_event: asyncio.Event) -> None:
        captured_events.append(stop_event)

    monkeypatch.setattr(asyncio, "get_running_loop", lambda: fake_loop)
    monkeypatch.setattr(scheduler_impl, "run_scheduler", fake_run_scheduler)
    monkeypatch.setattr(scheduler_module, "run_scheduler", fake_run_scheduler)

    await scheduler_module.main()

    assert len(captured_events) == 1
    stop_event = captured_events[0]
    assert stop_event.is_set() is False
    assert set(fake_loop.signal_handlers) == {signal.SIGINT, signal.SIGTERM}

    fake_loop.signal_handlers[signal.SIGTERM]()

    assert stop_event.is_set() is True


@pytest.mark.skip(
    reason="awaiting implementation of env-only fallback when schedule YAML is missing"
)
def test_scheduler_uses_env_defaults_when_yaml_config_is_missing() -> None:
    pass


def test_scheduler_rejects_zero_minute_collection_intervals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PRICES_COLLECTION_INTERVAL_MINUTES", "0")

    with pytest.raises(ValueError, match="positive integer"):
        scheduler_module.load_scheduler_settings()
