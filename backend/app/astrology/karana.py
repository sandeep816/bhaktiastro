"""Deterministic Karana lookup from sidereal Sun and Moon longitudes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
from numbers import Real
from typing import TypedDict

from backend.app.astronomy import ayanamsa, julian, planet_positions, search
from backend.app.constants.karana import (
    FIXED_KARANAS,
    REPEATING_KARANAS,
    Karana,
)

FULL_CIRCLE_DEGREES = 360.0
HALF_TITHI_COUNT = 60
KARANA_SPAN_DEGREES = FULL_CIRCLE_DEGREES / HALF_TITHI_COUNT
DEGREE_PRECISION = 6
UTC_SUFFIX = "Z"


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


class KaranaWithBoundaryResult(KaranaResult):
    """Typed output for a Karana lookup with boundary end time."""

    end_time_local: str
    end_time_utc: str


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


def get_karana_with_boundary(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_offset: float,
) -> KaranaWithBoundaryResult:
    """Return current Karana with its next boundary end time.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        hour: Local hour.
        minute: Local minute.
        second: Local second.
        timezone_offset: Local UTC offset in decimal hours.

    Returns:
        KaranaWithBoundaryResult containing current Karana details plus
        ``end_time_local`` and ``end_time_utc``.

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
    sun_longitude, moon_longitude = _get_sun_moon_sidereal_longitudes(
        julian_day_result.julian_day_ut
    )
    current_karana = get_karana(sun_longitude, moon_longitude)
    target_boundary = current_karana["end_angle"]

    end_datetime_utc = search.find_next_longitude_boundary(
        julian_day_result.utc_datetime,
        _calculate_karana_angle_at_utc,
        target_boundary,
    )
    end_datetime_local = end_datetime_utc.astimezone(
        timezone(timedelta(hours=float(timezone_offset)))
    )

    result: KaranaWithBoundaryResult = {
        **current_karana,
        "end_time_local": end_datetime_local.isoformat(timespec="seconds"),
        "end_time_utc": _format_utc_datetime(end_datetime_utc),
    }
    return result


def _calculate_karana_angle_at_utc(utc_datetime: datetime) -> float:
    """Calculate Moon-Sun sidereal angle for a UTC datetime."""

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
    sun_longitude, moon_longitude = _get_sun_moon_sidereal_longitudes(
        julian_day_result.julian_day_ut
    )
    return _normalize_longitude(moon_longitude - sun_longitude)


def _get_sun_moon_sidereal_longitudes(julian_day_ut: float) -> tuple[float, float]:
    """Return Sun and Moon sidereal longitudes for a Julian Day UT."""

    ayanamsa_value = ayanamsa.get_ayanamsa(julian_day_ut)
    positions = planet_positions.get_planet_positions(julian_day_ut, ayanamsa_value)
    sun = _find_planet_position(positions, "sun")
    moon = _find_planet_position(positions, "moon")
    return (
        _get_sidereal_longitude(sun, "sun"),
        _get_sidereal_longitude(moon, "moon"),
    )


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
        .replace("+00:00", UTC_SUFFIX)
    )


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
