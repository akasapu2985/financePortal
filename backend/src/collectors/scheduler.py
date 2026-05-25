"""Backward-compatible exports for the pipeline scheduler."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path


def _load_pipeline_scheduler():
    module_path = Path(__file__).resolve().parents[3] / "pipeline" / "src" / "scheduler.py"
    spec = importlib.util.spec_from_file_location("pipeline_scheduler", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load pipeline scheduler from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_pipeline_scheduler = _load_pipeline_scheduler()

CollectorSchedule = _pipeline_scheduler.CollectorSchedule
SchedulerJobState = _pipeline_scheduler.SchedulerJobState
SchedulerSettings = _pipeline_scheduler.SchedulerSettings
build_scheduler_state_snapshot = _pipeline_scheduler.build_scheduler_state_snapshot
configure_scheduler = _pipeline_scheduler.configure_scheduler
get_symbols = _pipeline_scheduler.get_symbols
is_market_hours = _pipeline_scheduler.is_market_hours
load_scheduler_settings = _pipeline_scheduler.load_scheduler_settings
log_scheduler_state = _pipeline_scheduler.log_scheduler_state
run_job = _pipeline_scheduler.run_job
run_news_collection = _pipeline_scheduler.run_news_collection
run_price_collection = _pipeline_scheduler.run_price_collection
run_scheduler = _pipeline_scheduler.run_scheduler
main = _pipeline_scheduler.main

__all__ = [
    "CollectorSchedule",
    "SchedulerJobState",
    "SchedulerSettings",
    "build_scheduler_state_snapshot",
    "configure_scheduler",
    "get_symbols",
    "is_market_hours",
    "load_scheduler_settings",
    "log_scheduler_state",
    "main",
    "run_job",
    "run_news_collection",
    "run_price_collection",
    "run_scheduler",
]


if __name__ == "__main__":
    asyncio.run(main())
