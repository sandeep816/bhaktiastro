"""Deterministic Karana lookup from sidereal Sun and Moon longitudes."""

from __future__ import annotations

import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.karana import (
    FIXED_KARANAS,
    REPEATING_KARANAS,
    Karana,
)

FULL_CIRCLE_DEGREES = 360.0
HALF_TITHI_COUNT = 60
KARANA_SPAN_DEGREES = FULL_CIRCLE_DEGREES / HALF_TITHI_COUNT
DEGREE_PRECISION = 6


class KaranaResult(TypedDict):
    """Typed output for a Karana lookup."""

    karana_index: int
    name_en: str
    name_hi: str
    name_sa: str
    type: str
    half_tithi_index: int
    current_angle: float
    start_angle: float
    end_angle: float
    degrees_completed: float
    degrees_remaining: float


def get_karana(sun_longitude: float, moon_longitude: float) -> KaranaResult:
    """Return Karana details from sidereal Sun and Moon longitudes.

    Args:
        sun_longitude: Sidereal Sun longitude in degrees.
        moon_longitude: Sidereal Moon longitude in degrees.

    Returns:
        KaranaResult containing Karana metadata, half-tithi index,
        current Moon-Sun angle, and progress within the six-degree span.

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
    half_tithi_index = min(
        int(current_angle // KARANA_SPAN_DEGREES),
        HALF_TITHI_COUNT - 1,
    )
    karana = _karana_for_half_tithi_index(half_tithi_index)
    start_angle = half_tithi_index * KARANA_SPAN_DEGREES
    end_angle = start_angle + KARANA_SPAN_DEGREES
    degrees_completed = round(current_angle - start_angle, DEGREE_PRECISION)
    degrees_remaining = round(end_angle - current_angle, DEGREE_PRECISION)

    return {
        "karana_index": karana.index,
        "name_en": karana.name_en,
        "name_hi": karana.name_hi,
        "name_sa": karana.name_sa,
        "type": karana.type,
        "half_tithi_index": half_tithi_index,
        "current_angle": current_angle,
        "start_angle": start_angle,
        "end_angle": end_angle,
        "degrees_completed": degrees_completed,
        "degrees_remaining": degrees_remaining,
    }


def _karana_for_half_tithi_index(half_tithi_index: int) -> Karana:
    """Return the Karana definition for a verified half-tithi position."""

    if half_tithi_index == 0:
        return FIXED_KARANAS[-1]
    if half_tithi_index == 57:
        return FIXED_KARANAS[0]
    if half_tithi_index == 58:
        return FIXED_KARANAS[1]
    if half_tithi_index == 59:
        return FIXED_KARANAS[2]

    repeating_index = (half_tithi_index - 1) % len(REPEATING_KARANAS)
    return REPEATING_KARANAS[repeating_index]


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
