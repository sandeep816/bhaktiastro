"""Foundation Ascendant/Lagna calculation helpers."""

from __future__ import annotations

from importlib import import_module
import math
from numbers import Real
from typing import Any, Optional, TypedDict

from backend.app.astronomy import ayanamsa, julian
from backend.app.kundali import rashi as rashi_engine

ASCENDANT_INDEX = 0
LONGITUDE_PRECISION = 6
MIN_LATITUDE_DEGREES = -90.0
MAX_LATITUDE_DEGREES = 90.0
MIN_LONGITUDE_DEGREES = -180.0
MAX_LONGITUDE_DEGREES = 180.0
DEFAULT_HOUSE_SYSTEM = b"P"


class LagnaResult(TypedDict):
    """Typed internal output for a Lagna foundation calculation."""

    ascendant_longitude: float
    sidereal_longitude: float
    tropical_longitude: float
    ayanamsa: float
    rashi: rashi_engine.RashiResult
    rashi_index: int
    rashi_degree: float


def calculate_lagna(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_offset: float,
    latitude: float,
    longitude: float,
    ayanamsa_mode: Optional[str] = None,
) -> LagnaResult:
    """Calculate a sidereal Ascendant/Lagna foundation result.

    This is intentionally limited to Ascendant longitude and Rashi metadata.
    It does not calculate full house systems or integrate into public APIs.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        hour: Local hour.
        minute: Local minute.
        second: Local second.
        timezone_offset: Local UTC offset in decimal hours.
        latitude: Geographic latitude in degrees, north positive.
        longitude: Geographic longitude in degrees, east positive.
        ayanamsa_mode: Optional configured ayanamsa mode.

    Returns:
        LagnaResult with normalized sidereal Ascendant longitude and Rashi data.

    Raises:
        TypeError: If latitude or longitude is not a real number.
        ValueError: If date/time, timezone, latitude, or longitude is invalid.
        RuntimeError: If Swiss Ephemeris is unavailable or fails.
    """

    latitude_value = _validate_coordinate(
        latitude,
        "latitude",
        MIN_LATITUDE_DEGREES,
        MAX_LATITUDE_DEGREES,
    )
    longitude_value = _validate_coordinate(
        longitude,
        "longitude",
        MIN_LONGITUDE_DEGREES,
        MAX_LONGITUDE_DEGREES,
    )
    julian_day = julian.calculate_julian_day(
        year,
        month,
        day,
        hour,
        minute,
        second,
        timezone_offset,
    )
    ayanamsa_value = ayanamsa.get_ayanamsa(
        julian_day.julian_day_ut,
        ayanamsa_mode,
    )
    tropical_longitude = _calculate_tropical_ascendant(
        julian_day.julian_day_ut,
        latitude_value,
        longitude_value,
    )
    sidereal_longitude = rashi_engine.normalize_longitude(
        tropical_longitude - ayanamsa_value
    )
    rashi = rashi_engine.get_rashi(sidereal_longitude)
    rashi_degree = rashi_engine.get_rashi_degree(sidereal_longitude)

    return {
        "ascendant_longitude": round(sidereal_longitude, LONGITUDE_PRECISION),
        "sidereal_longitude": round(sidereal_longitude, LONGITUDE_PRECISION),
        "tropical_longitude": round(tropical_longitude, LONGITUDE_PRECISION),
        "ayanamsa": round(ayanamsa_value, LONGITUDE_PRECISION),
        "rashi": rashi,
        "rashi_index": rashi["index"],
        "rashi_degree": rashi_degree,
    }


def _calculate_tropical_ascendant(
    jd_ut: float,
    latitude: float,
    longitude: float,
) -> float:
    """Calculate tropical Ascendant longitude using Swiss Ephemeris houses."""

    swe = _load_swisseph()
    try:
        _, ascmc = swe.houses_ex(
            jd_ut,
            latitude,
            longitude,
            DEFAULT_HOUSE_SYSTEM,
        )
    except Exception as exc:
        raise RuntimeError("Swiss Ephemeris failed to calculate Ascendant") from exc

    if len(ascmc) <= ASCENDANT_INDEX:
        raise RuntimeError("Swiss Ephemeris returned incomplete Ascendant data")

    ascendant = float(ascmc[ASCENDANT_INDEX])
    if not math.isfinite(ascendant):
        raise RuntimeError("Swiss Ephemeris returned non-finite Ascendant data")

    return rashi_engine.normalize_longitude(ascendant)


def _load_swisseph() -> Any:
    """Load the Swiss Ephemeris module."""

    try:
        return import_module("swisseph")
    except ImportError as exc:
        raise RuntimeError(
            "Swiss Ephemeris package 'pyswisseph' is required"
        ) from exc


def _validate_coordinate(
    value: float,
    name: str,
    minimum: float,
    maximum: float,
) -> float:
    """Validate a finite geographic coordinate."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")

    if not minimum <= numeric_value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum} degrees")

    return numeric_value
