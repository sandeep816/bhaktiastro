"""Foundation detector for Gajakesari Yoga."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any

from backend.app.kundali import bhava, yoga_framework

YOGA_NAME = "Gajakesari Yoga"
MOON_KEY = "moon"
JUPITER_KEY = "jupiter"
MOON_KENDRA_HOUSES = {1, 4, 7, 10}


def detect_gajakesari_yoga(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Detect foundational Gajakesari Yoga from chart house metadata."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    moon = _find_planet(chart_data, MOON_KEY)
    jupiter = _find_planet(chart_data, JUPITER_KEY)
    if moon is None or jupiter is None:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            involved_planets=[MOON_KEY, JUPITER_KEY],
            reason="Moon or Jupiter placement data is missing.",
        )

    moon_house = _get_house_number(moon)
    jupiter_house = _get_house_number(jupiter)
    if moon_house is None or jupiter_house is None:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            involved_planets=[MOON_KEY, JUPITER_KEY],
            reason="Moon or Jupiter house metadata is missing.",
        )

    relative_house = _relative_house_from_moon(moon_house, jupiter_house)
    is_present = relative_house in MOON_KENDRA_HOUSES
    reason = (
        "Jupiter is in a Kendra from Moon."
        if is_present
        else "Jupiter is not in a Kendra from Moon."
    )

    return yoga_framework.create_yoga_result(
        yoga_name=YOGA_NAME,
        is_present=is_present,
        involved_planets=[MOON_KEY, JUPITER_KEY],
        involved_houses=[moon_house, jupiter_house],
        reason=reason,
    )


def _find_planet(
    chart_data: Mapping[str, Any],
    planet_key: str,
) -> Mapping[str, Any] | None:
    """Return planet data by project planet key."""

    planets = chart_data.get("planets")
    if not isinstance(planets, list):
        return None

    for planet in planets:
        if not isinstance(planet, Mapping):
            continue
        name = planet.get("planet")
        if isinstance(name, str) and name.casefold() == planet_key:
            return planet

    return None


def _get_house_number(planet: Mapping[str, Any]) -> int | None:
    """Return normalized house number from planet data when present."""

    house_number = planet.get("house_number")
    if isinstance(house_number, bool) or not isinstance(house_number, Integral):
        return None

    return bhava.normalize_house_number(int(house_number))


def _relative_house_from_moon(moon_house: int, jupiter_house: int) -> int:
    """Return Jupiter's one-based relative house from Moon."""

    return ((jupiter_house - moon_house) % bhava.HOUSE_COUNT) + 1


yoga_framework.register_yoga_detector("gajakesari_yoga", detect_gajakesari_yoga)
