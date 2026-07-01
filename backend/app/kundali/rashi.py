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

    list_index = get_rashi_index(longitude) - 1
    rashi = RASHI_LIST[list_index]

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
        "degree_in_rashi": get_rashi_degree(longitude),
    }


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the `[0, 360)` range."""

    longitude_float = _validate_longitude(longitude)
    normalized = round(longitude_float % FULL_CIRCLE_DEGREES, DEGREE_PRECISION)
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized


def get_rashi_index(longitude: float) -> int:
    """Return the one-based Rashi index for a longitude."""

    normalized_longitude = normalize_longitude(longitude)
    return (
        min(
            int(normalized_longitude // RASHI_SPAN_DEGREES),
            RASHI_COUNT - 1,
        )
        + 1
    )


def get_rashi_degree(longitude: float) -> float:
    """Return the degree completed within the current Rashi."""

    normalized_longitude = normalize_longitude(longitude)
    list_index = get_rashi_index(normalized_longitude) - 1
    degree_in_rashi = round(
        normalized_longitude - RASHI_LIST[list_index].start_degree,
        DEGREE_PRECISION,
    )
    if degree_in_rashi < 0:
        return 0.0
    return degree_in_rashi


def _validate_longitude(longitude: float) -> float:
    """Validate longitude as a finite real number."""

    if isinstance(longitude, bool) or not isinstance(longitude, Real):
        raise TypeError("longitude must be a real number")

    longitude_float = float(longitude)
    if not math.isfinite(longitude_float):
        raise ValueError("longitude must be finite")

    return longitude_float
