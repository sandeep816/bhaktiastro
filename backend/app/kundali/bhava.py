"""Foundation helpers for placeholder Bhava house divisions."""

from __future__ import annotations

import math
from numbers import Integral, Real

from backend.app.kundali.rashi import normalize_longitude

FULL_CIRCLE_DEGREES = 360.0
HOUSE_COUNT = 12
HOUSE_SPAN_DEGREES = FULL_CIRCLE_DEGREES / HOUSE_COUNT
HOUSE_NUMBERS = tuple(range(1, HOUSE_COUNT + 1))
DEGREE_PRECISION = 6


def normalize_house_number(house: int) -> int:
    """Normalize any integer house value into the `1..12` range."""

    if isinstance(house, bool) or not isinstance(house, Integral):
        raise TypeError("house must be an integer")

    return ((int(house) - 1) % HOUSE_COUNT) + 1


def get_house_index_from_degree(degree: float) -> int:
    """Return the zero-based placeholder house index for a degree."""

    normalized_degree = normalize_longitude(_validate_degree(degree))
    return min(
        int(normalized_degree // HOUSE_SPAN_DEGREES),
        HOUSE_COUNT - 1,
    )


def get_house_number_from_degree(degree: float) -> int:
    """Return the one-based placeholder house number for a degree."""

    return get_house_index_from_degree(degree) + 1


def get_house_degree(degree: float) -> float:
    """Return degree completed inside the placeholder 30-degree house span."""

    normalized_degree = normalize_longitude(_validate_degree(degree))
    house_index = get_house_index_from_degree(normalized_degree)
    house_degree = round(
        normalized_degree - (house_index * HOUSE_SPAN_DEGREES),
        DEGREE_PRECISION,
    )
    if house_degree < 0:
        return 0.0
    return house_degree


def _validate_degree(degree: float) -> float:
    """Validate a degree value before placeholder house lookup."""

    if isinstance(degree, bool) or not isinstance(degree, Real):
        raise TypeError("degree must be a real number")

    degree_float = float(degree)
    if not math.isfinite(degree_float):
        raise ValueError("degree must be finite")

    return degree_float
