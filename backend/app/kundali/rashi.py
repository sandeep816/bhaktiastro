"""Deterministic Rashi lookup from sidereal longitude."""

from __future__ import annotations

import math
from numbers import Real
from typing import TypedDict

from backend.app.constants.rashi import (
    FULL_CIRCLE_DEGREES,
    RASHI_COUNT,
    RASHI_LIST,
    RASHI_SPAN_DEGREES,
)

DEGREE_PRECISION = 6


class RashiResult(TypedDict):
    """Typed output for a Rashi lookup."""

    index: int
    english: str
    hindi: str
    sanskrit: str
    lord: str
    element: str
    modality: str
    start_degree: float
    end_degree: float
    degree_in_rashi: float


def get_rashi(longitude: float) -> RashiResult:
    """Return Rashi details for a sidereal longitude.

    Args:
        longitude: Sidereal longitude in degrees. Values outside the
            0 <= longitude < 360 range are normalized before lookup.

    Returns:
        RashiResult containing one-based index, names, lord, element,
        modality, Rashi boundary degrees, and degree within the Rashi.

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
    list_index = min(
        int(normalized_longitude // RASHI_SPAN_DEGREES),
        RASHI_COUNT - 1,
    )
    rashi = RASHI_LIST[list_index]
    degree_in_rashi = round(
        normalized_longitude - rashi.start_degree,
        DEGREE_PRECISION,
    )
    if degree_in_rashi < 0:
        degree_in_rashi = 0.0

    return {
        "index": rashi.index,
        "english": rashi.english,
        "hindi": rashi.hindi,
        "sanskrit": rashi.sanskrit,
        "lord": rashi.lord,
        "element": rashi.element,
        "modality": rashi.modality,
        "start_degree": rashi.start_degree,
        "end_degree": rashi.end_degree,
        "degree_in_rashi": degree_in_rashi,
    }


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the `[0, 360)` range."""

    normalized = round(longitude % FULL_CIRCLE_DEGREES, DEGREE_PRECISION)
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized

