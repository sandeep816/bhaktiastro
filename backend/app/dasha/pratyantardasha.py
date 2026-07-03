"""Pratyantardasha generation helpers."""

from __future__ import annotations

from datetime import datetime
import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.dasha import (
    VIMSHOTTARI_TOTAL_CYCLE_YEARS,
    get_dasha_duration,
    get_dasha_sequence,
)
from backend.app.dasha.antardasha import (
    _parse_dasha_datetime,
    _rotate_sequence,
    _validate_datetime_bounds,
)

YEAR_PRECISION = 6


class PratyantardashaPeriod(TypedDict):
    """JSON-safe Pratyantardasha period output."""

    mahadasha_lord: str
    antardasha_lord: str
    pratyantardasha_lord: str
    start_datetime: str
    end_datetime: str
    duration_years: float


def generate_pratyantardasha_periods(
    mahadasha_lord: str,
    antardasha_lord: str,
    antardasha_start: datetime | str,
    antardasha_end: datetime | str,
    antardasha_duration_years: float,
) -> list[PratyantardashaPeriod]:
    """Generate Pratyantardasha periods within one Antardasha.

    Args:
        mahadasha_lord: Vimshottari Mahadasha lord.
        antardasha_lord: Vimshottari Antardasha lord.
        antardasha_start: Antardasha start datetime or ISO datetime string.
        antardasha_end: Antardasha end datetime or ISO datetime string.
        antardasha_duration_years: Antardasha duration in years.

    Returns:
        JSON-safe Pratyantardasha period dictionaries bounded by the supplied
        Antardasha start and end datetimes.

    Raises:
        TypeError: If datetime or duration inputs have invalid types.
        ValueError: If a Dasha lord is unsupported, datetime strings are
            invalid, date bounds are invalid, or duration is non-positive.
    """

    normalized_mahadasha_lord = _normalize_dasha_lord(
        mahadasha_lord,
        "mahadasha_lord",
    )
    normalized_antardasha_lord = _normalize_dasha_lord(
        antardasha_lord,
        "antardasha_lord",
    )
    start_datetime = _parse_dasha_datetime(antardasha_start, "antardasha_start")
    end_datetime = _parse_dasha_datetime(antardasha_end, "antardasha_end")
    _validate_datetime_bounds(start_datetime, end_datetime)
    duration_years = _validate_duration_years(antardasha_duration_years)

    sequence = get_dasha_sequence()
    pratyantardasha_lords = _rotate_sequence(sequence, normalized_antardasha_lord)

    periods: list[PratyantardashaPeriod] = []
    elapsed_years = 0.0
    current_start = start_datetime

    for index, pratyantardasha_lord in enumerate(pratyantardasha_lords):
        pratyantardasha_duration = _calculate_pratyantardasha_duration(
            duration_years,
            pratyantardasha_lord,
        )
        elapsed_years += pratyantardasha_duration
        current_end = (
            end_datetime
            if index == len(pratyantardasha_lords) - 1
            else start_datetime
            + (end_datetime - start_datetime)
            * (elapsed_years / duration_years)
        )
        periods.append(
            {
                "mahadasha_lord": normalized_mahadasha_lord,
                "antardasha_lord": normalized_antardasha_lord,
                "pratyantardasha_lord": pratyantardasha_lord,
                "start_datetime": current_start.isoformat(timespec="seconds"),
                "end_datetime": current_end.isoformat(timespec="seconds"),
                "duration_years": round(pratyantardasha_duration, YEAR_PRECISION),
            }
        )
        current_start = current_end

    return periods


def _calculate_pratyantardasha_duration(
    antardasha_duration_years: float,
    pratyantardasha_lord: str,
) -> float:
    """Calculate one Pratyantardasha duration in Dasha years."""

    return (
        antardasha_duration_years
        * get_dasha_duration(pratyantardasha_lord)
        / VIMSHOTTARI_TOTAL_CYCLE_YEARS
    )


def _normalize_dasha_lord(dasha_lord: str, field_name: str) -> str:
    """Normalize and validate a Vimshottari Dasha lord."""

    if not isinstance(dasha_lord, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = dasha_lord.strip().lower()
    get_dasha_duration(normalized)
    return normalized


def _validate_duration_years(duration_years: float) -> float:
    """Validate Antardasha duration years."""

    if isinstance(duration_years, bool) or not isinstance(duration_years, Real):
        raise TypeError("antardasha_duration_years must be a real number")

    duration_float = float(duration_years)
    if not math.isfinite(duration_float) or duration_float <= 0.0:
        raise ValueError("antardasha_duration_years must be finite and positive")

    return duration_float
