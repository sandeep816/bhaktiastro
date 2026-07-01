"""Reusable combustion helpers for Kundali foundations."""

from __future__ import annotations

import math
from numbers import Real
from typing import Literal, TypedDict

CombustionStatus = Literal["combust", "not_combust", "unsupported"]

COMBUSTION_ORBS: dict[str, float] = {
    "moon": 12.0,
    "mars": 17.0,
    "mercury": 14.0,
    "jupiter": 11.0,
    "venus": 10.0,
    "saturn": 15.0,
}


class PlanetCombustionMetadata(TypedDict):
    """Combustion metadata for chart enrichment."""

    status: CombustionStatus
    angular_distance: float
    orb: float


def angular_distance(longitude_a: float, longitude_b: float) -> float:
    """Return shortest angular distance between two longitudes, from 0 to 180."""

    first = _normalize_longitude(longitude_a)
    second = _normalize_longitude(longitude_b)
    distance = abs(first - second)
    return min(distance, 360.0 - distance)


def is_combust(
    planet: str,
    planet_longitude: float,
    sun_longitude: float,
) -> bool:
    """Return whether a supported planet is within its combustion orb."""

    return (
        get_combustion_status(planet, planet_longitude, sun_longitude)
        == "combust"
    )


def get_combustion_status(
    planet: str,
    planet_longitude: float,
    sun_longitude: float,
) -> CombustionStatus:
    """Return combustion status for a planet relative to the Sun."""

    planet_key = _normalize_planet(planet)
    if planet_key == "sun":
        return "not_combust"

    orb = COMBUSTION_ORBS.get(planet_key)
    if orb is None:
        return "unsupported"

    if angular_distance(planet_longitude, sun_longitude) <= orb:
        return "combust"

    return "not_combust"


def get_combustion_metadata(
    planet: str,
    planet_longitude: float,
    sun_longitude: float,
) -> PlanetCombustionMetadata:
    """Return combustion status, distance from Sun, and configured orb."""

    planet_key = _normalize_planet(planet)
    if planet_key not in COMBUSTION_ORBS:
        raise ValueError(f"Unsupported planet combustion mapping: {planet}")

    return {
        "status": get_combustion_status(planet_key, planet_longitude, sun_longitude),
        "angular_distance": angular_distance(planet_longitude, sun_longitude),
        "orb": COMBUSTION_ORBS[planet_key],
    }


def supports_combustion(planet: str) -> bool:
    """Return whether the project has combustion orb mapping for the planet."""

    return _normalize_planet(planet) in COMBUSTION_ORBS


def _normalize_planet(planet: str) -> str:
    """Return the normalized project planet key, or an unsupported sentinel."""

    if not isinstance(planet, str):
        return ""

    return planet.strip().casefold()


def _normalize_longitude(longitude: float) -> float:
    """Validate and normalize a longitude into the [0, 360) range."""

    if isinstance(longitude, bool) or not isinstance(longitude, Real):
        raise TypeError("longitude must be a real number")

    longitude_float = float(longitude)
    if not math.isfinite(longitude_float):
        raise ValueError("longitude must be finite")

    return longitude_float % 360.0
