"""Pure helpers for the accelerated 24-hour simulation."""
from __future__ import annotations

from typing import Any


MIN_TIME_LAPSE_DURATION_MINUTES = 1
MAX_TIME_LAPSE_DURATION_MINUTES = 10
DEFAULT_TIME_LAPSE_DURATION_MINUTES = 1
MINUTES_PER_DAY = 1440


def normalize_time_lapse_duration(value: Any) -> float:
    """Return a valid full-day duration between one and ten minutes."""
    try:
        duration = float(value)
    except (TypeError, ValueError):
        duration = DEFAULT_TIME_LAPSE_DURATION_MINUTES
    return max(
        MIN_TIME_LAPSE_DURATION_MINUTES,
        min(MAX_TIME_LAPSE_DURATION_MINUTES, duration),
    )


def advance_time_lapse_position(
    position_minutes: float,
    elapsed_seconds: float,
    duration_minutes: Any,
) -> float:
    """Advance the simulated minute while keeping a precise fractional position."""
    duration = normalize_time_lapse_duration(duration_minutes)
    simulated_minutes_per_second = MINUTES_PER_DAY / (duration * 60)
    return (
        float(position_minutes)
        + (max(0.0, float(elapsed_seconds)) * simulated_minutes_per_second)
    ) % MINUTES_PER_DAY


def is_time_lapse_cycle_complete(
    elapsed_seconds: Any,
    duration_minutes: Any,
) -> bool:
    """Return whether one complete accelerated day has elapsed."""
    try:
        elapsed = max(0.0, float(elapsed_seconds))
    except (TypeError, ValueError):
        elapsed = 0.0
    return elapsed >= normalize_time_lapse_duration(duration_minutes) * 60
