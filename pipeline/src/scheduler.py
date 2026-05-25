"""APScheduler runner for the intelligence pipeline collectors."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _REPO_ROOT / "backend" / "src"

if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from collectors.news import collect_news  # noqa: E402
from collectors.prices import collect_prices  # noqa: E402
from config import get_env, get_repo_root, load_environment  # noqa: E402
from db.connection import close_pool, get_pool  # noqa: E402

logger = logging.getLogger(__name__)
_MARKET_TIMEZONE = ZoneInfo("America/New_York")
_SCHEDULE_PATH = get_repo_root() / "pipeline" / "schedule.yaml"


@dataclass(frozen=True)
class CollectorSchedule:
    name: str
    job_id: str
    trigger: str
    trigger_args: dict[str, int | str] = field(default_factory=dict)
    timezone: str | None = None
    market_hours_only: bool = False
    run_on_startup: bool = True


@dataclass(frozen=True)
class SchedulerSettings:
    timezone: str = "UTC"
    collectors: dict[str, CollectorSchedule] = field(default_factory=dict)


@dataclass
class SchedulerJobState:
    last_status: str = "not-run"
    last_finished_at: datetime | None = None
    last_error: str | None = None


CollectorJob = Callable[[], Awaitable[None]]


def is_market_hours(current_time: datetime | None = None) -> bool:
    """Return True when the NYSE is open or at the daily close on a trading day."""
    now = (
        current_time.astimezone(_MARKET_TIMEZONE)
        if current_time
        else datetime.now(_MARKET_TIMEZONE)
    )
    if now.weekday() > 4:
        return False
    market_open = time(hour=9, minute=30)
    market_close = time(hour=16, minute=0)
    return market_open <= now.time() <= market_close


async def get_symbols() -> list[str]:
    """Load tracked symbols from the instruments table."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT symbol FROM instruments ORDER BY symbol")
    return [row["symbol"] for row in rows]


async def run_price_collection(market_hours_only: bool = True) -> None:
    """Collect prices during US market hours when required by schedule settings."""
    if market_hours_only and not is_market_hours():
        logger.info("Skipping price collection outside market hours")
        return

    symbols = await get_symbols()
    if not symbols:
        logger.info("Skipping price collection because no instruments are seeded")
        return

    await collect_prices(symbols)


async def run_news_collection() -> None:
    """Collect the latest news for tracked symbols."""
    symbols = await get_symbols()
    if not symbols:
        logger.info("Skipping news collection because no instruments are seeded")
        return

    await collect_news(symbols)


def _require_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected a mapping for {context}")
    return value


