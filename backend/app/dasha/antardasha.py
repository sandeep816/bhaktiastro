"""Antardasha generation helpers."""

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

YEAR_PRECISION = 6


class AntardashaPeriod(TypedDict):
    """JSON-safe Antardasha period output."""

    mahadasha_lord: str
    antardasha_lord: str
    start_datetime: str
    end_datetime: str
    duration_years: float


def generate_antardasha_periods(
    mahadasha_lord: str,
    mahadasha_start: datetime | str,
    mahadasha_end: datetime | str,
    mahadasha_duration_years: float,
) -> list[AntardashaPeriod]:
    """Generate Antardasha periods within one Mahadasha.

    Args:
        mahadasha_lord: Vimshottari Mahadasha lord.
        mahadasha_start: Mahadasha start datetime or ISO datetime string.
        mahadasha_end: Mahadasha end datetime or ISO datetime string.
        mahadasha_duration_years: Mahadasha duration in years.

    Returns:
        JSON-safe Antardasha period dictionaries bounded by the supplied
        Mahadasha start and end datetimes.

    Raises:
        TypeError: If datetime or duration inputs have invalid types.
        ValueError: If the Dasha lord is unsupported, datetime strings are
            invalid, date bounds are invalid, or duration is non-positive.
    """

    normalized_mahadasha_lord = _normalize_dasha_lord(mahadasha_lord)
    start_datetime = _parse_dasha_datetime(mahadasha_start, "mahadasha_start")
    end_datetime = _parse_dasha_datetime(mahadasha_end, "mahadasha_end")
    _validate_datetime_bounds(start_datetime, end_datetime)
    duration_years = _validate_duration_years(mahadasha_duration_years)

    sequence = get_dasha_sequence()
    antardasha_lords = _rotate_sequence(sequence, normalized_mahadasha_lord)
    total_seconds = (end_datetime - start_datetime).total_seconds()

    periods: list[AntardashaPeriod] = []
    elapsed_years = 0.0
    current_start = start_datetime

    for index, antardasha_lord in enumerate(antardasha_lords):
        antardasha_duration = _calculate_antardasha_duration(
            duration_years,
            antardasha_lord,
        )
        elapsed_years += antardasha_duration
        current_end = (
            end_datetime
            if index == len(antardasha_lords) - 1
            else start_datetime
            + (end_datetime - start_datetime)
            * (elapsed_years / duration_years)
        )
        periods.append(
            {
                "mahadasha_lord": normalized_mahadasha_lord,
                "antardasha_lord": antardasha_lord,
                "start_datetime": current_start.isoformat(timespec="seconds"),
                "end_datetime": current_end.isoformat(timespec="seconds"),
                "duration_years": round(antardasha_duration, YEAR_PRECISION),
            }
        )
        current_start = current_end

    if total_seconds <= 0:
        raise ValueError("Mahadasha datetime range must be positive")

    return periods


def _calculate_antardasha_duration(
    mahadasha_duration_years: float,
    antardasha_lord: str,
) -> float:
    """Calculate one Antardasha duration in Dasha years."""

    return (
        mahadasha_duration_years
        * get_dasha_duration(antardasha_lord)
        / VIMSHOTTARI_TOTAL_CYCLE_YEARS
    )


def _rotate_sequence(sequence: tuple[str, ...], start_lord: str) -> tuple[str, ...]:
    """Return Vimshottari sequence starting from a given lord."""

    start_index = sequence.index(start_lord)
    return sequence[start_index:] + sequence[:start_index]


def _normalize_dasha_lord(dasha_lord: str) -> str:
    """Normalize and validate a Vimshottari Dasha lord."""

    if not isinstance(dasha_lord, str):
        raise TypeError("mahadasha_lord must be a string")

    normalized = dasha_lord.strip().lower()
    get_dasha_duration(normalized)
    return normalized


def _parse_dasha_datetime(
    value: datetime | str,
    field_name: str,
) -> datetime:
    """Parse and validate a Dasha datetime input."""

    if isinstance(value, datetime):
        return value.replace(microsecond=0)

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).replace(microsecond=0)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid ISO datetime") from exc

    raise TypeError(f"{field_name} must be a datetime object or ISO datetime string")


def _validate_datetime_bounds(
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:
    """Validate Mahadasha datetime bounds."""

    try:
        if end_datetime <= start_datetime:
            raise ValueError("mahadasha_end must be after mahadasha_start")
    except TypeError as exc:
        raise ValueError(
            "mahadasha_start and mahadasha_end must use matching timezone style"
        ) from exc


def _validate_duration_years(duration_years: float) -> float:
    """Validate Mahadasha duration years."""

    if isinstance(duration_years, bool) or not isinstance(duration_years, Real):
        raise TypeError("mahadasha_duration_years must be a real number")

    duration_float = float(duration_years)
    if not math.isfinite(duration_float) or duration_float <= 0.0:
        raise ValueError("mahadasha_duration_years must be finite and positive")

    return duration_float
