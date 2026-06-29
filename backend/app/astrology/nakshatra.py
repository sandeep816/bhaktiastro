"""Deterministic Nakshatra lookup from sidereal longitude."""

from __future__ import annotations

import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.nakshatra import (
    FULL_CIRCLE_DEGREES,
    NAKSHATRA_COUNT,
    NAKSHATRA_LIST,
    NAKSHATRA_SPAN_DEGREES,
)

PADA_COUNT = 4
BOUNDARY_PRECISION = 6
NAKSHATRA_SPAN_FOR_LOOKUP = round(NAKSHATRA_SPAN_DEGREES, BOUNDARY_PRECISION)
PADA_SPAN_DEGREES = round(
    NAKSHATRA_SPAN_FOR_LOOKUP / PADA_COUNT,
    BOUNDARY_PRECISION,
)


class NakshatraResult(TypedDict):
    """Typed output for a Nakshatra lookup."""

    index: int
    name_en: str
    name_hi: str
    name_sa: str
    pada: int
    ruling_planet: str
    start_degree: float
    end_degree: float
    degree_within_nakshatra: float


def get_nakshatra(longitude: float) -> NakshatraResult:
    """Return Nakshatra and Pada details for a sidereal longitude.

    Args:
        longitude: Sidereal longitude in degrees. Values outside the
            0 <= longitude < 360 range are normalized before lookup.

    Returns:
        NakshatraResult containing index, names, pada, ruling planet,
        Nakshatra boundary degrees, and degree within the Nakshatra.

    Raises:
        TypeError: If longitude is not a real number.
        ValueError: If longitude is NaN or infinite.
    """

    if isinstance(longitude, bool) or not isinstance(longitude, Real):
        raise TypeError("longitude must be a real number")

    longitude_float = float(longitude)
    if not math.isfinite(longitude_float):
        raise ValueError("longitude must be finite")

    normalized_longitude = _normalize_longitude(longitude_float)
    index = min(
        int(normalized_longitude // NAKSHATRA_SPAN_FOR_LOOKUP),
        NAKSHATRA_COUNT - 1,
    )
    nakshatra = NAKSHATRA_LIST[index]
    degree_within_nakshatra = round(
        normalized_longitude - (index * NAKSHATRA_SPAN_FOR_LOOKUP),
        BOUNDARY_PRECISION,
    )
    if degree_within_nakshatra < 0:
        degree_within_nakshatra = 0.0

    pada = min(
        int(degree_within_nakshatra // PADA_SPAN_DEGREES) + 1,
        PADA_COUNT,
    )

    return {
        "index": nakshatra.index,
        "name_en": nakshatra.name_en,
        "name_hi": nakshatra.name_hi,
        "name_sa": nakshatra.name_sa,
        "pada": pada,
        "ruling_planet": nakshatra.ruling_planet,
        "start_degree": nakshatra.start_degree,
        "end_degree": nakshatra.end_degree,
        "degree_within_nakshatra": degree_within_nakshatra,
    }


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the 0 <= longitude < 360 range."""

    normalized = round(longitude % FULL_CIRCLE_DEGREES, BOUNDARY_PRECISION)
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized
