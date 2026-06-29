"""Reusable numerical search helpers for astronomy boundaries."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
from numbers import Real
from typing import Callable

FULL_CIRCLE_DEGREES = 360.0
DEFAULT_SEARCH_STEP = timedelta(hours=6)
DEFAULT_MAX_SEARCH = timedelta(hours=48)
DEFAULT_TOLERANCE = timedelta(minutes=5)


def find_next_longitude_boundary(
    start_datetime_utc: datetime,
    value_at: Callable[[datetime], float],
    target_boundary: float,
    *,
    tolerance: timedelta = DEFAULT_TOLERANCE,
    max_search: timedelta = DEFAULT_MAX_SEARCH,
    search_step: timedelta = DEFAULT_SEARCH_STEP,
) -> datetime:
    """Find when an angular value next crosses a target longitude boundary.

    Args:
        start_datetime_utc: Search start datetime in UTC.
        value_at: Callable that returns the angular value in degrees for a UTC
            datetime.
        target_boundary: Target boundary in degrees. Values are normalized into
            the ``0 <= value < 360`` range.
        tolerance: Maximum final time window for the binary search.
        max_search: Maximum forward search duration.
        search_step: Step used while bracketing the crossing.

    Returns:
        UTC datetime at or just after the target boundary crossing.

    Raises:
        TypeError: If inputs have invalid types.
        ValueError: If numeric or duration inputs are invalid.
        RuntimeError: If the boundary is not found within ``max_search``.
    """

    start_datetime = _validate_utc_datetime(start_datetime_utc)
    target = _normalize_degrees(_validate_angle(target_boundary, "target_boundary"))
    tolerance_value = _validate_positive_timedelta(tolerance, "tolerance")
    max_search_value = _validate_positive_timedelta(max_search, "max_search")
    search_step_value = _validate_positive_timedelta(search_step, "search_step")

    if not callable(value_at):
        raise TypeError("value_at must be callable")

    start_value = _normalize_degrees(_validate_angle(value_at(start_datetime), "value_at"))
    required_delta = (target - start_value) % FULL_CIRCLE_DEGREES
    if required_delta == 0.0:
        required_delta = FULL_CIRCLE_DEGREES

    low = start_datetime
    high = start_datetime
    search_end = start_datetime + max_search_value

    while high < search_end:
        high = min(high + search_step_value, search_end)
        if _forward_delta(value_at(high), start_value) >= required_delta:
            break
    else:
        raise RuntimeError("Longitude boundary was not found within max_search")

    if _forward_delta(value_at(high), start_value) < required_delta:
        raise RuntimeError("Longitude boundary was not found within max_search")

    while high - low > tolerance_value:
        midpoint = low + ((high - low) / 2)
        if _forward_delta(value_at(midpoint), start_value) >= required_delta:
            high = midpoint
        else:
            low = midpoint

    return high.astimezone(timezone.utc)


def _validate_utc_datetime(value: datetime) -> datetime:
    """Validate and normalize a timezone-aware datetime to UTC."""

    if not isinstance(value, datetime):
        raise TypeError("start_datetime_utc must be a datetime")

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("start_datetime_utc must be timezone-aware")

    return value.astimezone(timezone.utc)


def _validate_angle(value: float, name: str) -> float:
    """Validate a finite angular value."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")

    return numeric_value


def _validate_positive_timedelta(value: timedelta, name: str) -> timedelta:
    """Validate a positive timedelta."""

    if not isinstance(value, timedelta):
        raise TypeError(f"{name} must be a timedelta")

    if value.total_seconds() <= 0:
        raise ValueError(f"{name} must be positive")

    return value


def _normalize_degrees(value: float) -> float:
    """Normalize an angle into the ``0 <= value < 360`` range."""

    return value % FULL_CIRCLE_DEGREES


def _forward_delta(value: float, start_value: float) -> float:
    """Return forward angular distance from the start value."""

    normalized_value = _normalize_degrees(_validate_angle(value, "value_at"))
    return (normalized_value - start_value) % FULL_CIRCLE_DEGREES