def _parse_bool(value: Any, *, context: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    raise ValueError(f"Expected a boolean for {context}")


def _parse_optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return _parse_bool(value, context="environment override")


def _parse_positive_int(value: Any, *, context: str) -> int:
    parsed_value = int(value)
    if parsed_value <= 0:
        raise ValueError(f"Expected a positive integer for {context}")
    return parsed_value


def _parse_trigger_args(trigger: str, raw_schedule: Mapping[str, Any]) -> dict[str, int | str]:
    if trigger == "interval":
        interval = _require_mapping(raw_schedule.get("interval"), context="interval trigger")
        trigger_args = {
            key: _parse_positive_int(value, context=f"interval trigger field '{key}'")
            for key, value in interval.items()
            if key in {"weeks", "days", "hours", "minutes", "seconds"}
        }
        if not trigger_args:
            raise ValueError("Interval trigger requires at least one interval field")
        return trigger_args

    if trigger == "cron":
        cron = _require_mapping(raw_schedule.get("cron"), context="cron trigger")
        trigger_args = {
            key: value
            for key, value in cron.items()
            if key in {"year", "month", "day", "week", "day_of_week", "hour", "minute", "second"}
        }
        if not trigger_args:
            raise ValueError("Cron trigger requires at least one cron field")
        return trigger_args

    raise ValueError(f"Unsupported trigger type: {trigger}")


def _parse_collector_schedule(name: str, raw_schedule: Any) -> CollectorSchedule:
    schedule_mapping = _require_mapping(raw_schedule, context=f"collector '{name}'")
    trigger = str(schedule_mapping.get("trigger", "")).strip().lower()
    if not trigger:
        raise ValueError(f"Collector '{name}' is missing a trigger")

    timezone = schedule_mapping.get("timezone")
    if timezone is not None and not isinstance(timezone, str):
        raise ValueError(f"Collector '{name}' timezone must be a string")

    return CollectorSchedule(
        name=name,
        job_id=str(schedule_mapping.get("job_id", f"{name}-collector")),
        trigger=trigger,
        trigger_args=_parse_trigger_args(trigger, schedule_mapping),
        timezone=timezone,
        market_hours_only=_parse_bool(
            schedule_mapping.get("market_hours_only", False),
            context=f"collector '{name}' market_hours_only",
        ),
        run_on_startup=_parse_bool(
            schedule_mapping.get("run_on_startup", True),
            context=f"collector '{name}' run_on_startup",
        ),
    )


def _parse_cron_expression(expression: str) -> dict[str, str]:
    parts = expression.split()
    if len(parts) == 5:
        minute, hour, day, month, day_of_week = parts
        return {
            "minute": minute,
            "hour": hour,
            "day": day,
            "month": month,
            "day_of_week": day_of_week,
        }
    if len(parts) == 6:
        second, minute, hour, day, month, day_of_week = parts
        return {
            "second": second,
            "minute": minute,
            "hour": hour,
            "day": day,
            "month": month,
            "day_of_week": day_of_week,
        }
    raise ValueError("Cron expressions must have 5 or 6 fields")


def _apply_env_overrides(settings: SchedulerSettings) -> SchedulerSettings:
    overridden_collectors: dict[str, CollectorSchedule] = {}

    for name, schedule in settings.collectors.items():
        prefix = name.upper()
        interval_minutes = get_env(f"{prefix}_COLLECTION_INTERVAL_MINUTES")
        cron_expression = get_env(f"{prefix}_SCHEDULE_CRON")
        timezone = get_env(f"{prefix}_SCHEDULE_TIMEZONE")
        market_hours_only = _parse_optional_bool(get_env(f"{prefix}_MARKET_HOURS_ONLY"))
        run_on_startup = _parse_optional_bool(get_env(f"{prefix}_RUN_ON_STARTUP"))

        trigger = schedule.trigger
        trigger_args = dict(schedule.trigger_args)
        if interval_minutes not in {None, ""}:
            trigger = "interval"
            trigger_args = {
                "minutes": _parse_positive_int(
                    interval_minutes,
                    context=f"environment override {prefix}_COLLECTION_INTERVAL_MINUTES",
                )
            }
        elif cron_expression not in {None, ""}:
            trigger = "cron"
            trigger_args = _parse_cron_expression(cron_expression)

        overridden_collectors[name] = replace(
            schedule,
            trigger=trigger,
            trigger_args=trigger_args,
            timezone=timezone or schedule.timezone,
            market_hours_only=(
                schedule.market_hours_only
                if market_hours_only is None
                else market_hours_only
            ),
            run_on_startup=schedule.run_on_startup if run_on_startup is None else run_on_startup,
        )

    return SchedulerSettings(timezone=settings.timezone, collectors=overridden_collectors)


def load_scheduler_settings(schedule_path: Path | None = None) -> SchedulerSettings:
    """Load YAML-backed scheduler settings with environment overrides."""
    load_environment()
    resolved_path = schedule_path or _SCHEDULE_PATH
    if not resolved_path.exists():
        raise FileNotFoundError(f"Scheduler config not found: {resolved_path}")

    raw_settings = yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}
    settings_mapping = _require_mapping(raw_settings, context="scheduler settings")
    collectors_mapping = _require_mapping(settings_mapping.get("collectors"), context="collectors")

    settings = SchedulerSettings(
        timezone=str(settings_mapping.get("timezone", "UTC")),
        collectors={
            name: _parse_collector_schedule(name, raw_schedule)
            for name, raw_schedule in collectors_mapping.items()
        },
    )
    return _apply_env_overrides(settings)


def _build_job_callable(name: str, schedule: CollectorSchedule) -> CollectorJob:
    if name == "prices":
        return lambda: run_price_collection(schedule.market_hours_only)
    if name == "news":
        return run_news_collection
    raise ValueError(f"Unsupported collector '{name}' in scheduler config")


def _get_trigger_kwargs(schedule: CollectorSchedule) -> dict[str, int | str]:
    trigger_kwargs = dict(schedule.trigger_args)
    if schedule.trigger == "cron" and schedule.timezone:
        trigger_kwargs["timezone"] = schedule.timezone
    return trigger_kwargs


def _resolve_next_run_time(job: Any) -> datetime | None:
    next_run_time = getattr(job, "next_run_time", None)
    if next_run_time is not None:
        return next_run_time

    trigger = getattr(job, "trigger", None)
    if trigger is None:
        return None

    return trigger.get_next_fire_time(None, datetime.now(UTC))


