"""Ghati Lagna foundation helper."""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict

from backend.app.kundali import rashi as rashi_engine
from backend.app.kundali.hora_lagna import (
    HoraElapsedTime,
    LONGITUDE_PRECISION,
    _create_elapsed_time,
    _normalize_lagna_longitude,
    _parse_datetime,
)

GHATI_LAGNA_NAME = "ghati_lagna"
GHATI_FORMULA_STATUS = "foundation"
SECONDS_PER_GHATI = 24.0 * 60.0
GHATIS_PER_CIRCLE = 60.0
GHATI_LAGNA_DEGREES_PER_GHATI = 360.0 / GHATIS_PER_CIRCLE


class GhatiCalculationStep(TypedDict):
    """JSON-safe Ghati Lagna calculation step."""

    step: str
    value: float | str | None
    reason: str


class GhatiLagnaResult(TypedDict):
    """JSON-safe Ghati Lagna foundation result."""

    ghati_lagna_longitude: float | None
    rashi: rashi_engine.RashiResult | None
    rashi_index: int | None
    rashi_degree: float | None
    elapsed_time: HoraElapsedTime
    elapsed_ghatis: float | None
    calculation_steps: list[GhatiCalculationStep]
    metadata: dict[str, object]


def calculate_ghati_lagna(
    lagna_longitude: float,
    birth_datetime: datetime | str,
    sunrise_datetime: datetime | str | None,
) -> GhatiLagnaResult:
    """Calculate foundation-level Ghati Lagna from Lagna and sunrise metadata."""

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
            reason="Sunrise datetime is required for Ghati Lagna foundation.",
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

    elapsed_hours = elapsed_seconds / 3600.0
    elapsed_ghatis = elapsed_seconds / SECONDS_PER_GHATI
    elapsed_degrees = elapsed_ghatis * GHATI_LAGNA_DEGREES_PER_GHATI
    ghati_lagna_longitude = rashi_engine.normalize_longitude(
        normalized_lagna + elapsed_degrees
    )
    rashi = rashi_engine.get_rashi(ghati_lagna_longitude)
    rashi_degree = rashi_engine.get_rashi_degree(ghati_lagna_longitude)

    return {
        "ghati_lagna_longitude": round(ghati_lagna_longitude, LONGITUDE_PRECISION),
        "rashi": rashi,
        "rashi_index": rashi["index"],
        "rashi_degree": rashi_degree,
        "elapsed_time": _create_elapsed_time(
            elapsed_seconds=elapsed_seconds,
            elapsed_hours=elapsed_hours,
            birth_datetime=birth_dt,
            sunrise_datetime=sunrise_dt,
        ),
        "elapsed_ghatis": round(elapsed_ghatis, LONGITUDE_PRECISION),
        "calculation_steps": [
            {
                "step": "lagna_longitude",
                "value": normalized_lagna,
                "reason": "Lagna longitude was normalized into the zodiac circle.",
            },
            {
                "step": "elapsed_ghatis_from_sunrise",
                "value": round(elapsed_ghatis, LONGITUDE_PRECISION),
                "reason": "Elapsed time from sunrise to birth time in ghatis.",
            },
            {
                "step": "elapsed_degrees",
                "value": round(elapsed_degrees, LONGITUDE_PRECISION),
                "reason": "Foundation placeholder uses 6 degrees per elapsed ghati.",
            },
            {
                "step": "ghati_lagna_longitude",
                "value": round(ghati_lagna_longitude, LONGITUDE_PRECISION),
                "reason": "Elapsed degrees were added to Lagna longitude and normalized.",
            },
        ],
        "metadata": {
            "calculation_status": "calculated",
            "formula_status": GHATI_FORMULA_STATUS,
            "component": GHATI_LAGNA_NAME,
            "seconds_per_ghati": SECONDS_PER_GHATI,
            "degrees_per_ghati": GHATI_LAGNA_DEGREES_PER_GHATI,
            "missing_fields": [],
        },
    }


def _create_missing_result(
    *,
    missing_fields: list[str],
    reason: str,
    birth_datetime: datetime | None = None,
    sunrise_datetime: datetime | None = None,
) -> GhatiLagnaResult:
    """Create a JSON-safe result when required metadata is unavailable."""

    return {
        "ghati_lagna_longitude": None,
        "rashi": None,
        "rashi_index": None,
        "rashi_degree": None,
        "elapsed_time": _create_elapsed_time(
            elapsed_seconds=None,
            elapsed_hours=None,
            birth_datetime=birth_datetime,
            sunrise_datetime=sunrise_datetime,
        ),
        "elapsed_ghatis": None,
        "calculation_steps": [
            {
                "step": "missing_data",
                "value": ",".join(missing_fields),
                "reason": reason,
            }
        ],
        "metadata": {
            "calculation_status": "missing_data",
            "formula_status": GHATI_FORMULA_STATUS,
            "component": GHATI_LAGNA_NAME,
            "seconds_per_ghati": SECONDS_PER_GHATI,
            "degrees_per_ghati": GHATI_LAGNA_DEGREES_PER_GHATI,
            "missing_fields": list(missing_fields),
        },
    }
