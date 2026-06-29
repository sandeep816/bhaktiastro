"""Basic Panchang assembly from deterministic astronomy and astrology modules."""

from __future__ import annotations

from datetime import date
from typing import Any, TypedDict

from backend.app.astronomy import ayanamsa, julian, planet_positions, rise_set
from backend.app.astrology import karana, nakshatra, tithi, vara, yoga


class BasicPanchangResult(TypedDict):
    """Structured basic Panchang output."""

    julian_day: dict[str, Any]
    ayanamsa: dict[str, Any]
    sun: dict[str, Any]
    moon: dict[str, Any]
    tithi: dict[str, Any]
    nakshatra: dict[str, Any]
    yoga: dict[str, Any]
    karana: dict[str, Any]
    vara: dict[str, Any]
    sunrise: dict[str, Any]
    sunset: dict[str, Any]
    moonrise: dict[str, Any]
    moonset: dict[str, Any]


def calculate_basic_panchang(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_offset: float,
    latitude: float,
    longitude: float,
) -> BasicPanchangResult:
    """Calculate the basic deterministic Panchang for a local date and time.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        hour: Local hour.
        minute: Local minute.
        second: Local second.
        timezone_offset: Local UTC offset in decimal hours.
        latitude: Geographic latitude in degrees.
        longitude: Geographic longitude in degrees.

    Returns:
        A structured dictionary with Julian Day, ayanamsa, Sun, Moon,
        Tithi, Nakshatra, Yoga, Karana, Vara, sunrise, sunset, moonrise,
        and moonset sections.

    Raises:
        ValueError: If the local date components are invalid.
        RuntimeError: If required Sun or Moon position data is missing.
    """

    local_date = _build_local_date(year, month, day)
    julian_day_result = julian.calculate_julian_day(
        year,
        month,
        day,
        hour,
        minute,
        second,
        timezone_offset,
    )
    ayanamsa_value = ayanamsa.get_ayanamsa(julian_day_result.julian_day_ut)
    positions = planet_positions.get_planet_positions(
        julian_day_result.julian_day_ut,
        ayanamsa_value,
    )
    sun = _find_planet_position(positions, "sun")
    moon = _find_planet_position(positions, "moon")
    sun_sidereal_longitude = _get_sidereal_longitude(sun, "sun")
    moon_sidereal_longitude = _get_sidereal_longitude(moon, "moon")

    return {
        "julian_day": {
            "utc_datetime": julian_day_result.utc_datetime.isoformat(),
            "julian_day_ut": julian_day_result.julian_day_ut,
        },
        "ayanamsa": {
            "value": ayanamsa_value,
        },
        "sun": sun,
        "moon": moon,
        "tithi": tithi.get_tithi_with_boundary(
            year,
            month,
            day,
            hour,
            minute,
            second,
            timezone_offset,
        ),
        "nakshatra": nakshatra.get_nakshatra_with_boundary(
            year,
            month,
            day,
            hour,
            minute,
            second,
            timezone_offset,
        ),
        "yoga": yoga.get_panchang_yoga_with_boundary(
            year,
            month,
            day,
            hour,
            minute,
            second,
            timezone_offset,
        ),
        "karana": karana.get_karana(sun_sidereal_longitude, moon_sidereal_longitude),
        "vara": vara.get_vara(local_date),
        "sunrise": rise_set.get_sunrise(
            year,
            month,
            day,
            latitude,
            longitude,
            timezone_offset,
        ),
        "sunset": rise_set.get_sunset(
            year,
            month,
            day,
            latitude,
            longitude,
            timezone_offset,
        ),
        "moonrise": rise_set.get_moonrise(
            year,
            month,
            day,
            latitude,
            longitude,
            timezone_offset,
        ),
        "moonset": rise_set.get_moonset(
            year,
            month,
            day,
            latitude,
            longitude,
            timezone_offset,
        ),
    }


def _build_local_date(year: int, month: int, day: int) -> date:
    """Build a local civil date from date components."""

    try:
        return date(year, month, day)
    except ValueError as exc:
        raise ValueError("Invalid local date components") from exc


def _find_planet_position(
    positions: list[planet_positions.PlanetPosition],
    planet_name: str,
) -> dict[str, Any]:
    """Return a required planet position from the planet engine output."""

    for position in positions:
        if position.get("planet") == planet_name:
            return dict(position)

    raise RuntimeError(f"Planet positions did not include required planet: {planet_name}")


def _get_sidereal_longitude(position: dict[str, Any], planet_name: str) -> float:
    """Extract a sidereal longitude from a planet position dictionary."""

    try:
        return float(position["sidereal_longitude"])
    except KeyError as exc:
        raise RuntimeError(
            f"Planet position for {planet_name} is missing sidereal_longitude"
        ) from exc
