"""Hora Lagna foundation helper."""

from __future__ import annotations

from datetime import datetime
import math
from numbers import Real
from typing import Any, TypedDict

from backend.app.kundali import rashi as rashi_engine

HORA_LAGNA_NAME = "hora_lagna"
HORA_FORMULA_STATUS = "foundation"
LONGITUDE_PRECISION = 6
SECONDS_PER_HOUR = 3600.0
HORA_LAGNA_DEGREES_PER_HOUR = 15.0


class HoraCalculationStep(TypedDict):
    """JSON-safe Hora Lagna calculation step."""

    step: str
    value: float | str | None
    reason: str


class HoraElapsedTime(TypedDict):
    """JSON-safe elapsed time metadata for Hora Lagna."""

    seconds: float | None
    hours: float | None
    birth_datetime: str | None
    sunrise_datetime: str | None


class HoraLagnaResult(TypedDict):
    """JSON-safe Hora Lagna foundation result."""

    hora_lagna_longitude: float | None
    rashi: rashi_engine.RashiResult | None
    rashi_index: int | None
    rashi_degree: float | None
    elapsed_time: HoraElapsedTime
    calculation_steps: list[HoraCalculationStep]
    metadata: dict[str, object]


def calculate_hora_lagna(
    lagna_longitude: float,
    birth_datetime: datetime | str,
    sunrise_datetime: datetime | str | None,
) -> HoraLagnaResult:
    """Calculate foundation-level Hora Lagna from Lagna and sunrise metadata."""

    normalized_lagna = _normalize_lagna_longitude(lagna_longitude)
    if normalized_lagna is None:
        return _create_missing_result(
            missing_fields=["lagna_longitude"],
            reason="Lagna longitude must be a finite real number.",
        )

    birth_dt = _parse_datetime(birth_datetime)
    if birth_dt is None:
        return _create_missing_result(
            missing_fields=["birth_datetime"],
            reason="Birth datetime must be a datetime object or ISO datetime string.",
        )

    if sunrise_datetime is None:
        return _create_missing_result(
            missing_fields=["sunrise_datetime"],
            reason="Sunrise datetime is required for Hora Lagna foundation.",
            birth_datetime=birth_dt,
        )

    sunrise_dt = _parse_datetime(sunrise_datetime)
    if sunrise_dt is None:
        return _create_missing_result(
            missing_fields=["sunrise_datetime"],
            reason="Sunrise datetime must be a datetime object or ISO datetime string.",
            birth_datetime=birth_dt,
        )

    try:
        elapsed_seconds = (birth_dt - sunrise_dt).total_seconds()
    except TypeError:
        return _create_missing_result(
            missing_fields=["datetime_timezone"],
            reason="Birth and sunrise datetimes must both be naive or both timezone-aware.",
            birth_datetime=birth_dt,
            sunrise_datetime=sunrise_dt,
        )

    elapsed_hours = elapsed_seconds / SECONDS_PER_HOUR
    elapsed_degrees = elapsed_hours * HORA_LAGNA_DEGREES_PER_HOUR
    hora_lagna_longitude = rashi_engine.normalize_longitude(
        normalized_lagna + elapsed_degrees
    )
    rashi = rashi_engine.get_rashi(hora_lagna_longitude)
    rashi_degree = rashi_engine.get_rashi_degree(hora_lagna_longitude)

    return {
        "hora_lagna_longitude": round(hora_lagna_longitude, LONGITUDE_PRECISION),
        "rashi": rashi,
        "rashi_index": rashi["index"],
        "rashi_degree": rashi_degree,
        "elapsed_time": _create_elapsed_time(
            elapsed_seconds=elapsed_seconds,
            elapsed_hours=elapsed_hours,
            birth_datetime=birth_dt,
            sunrise_datetime=sunrise_dt,
        ),
        "calculation_steps": [
            {
                "step": "lagna_longitude",
                "value": normalized_lagna,
                "reason": "Lagna longitude was normalized into the zodiac circle.",
            },
            {
                "step": "elapsed_hours_from_sunrise",
                "value": round(elapsed_hours, LONGITUDE_PRECISION),
                "reason": "Elapsed time from sunrise to birth time.",
            },
            {
                "step": "elapsed_degrees",
                "value": round(elapsed_degrees, LONGITUDE_PRECISION),
                "reason": "Foundation placeholder uses 15 degrees per elapsed hour.",
            },
            {
                "step": "hora_lagna_longitude",
                "value": round(hora_lagna_longitude, LONGITUDE_PRECISION),
                "reason": "Elapsed degrees were added to Lagna longitude and normalized.",
            },
        ],
        "metadata": {
            "calculation_status": "calculated",
            "formula_status": HORA_FORMULA_STATUS,
            "component": HORA_LAGNA_NAME,
            "degrees_per_hour": HORA_LAGNA_DEGREES_PER_HOUR,
            "missing_fields": [],
        },
    }


def _create_missing_result(
    *,
    missing_fields: list[str],
    reason: str,
    birth_datetime: datetime | None = None,
    sunrise_datetime: datetime | None = None,
) -> HoraLagnaResult:
    """Create a JSON-safe result when required metadata is unavailable."""

    return {
        "hora_lagna_longitude": None,
        "rashi": None,
        "rashi_index": None,
        "rashi_degree": None,
        "elapsed_time": _create_elapsed_time(
            elapsed_seconds=None,
            elapsed_hours=None,
            birth_datetime=birth_datetime,
            sunrise_datetime=sunrise_datetime,
        ),
        "calculation_steps": [
            {
                "step": "missing_data",
                "value": ",".join(missing_fields),
                "reason": reason,
            }
        ],
        "metadata": {
            "calculation_status": "missing_data",
            "formula_status": HORA_FORMULA_STATUS,
            "component": HORA_LAGNA_NAME,
            "degrees_per_hour": HORA_LAGNA_DEGREES_PER_HOUR,
            "missing_fields": list(missing_fields),
        },
    }


def _create_elapsed_time(
    *,
    elapsed_seconds: float | None,
    elapsed_hours: float | None,
    birth_datetime: datetime | None,
    sunrise_datetime: datetime | None,
) -> HoraElapsedTime:
    """Create JSON-safe elapsed time metadata."""

    return {
        "seconds": (
            round(elapsed_seconds, LONGITUDE_PRECISION)
            if elapsed_seconds is not None
            else None
        ),
        "hours": (
            round(elapsed_hours, LONGITUDE_PRECISION)
            if elapsed_hours is not None
            else None
        ),
        "birth_datetime": (
            birth_datetime.isoformat(timespec="seconds")
            if birth_datetime is not None
            else None
        ),
        "sunrise_datetime": (
            sunrise_datetime.isoformat(timespec="seconds")
            if sunrise_datetime is not None
            else None
        ),
    }


def _normalize_lagna_longitude(lagna_longitude: float) -> float | None:
    """Return normalized Lagna longitude, or None for invalid input."""

    if isinstance(lagna_longitude, bool) or not isinstance(lagna_longitude, Real):
        return None

    longitude = float(lagna_longitude)
    if not math.isfinite(longitude):
        return None

    return rashi_engine.normalize_longitude(longitude)


def _parse_datetime(value: datetime | str) -> datetime | None:
    """Parse a datetime object or ISO datetime string without raising."""

    if isinstance(value, datetime):
        return value.replace(microsecond=0)

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).replace(microsecond=0)
        except ValueError:
            return None

    return None
