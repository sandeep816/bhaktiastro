"""Birth Dasha balance helpers."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import TypedDict

from backend.app.constants.dasha import (
    get_dasha_duration,
    get_nakshatra_dasha_lord,
)
from backend.app.constants.nakshatra import (
    FULL_CIRCLE_DEGREES,
    NAKSHATRA_SPAN_DEGREES,
)

DEGREE_PRECISION = 6
RATIO_PRECISION = 12
YEAR_PRECISION = 6
BOUNDARY_EPSILON = 0.000000001


class BirthDashaBalance(TypedDict):
    """JSON-safe birth Dasha balance output."""

    nakshatra_index: int
    dasha_lord: str
    full_dasha_years: int
    nakshatra_elapsed_degrees: float
    nakshatra_remaining_degrees: float
    balance_ratio: float
    balance_years: float


def calculate_birth_dasha_balance(
    nakshatra_index: int,
    moon_longitude: float,
) -> BirthDashaBalance:
    """Calculate remaining Vimshottari Mahadasha balance at birth.

    Args:
        nakshatra_index: Zero-based birth Nakshatra index.
        moon_longitude: Moon sidereal longitude in degrees. Values outside the
            0 <= longitude < 360 range are normalized before calculation.

    Returns:
        BirthDashaBalance containing the starting Dasha lord and remaining
        Mahadasha balance as a JSON-safe dictionary.

    Raises:
        TypeError: If inputs are not numeric values of the expected kind.
        ValueError: If the Nakshatra index is invalid, the longitude is not
            finite, or the normalized longitude does not fall within the
            supplied Nakshatra.
    """

    normalized_index = _validate_nakshatra_index(nakshatra_index)
    normalized_longitude = _normalize_longitude(moon_longitude)
    nakshatra_start = normalized_index * NAKSHATRA_SPAN_DEGREES
    elapsed_degrees = normalized_longitude - nakshatra_start
    if not _longitude_matches_nakshatra(elapsed_degrees):
        raise ValueError("moon_longitude does not fall within nakshatra_index")

    elapsed_degrees = min(max(elapsed_degrees, 0.0), NAKSHATRA_SPAN_DEGREES)
    remaining_degrees = max(NAKSHATRA_SPAN_DEGREES - elapsed_degrees, 0.0)
    balance_ratio = remaining_degrees / NAKSHATRA_SPAN_DEGREES

    dasha_lord = get_nakshatra_dasha_lord(normalized_index)
    full_dasha_years = get_dasha_duration(dasha_lord)
    balance_years = full_dasha_years * balance_ratio

    return {
        "nakshatra_index": normalized_index,
        "dasha_lord": dasha_lord,
        "full_dasha_years": full_dasha_years,
        "nakshatra_elapsed_degrees": round(elapsed_degrees, DEGREE_PRECISION),
        "nakshatra_remaining_degrees": round(
            remaining_degrees,
            DEGREE_PRECISION,
        ),
        "balance_ratio": round(balance_ratio, RATIO_PRECISION),
        "balance_years": round(balance_years, YEAR_PRECISION),
    }


def _validate_nakshatra_index(nakshatra_index: int) -> int:
    """Validate and return a zero-based Nakshatra index."""

    if isinstance(nakshatra_index, bool) or not isinstance(
        nakshatra_index,
        Integral,
    ):
        raise TypeError("nakshatra_index must be an integer")

    normalized_index = int(nakshatra_index)
    get_nakshatra_dasha_lord(normalized_index)
    return normalized_index


def _normalize_longitude(longitude: float) -> float:
    """Normalize Moon longitude into the 0 <= longitude < 360 range."""

    if isinstance(longitude, bool) or not isinstance(longitude, Real):
        raise TypeError("moon_longitude must be a real number")

    longitude_float = float(longitude)
    if not math.isfinite(longitude_float):
        raise ValueError("moon_longitude must be finite")

    normalized = longitude_float % FULL_CIRCLE_DEGREES
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized


def _longitude_matches_nakshatra(elapsed_degrees: float) -> bool:
    """Return whether elapsed degrees are inside the supplied Nakshatra."""

    return (
        -BOUNDARY_EPSILON
        <= elapsed_degrees
        < NAKSHATRA_SPAN_DEGREES - BOUNDARY_EPSILON
    )
