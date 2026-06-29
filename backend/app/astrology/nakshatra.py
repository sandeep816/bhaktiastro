"""Deterministic Nakshatra lookup from sidereal longitude."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
from numbers import Real
from typing import TypedDict

from backend.app.astronomy import ayanamsa, julian, planet_positions, search
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


class NakshatraWithBoundaryResult(NakshatraResult):
    """Typed output for a Nakshatra lookup with boundary end time."""

    current_degree: float
    degrees_remaining: float
    end_time_local: str
    end_time_utc: str


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


def get_nakshatra_with_boundary(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_offset: float,
) -> NakshatraWithBoundaryResult:
    """Return current Nakshatra with its next boundary end time.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        hour: Local hour.
        minute: Local minute.
        second: Local second.
        timezone_offset: Local UTC offset in decimal hours.

    Returns:
        NakshatraWithBoundaryResult containing current Nakshatra and Pada
        details plus the next boundary end time.

    Raises:
        TypeError: If timezone offset or ephemeris inputs are invalid.
        ValueError: If date/time components are invalid.
        RuntimeError: If Swiss Ephemeris or boundary search fails.
    """

    julian_day_result = julian.calculate_julian_day(
        year,
        month,
        day,
        hour,
        minute,
        second,
        timezone_offset,
    )
    moon_longitude = _get_moon_sidereal_longitude(julian_day_result.julian_day_ut)
    current_nakshatra = get_nakshatra(moon_longitude)
    current_degree = _normalize_longitude(moon_longitude)
    target_boundary = current_nakshatra["end_degree"]
    degrees_remaining = round(
        (target_boundary - current_degree) % FULL_CIRCLE_DEGREES,
        BOUNDARY_PRECISION,
    )
    if degrees_remaining == 0.0:
        degrees_remaining = round(NAKSHATRA_SPAN_DEGREES, BOUNDARY_PRECISION)

    end_datetime_utc = search.find_next_longitude_boundary(
        julian_day_result.utc_datetime,
        _calculate_moon_longitude_at_utc,
        target_boundary,
    )
    end_datetime_local = end_datetime_utc.astimezone(
        timezone(timedelta(hours=float(timezone_offset)))
    )

    result: NakshatraWithBoundaryResult = {
        **current_nakshatra,
        "current_degree": current_degree,
        "degrees_remaining": degrees_remaining,
        "end_time_local": end_datetime_local.isoformat(timespec="seconds"),
        "end_time_utc": _format_utc_datetime(end_datetime_utc),
    }
    return result


def _calculate_moon_longitude_at_utc(utc_datetime: datetime) -> float:
    """Calculate Moon sidereal longitude for a UTC datetime."""

    normalized_datetime = utc_datetime.astimezone(timezone.utc).replace(microsecond=0)
    julian_day_result = julian.calculate_julian_day(
        normalized_datetime.year,
        normalized_datetime.month,
        normalized_datetime.day,
        normalized_datetime.hour,
        normalized_datetime.minute,
        normalized_datetime.second,
        0.0,
    )
    return _get_moon_sidereal_longitude(julian_day_result.julian_day_ut)


def _get_moon_sidereal_longitude(julian_day_ut: float) -> float:
    """Return Moon sidereal longitude for a Julian Day UT."""

    ayanamsa_value = ayanamsa.get_ayanamsa(julian_day_ut)
    positions = planet_positions.get_planet_positions(julian_day_ut, ayanamsa_value)
    moon = _find_planet_position(positions, "moon")
    return _get_sidereal_longitude(moon, "moon")


def _find_planet_position(
    positions: list[planet_positions.PlanetPosition],
    planet_name: str,
) -> planet_positions.PlanetPosition:
    """Return a required planet position from the planet engine output."""

    for position in positions:
        if position.get("planet") == planet_name:
            return position

    raise RuntimeError(f"Planet positions did not include required planet: {planet_name}")


def _get_sidereal_longitude(
    position: planet_positions.PlanetPosition,
    planet_name: str,
) -> float:
    """Extract a sidereal longitude from a planet position dictionary."""

    try:
        return float(position["sidereal_longitude"])
    except KeyError as exc:
        raise RuntimeError(
            f"Planet position for {planet_name} is missing sidereal_longitude"
        ) from exc


def _format_utc_datetime(utc_datetime: datetime) -> str:
    """Format a UTC datetime as an ISO-8601 string with Z suffix."""

    return (
        utc_datetime.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the 0 <= longitude < 360 range."""

    normalized = round(longitude % FULL_CIRCLE_DEGREES, BOUNDARY_PRECISION)
    if normalized == FULL_CIRCLE_DEGREES:
        return 0.0
    return normalized
