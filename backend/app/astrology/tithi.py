"""Deterministic Tithi lookup from sidereal Sun and Moon longitudes."""

from __future__ import annotations

import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.tithi import (
    FULL_CIRCLE_DEGREES,
    TITHI_COUNT,
    TITHI_LIST,
    TITHI_SPAN_DEGREES,
)

ANGLE_PRECISION = 6


class TithiResult(TypedDict):
    """Typed output for a Tithi lookup."""

    tithi_number: int
    name_en: str
    name_hi: str
    name_sa: str
    paksha: str
    start_angle: float
    end_angle: float
    current_angle: float
    degrees_completed: float
    degrees_remaining: float


def get_tithi(sun_longitude: float, moon_longitude: float) -> TithiResult:
    """Return Tithi details from sidereal Sun and Moon longitudes.

    Args:
        sun_longitude: Sidereal Sun longitude in degrees.
        moon_longitude: Sidereal Moon longitude in degrees.

    Returns:
        TithiResult containing Tithi number, names, paksha, angle boundaries,
        current Moon-Sun angle, and progress within the Tithi.

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
    current_angle = _normalize_longitude(
        normalized_moon_longitude - normalized_sun_longitude
    )
    tithi_number = min(
        int(current_angle // TITHI_SPAN_DEGREES) + 1,
        TITHI_COUNT,
    )
    tithi = TITHI_LIST[tithi_number - 1]
    degrees_completed = round(
        current_angle - tithi.start_angle,
        ANGLE_PRECISION,
    )
    degrees_remaining = round(
        tithi.end_angle - current_angle,
        ANGLE_PRECISION,
    )

    return {
        "tithi_number": tithi.number,
        "name_en": tithi.name_en,
        "name_hi": tithi.name_hi,
        "name_sa": tithi.name_sa,
        "paksha": tithi.paksha,
        "start_angle": tithi.start_angle,
        "end_angle": tithi.end_angle,
        "current_angle": current_angle,
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

    normalized = round(longitude % FULL_CIRCLE_DEGREES, ANGLE_PRECISION)
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized
