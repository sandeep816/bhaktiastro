"""Reusable house-based Graha Drishti helpers."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any, TypedDict

from backend.app.kundali import bhava

STANDARD_ASPECTS: tuple[int, ...] = (7,)
SPECIAL_ASPECTS: dict[str, tuple[int, ...]] = {
    "mars": (4, 7, 8),
    "jupiter": (5, 7, 9),
    "saturn": (3, 7, 10),
}
SUPPORTED_PLANETS: tuple[str, ...] = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)


class PlanetAspects(TypedDict):
    """House-based aspect metadata for a supported planet."""

    planet: str
    house_number: int
    aspected_houses: list[int]


def normalize_house_number(house: int) -> int:
    """Normalize any integer house value into the `1..12` range."""

    return bhava.normalize_house_number(house)


def get_aspected_houses(planet: str, house_number: int) -> list[int]:
    """Return houses aspected by a supported planet from its placement house."""

    planet_key = _normalize_planet(planet)
    if planet_key is None:
        return []

    house = normalize_house_number(house_number)
    aspect_offsets = SPECIAL_ASPECTS.get(planet_key, STANDARD_ASPECTS)
    return [
        normalize_house_number(house + aspect_number - 1)
        for aspect_number in aspect_offsets
    ]


def get_planet_aspects(planet_data: Mapping[str, Any]) -> dict[str, Any]:
    """Return aspect metadata for planet-like chart data."""

    if not isinstance(planet_data, Mapping):
        raise TypeError("planet_data must be a mapping")

    planet = planet_data.get("planet")
    house_number = planet_data.get("house_number")
    if not isinstance(planet, str):
        raise ValueError("planet_data must include a planet key")
    if isinstance(house_number, bool) or not isinstance(house_number, Integral):
        raise ValueError("planet_data must include an integer house_number")

    planet_key = _normalize_planet(planet)
    if planet_key is None:
        return {
            "planet": planet.strip().casefold(),
            "house_number": normalize_house_number(int(house_number)),
            "aspected_houses": [],
        }

    return {
        "planet": planet_key,
        "house_number": normalize_house_number(int(house_number)),
        "aspected_houses": get_aspected_houses(planet_key, int(house_number)),
    }


def supports_drishti(planet: str) -> bool:
    """Return whether the project has Graha Drishti rules for the planet."""

    return _normalize_planet(planet) is not None


def _normalize_planet(planet: str) -> str | None:
    """Return the normalized project planet key if supported."""

    if not isinstance(planet, str):
        return None

    planet_key = planet.strip().casefold()
    if planet_key not in SUPPORTED_PLANETS:
        return None

    return planet_key