def build_scheduler_state_snapshot(
    scheduler: AsyncIOScheduler,
    job_states: Mapping[str, SchedulerJobState],
) -> list[dict[str, str | None]]:
    """Return a serializable snapshot of scheduled jobs and their last known status."""
    snapshots: list[dict[str, str | None]] = []
    for job in sorted(scheduler.get_jobs(), key=lambda item: item.id):
        state = job_states.get(job.id, SchedulerJobState())
        next_run_time = _resolve_next_run_time(job)
        snapshots.append(
            {
                "job_id": job.id,
                "collector": job.name,
                "next_run_time": next_run_time.isoformat() if next_run_time else None,
                "last_status": state.last_status,
                "last_finished_at": (
                    state.last_finished_at.isoformat() if state.last_finished_at else None
                ),
                "last_error": state.last_error,
            }
        )
    return snapshots


def log_scheduler_state(
    scheduler: AsyncIOScheduler,
    job_states: Mapping[str, SchedulerJobState],
) -> None:
    """Log next-run and last-run state for every configured scheduler job."""
    for snapshot in build_scheduler_state_snapshot(scheduler, job_states):
        logger.info(
            "Scheduler state job_id=%s collector=%s next_run_time=%s "
            "last_status=%s last_finished_at=%s last_error=%s",
            snapshot["job_id"],
            snapshot["collector"],
            snapshot["next_run_time"],
            snapshot["last_status"],
            snapshot["last_finished_at"],
            snapshot["last_error"],
        )


async def run_job(
    job_id: str,
    collector_name: str,
    collector_job: CollectorJob,
    job_states: dict[str, SchedulerJobState],
    scheduler: AsyncIOScheduler,
) -> None:
    """Run one collector job and update the in-memory scheduler state."""
    state = job_states.setdefault(job_id, SchedulerJobState())
    try:
        await collector_job()
    except Exception as exc:
        state.last_status = "failed"
        state.last_finished_at = datetime.now(UTC)
        state.last_error = str(exc)
        logger.exception("Collector job failed: %s", collector_name)
        log_scheduler_state(scheduler, job_states)
        raise

    state.last_status = "succeeded"
    state.last_finished_at = datetime.now(UTC)
    state.last_error = None
    logger.info("Collector job completed: %s", collector_name)
    log_scheduler_state(scheduler, job_states)


def configure_scheduler(
    scheduler: AsyncIOScheduler,
    settings: SchedulerSettings,
    job_states: dict[str, SchedulerJobState],
) -> None:
    """Register collector jobs on the provided scheduler instance."""
    for name, schedule in settings.collectors.items():
        collector_job = _build_job_callable(name, schedule)
        job_states.setdefault(schedule.job_id, SchedulerJobState())

        async def scheduled_run(
            job_id: str = schedule.job_id,
            collector_name: str = name,
            job: CollectorJob = collector_job,
        ) -> None:
            await run_job(job_id, collector_name, job, job_states, scheduler)

        scheduler.add_job(
            scheduled_run,
            schedule.trigger,
            **_get_trigger_kwargs(schedule),
            max_instances=1,
            coalesce=True,
            id=schedule.job_id,
            name=name,
        )


async def _run_startup_jobs(
    settings: SchedulerSettings,
    job_states: dict[str, SchedulerJobState],
    scheduler: AsyncIOScheduler,
) -> None:
    for name, schedule in settings.collectors.items():
        if not schedule.run_on_startup:
            continue
        try:
            await run_job(
                schedule.job_id,
                name,
                _build_job_callable(name, schedule),
                job_states,
                scheduler,
            )
        except Exception:
            logger.warning("Startup collector run failed and will be retried on schedule: %s", name)


async def run_scheduler(stop_event: asyncio.Event | None = None) -> None:
    """Start the scheduler and keep it alive until shutdown is requested."""
    load_environment()
    settings = load_scheduler_settings()
    scheduler: AsyncIOScheduler | None = None
    scheduler_started = False

    try:
        await get_pool()
        scheduler = AsyncIOScheduler(timezone=settings.timezone)
        job_states: dict[str, SchedulerJobState] = {}
        configure_scheduler(scheduler, settings, job_states)
        scheduler.start()
        scheduler_started = True
        logger.info("Collector scheduler started using %s", _SCHEDULE_PATH)
        log_scheduler_state(scheduler, job_states)

        shutdown_event = stop_event or asyncio.Event()
        await _run_startup_jobs(settings, job_states, scheduler)
        await shutdown_event.wait()
    finally:
        if scheduler is not None and scheduler_started:
            scheduler.shutdown(wait=True)
        await close_pool()
        logger.info("Collector scheduler stopped")


async def main() -> None:
    """Run the scheduler until the process receives a shutdown signal."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signal_name, stop_event.set)
        except NotImplementedError:
            pass
    await run_scheduler(stop_event)


if __name__ == "__main__":
    asyncio.run(main())
