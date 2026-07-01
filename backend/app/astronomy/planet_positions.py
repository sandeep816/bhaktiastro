"""Planetary position calculation engine."""

from __future__ import annotations

from importlib import import_module
import math
from typing import Any, TypedDict

from backend.app.kundali import rashi as rashi_engine

KETU_OFFSET_DEGREES = 180.0
PLANETARY_RESULT_PRECISION = 6
RASHI_DEGREE_PRECISION = 4
SECONDS_PRECISION = 1

PLANET_ORDER = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
    "rahu",
)

class Dms(TypedDict):
    """Degrees, minutes, and seconds."""

    degrees: int
    minutes: int
    seconds: float


class PlanetPosition(TypedDict, total=False):
    """Calculated planetary position."""

    planet: str
    tropical_longitude: float
    sidereal_longitude: float
    rashi_index: int
    rashi_name_hi: str
    degree_in_rashi: float
    dms: Dms
    speed: float
    retrograde: bool


class InternalRashiData(TypedDict):
    """Internal Rashi data derived from the Kundali Rashi utility."""

    rashi: rashi_engine.RashiResult
    rashi_index: int
    rashi_degree: float


def _load_swisseph() -> Any:
    """Load the Swiss Ephemeris module.

    Returns:
        Imported `swisseph` module.

    Raises:
        RuntimeError: If `pyswisseph` is not installed.
    """
    try:
        return import_module("swisseph")
    except ImportError as exc:
        raise RuntimeError(
            "Swiss Ephemeris package 'pyswisseph' is required"
        ) from exc


def _normalize_deg(value: float) -> float:
    """Normalize a degree value into the `[0, 360)` range."""
    return rashi_engine.normalize_longitude(value)


def _deg_to_dms(value: float) -> Dms:
    """Convert decimal degrees to degrees, minutes, and seconds."""
    degrees = int(value)
    minute_float = (value - degrees) * 60
    minutes = int(minute_float)
    seconds = round((minute_float - minutes) * 60, SECONDS_PRECISION)

    return {
        "degrees": degrees,
        "minutes": minutes,
        "seconds": seconds,
    }


def _validate_numeric(value: float, name: str) -> float:
    """Validate a finite numeric value."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")

    return numeric_value


def _planet_ids(swe: Any) -> dict[str, int]:
    """Return Swiss Ephemeris IDs for calculated planets."""
    return {
        "sun": swe.SUN,
        "moon": swe.MOON,
        "mars": swe.MARS,
        "mercury": swe.MERCURY,
        "jupiter": swe.JUPITER,
        "venus": swe.VENUS,
        "saturn": swe.SATURN,
        "rahu": swe.MEAN_NODE,
    }


def _is_retrograde(planet: str, speed: float) -> bool:
    """Return retrograde status using project rules."""
    if planet in {"sun", "moon"}:
        return False

    if planet == "rahu":
        return True

    return speed < 0


def _position_from_longitude(
    planet: str,
    sidereal_longitude: float,
) -> PlanetPosition:
    """Build shared rashi fields from a sidereal longitude."""
    rashi_data = _rashi_data_from_longitude(sidereal_longitude)
    degree_in_rashi = rashi_data["rashi_degree"]

    return {
        "planet": planet,
        "sidereal_longitude": round(sidereal_longitude, PLANETARY_RESULT_PRECISION),
        "rashi_index": rashi_data["rashi_index"],
        "rashi_name_hi": rashi_data["rashi"]["hindi"],
        "degree_in_rashi": round(degree_in_rashi, RASHI_DEGREE_PRECISION),
        "dms": _deg_to_dms(degree_in_rashi),
    }


def _rashi_data_from_longitude(sidereal_longitude: float) -> InternalRashiData:
    """Return internal Rashi data without changing public planet fields."""

    rashi = rashi_engine.get_rashi(sidereal_longitude)
    return {
        "rashi": rashi,
        "rashi_index": rashi["index"] - 1,
        "rashi_degree": rashi_engine.get_rashi_degree(sidereal_longitude),
    }


def get_planet_positions(jd_ut: float, ayanamsa: float) -> list[PlanetPosition]:
    """Calculate sidereal planetary positions for Sun through Ketu.

    Args:
        jd_ut: Julian Day in Universal Time.
        ayanamsa: Ayanamsa value in degrees.

    Returns:
        List of nine planet position dictionaries. Ketu is calculated from
        Rahu + 180 degrees and does not call Swiss Ephemeris separately.

    Raises:
        TypeError: If `jd_ut` or `ayanamsa` is not numeric.
        ValueError: If `jd_ut` or `ayanamsa` is not finite.
        RuntimeError: If `pyswisseph` is not installed or calculation fails.
    """
    jd_ut_value = _validate_numeric(jd_ut, "jd_ut")
    ayanamsa_value = _validate_numeric(ayanamsa, "ayanamsa")
    swe = _load_swisseph()
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    planet_ids = _planet_ids(swe)

    results: list[PlanetPosition] = []
    for planet in PLANET_ORDER:
        try:
            data, _ = swe.calc_ut(jd_ut_value, planet_ids[planet], flags)
        except Exception as exc:
            raise RuntimeError(f"Swiss Ephemeris failed for planet: {planet}") from exc

        if len(data) < 4:
            raise RuntimeError(
                f"Swiss Ephemeris returned incomplete data for planet: {planet}"
            )

        tropical_longitude = float(data[0])
        speed = float(data[3])
        sidereal_longitude = _normalize_deg(tropical_longitude - ayanamsa_value)
        position = _position_from_longitude(planet, sidereal_longitude)
        position["tropical_longitude"] = round(
            tropical_longitude,
            PLANETARY_RESULT_PRECISION,
        )
        position["speed"] = round(speed, PLANETARY_RESULT_PRECISION)
        position["retrograde"] = _is_retrograde(planet, speed)
        results.append(position)

    rahu = next(position for position in results if position["planet"] == "rahu")
    ketu_longitude = _normalize_deg(
        float(rahu["sidereal_longitude"]) + KETU_OFFSET_DEGREES
    )
    ketu_position = _position_from_longitude("ketu", ketu_longitude)
    ketu_position["retrograde"] = True
    results.append(ketu_position)

    return results
