"""Mahadasha timeline generation helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.dasha import get_dasha_duration, get_dasha_sequence
from backend.app.dasha.balance import calculate_birth_dasha_balance

DAYS_PER_DASHA_YEAR = 365.25
TIMELINE_COVERAGE_YEARS = 120.0
YEAR_PRECISION = 6


class MahadashaPeriod(TypedDict):
    """JSON-safe Mahadasha period output."""

    dasha_lord: str
    start_datetime: str
    end_datetime: str
    duration_years: float
    is_birth_dasha: bool


def generate_mahadasha_timeline(
    birth_datetime: datetime | str,
    nakshatra_index: int,
    moon_longitude: float,
) -> list[MahadashaPeriod]:
    """Generate a Vimshottari Mahadasha timeline from birth.

    Args:
        birth_datetime: Birth datetime as a ``datetime`` object or ISO string.
            Naive and timezone-aware datetimes are preserved as supplied.
        nakshatra_index: Zero-based birth Nakshatra index.
        moon_longitude: Moon sidereal longitude in degrees.

    Returns:
        JSON-safe Mahadasha period dictionaries covering at least 120 Dasha
        years from birth.

    Raises:
        TypeError: If birth_datetime is not a datetime or ISO string.
        ValueError: If birth_datetime is an invalid string or if balance inputs
            are invalid.
    """

    timeline_start = _parse_birth_datetime(birth_datetime)
    birth_balance = calculate_birth_dasha_balance(nakshatra_index, moon_longitude)
    sequence = get_dasha_sequence()
    current_lord_index = sequence.index(birth_balance["dasha_lord"])

    periods: list[MahadashaPeriod] = []
    elapsed_years = 0.0
    current_start = timeline_start

    birth_duration = _validate_duration_years(birth_balance["balance_years"])
    current_end = _add_dasha_years(current_start, birth_duration)
    periods.append(
        _build_period(
            dasha_lord=birth_balance["dasha_lord"],
            start_datetime=current_start,
            end_datetime=current_end,
            duration_years=birth_duration,
            is_birth_dasha=True,
        )
    )
    elapsed_years += birth_duration
    current_start = current_end
    current_lord_index = _next_lord_index(current_lord_index, sequence)

    while elapsed_years < TIMELINE_COVERAGE_YEARS:
        dasha_lord = sequence[current_lord_index]
        duration_years = float(get_dasha_duration(dasha_lord))
        current_end = _add_dasha_years(current_start, duration_years)
        periods.append(
            _build_period(
                dasha_lord=dasha_lord,
                start_datetime=current_start,
                end_datetime=current_end,
                duration_years=duration_years,
                is_birth_dasha=False,
            )
        )
        elapsed_years += duration_years
        current_start = current_end
        current_lord_index = _next_lord_index(current_lord_index, sequence)

    return periods


def _parse_birth_datetime(birth_datetime: datetime | str) -> datetime:
    """Parse and validate a birth datetime input."""

    if isinstance(birth_datetime, datetime):
        return birth_datetime.replace(microsecond=0)

    if isinstance(birth_datetime, str):
        try:
            return datetime.fromisoformat(birth_datetime).replace(microsecond=0)
        except ValueError as exc:
            raise ValueError("birth_datetime must be a valid ISO datetime") from exc

    raise TypeError("birth_datetime must be a datetime object or ISO datetime string")


def _build_period(
    dasha_lord: str,
    start_datetime: datetime,
    end_datetime: datetime,
    duration_years: float,
    is_birth_dasha: bool,
) -> MahadashaPeriod:
    """Build one JSON-safe Mahadasha period."""

    return {
        "dasha_lord": dasha_lord,
        "start_datetime": start_datetime.isoformat(timespec="seconds"),
        "end_datetime": end_datetime.isoformat(timespec="seconds"),
        "duration_years": round(duration_years, YEAR_PRECISION),
        "is_birth_dasha": is_birth_dasha,
    }


def _add_dasha_years(start_datetime: datetime, years: float) -> datetime:
    """Add deterministic Dasha years to a datetime."""

    return start_datetime + timedelta(days=years * DAYS_PER_DASHA_YEAR)


def _validate_duration_years(duration_years: float) -> float:
    """Validate a calculated Dasha duration."""

    if not isinstance(duration_years, Real):
        raise TypeError("duration_years must be a real number")

    duration_float = float(duration_years)
    if not math.isfinite(duration_float) or duration_float < 0:
        raise ValueError("duration_years must be finite and non-negative")

    return duration_float


def _next_lord_index(current_index: int, sequence: tuple[str, ...]) -> int:
    """Return the next Dasha lord index in the Vimshottari sequence."""

    return (current_index + 1) % len(sequence)
