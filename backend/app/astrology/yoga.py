"""Deterministic Panchang Yoga lookup from sidereal longitudes."""

from __future__ import annotations

import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.yoga import (
    FULL_CIRCLE_DEGREES,
    YOGA_COUNT,
    YOGA_LIST,
    YOGA_SPAN_DEGREES,
)

DEGREE_PRECISION = 6
YOGA_SPAN_FOR_LOOKUP = round(YOGA_SPAN_DEGREES, DEGREE_PRECISION)


class PanchangYogaResult(TypedDict):
    """Typed output for a Panchang Yoga lookup."""

    yoga_index: int
    name_en: str
    name_hi: str
    name_sa: str
    start_degree: float
    end_degree: float
    current_degree: float
    degrees_completed: float
    degrees_remaining: float


def get_panchang_yoga(
    sun_longitude: float,
    moon_longitude: float,
) -> PanchangYogaResult:
    """Return Panchang Yoga details from sidereal Sun and Moon longitudes.

    Args:
        sun_longitude: Sidereal Sun longitude in degrees.
        moon_longitude: Sidereal Moon longitude in degrees.

    Returns:
        PanchangYogaResult containing Yoga index, names, boundaries,
        current normalized Sun-Moon sum, and progress within the Yoga.

    Raises:
        TypeError: If either longitude is not a real number.
        ValueError: If either longitude is NaN or infinite.
    """

    normalized_sun_longitude = _normalize_longitude(
        _validate_longitude(sun_longitude, "sun_longitude")
    )
    normalized_moon_longitude = _normalize_longitude(
        _validate_longitude(moon_longitude, "moon_longitude")
    )
    current_degree = _normalize_longitude(
        normalized_sun_longitude + normalized_moon_longitude
    )
    yoga_index = min(
        int(current_degree // YOGA_SPAN_FOR_LOOKUP) + 1,
        YOGA_COUNT,
    )
    yoga = YOGA_LIST[yoga_index - 1]
    yoga_start_for_lookup = (yoga_index - 1) * YOGA_SPAN_FOR_LOOKUP
    degrees_completed = round(
        current_degree - yoga_start_for_lookup,
        DEGREE_PRECISION,
    )
    if degrees_completed < 0:
        degrees_completed = 0.0

    degrees_remaining = round(
        YOGA_SPAN_FOR_LOOKUP - degrees_completed,
        DEGREE_PRECISION,
    )

    return {
        "yoga_index": yoga.index,
        "name_en": yoga.name_en,
        "name_hi": yoga.name_hi,
        "name_sa": yoga.name_sa,
        "start_degree": yoga.start_degree,
        "end_degree": yoga.end_degree,
        "current_degree": current_degree,
        "degrees_completed": degrees_completed,
        "degrees_remaining": degrees_remaining,
    }


def _validate_longitude(longitude: float, field_name: str) -> float:
    """Validate a longitude value and return it as a float."""

    if isinstance(longitude, bool) or not isinstance(longitude, Real):
        raise TypeError(f"{field_name} must be a real number")

    longitude_float = float(longitude)
    if not math.isfinite(longitude_float):
        raise ValueError(f"{field_name} must be finite")

    return longitude_float


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the 0 <= longitude < 360 range."""

    normalized = round(longitude % FULL_CIRCLE_DEGREES, DEGREE_PRECISION)
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized
