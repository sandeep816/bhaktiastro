"""Foundation detector for Raja Yoga."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any, Optional

from backend.app.kundali import bhava, yoga_framework

YOGA_NAME = "Raja Yoga"
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
LORD_KEYS = ("lord", "house_lord", "lord_planet")


def detect_raja_yoga(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Detect foundational Raja Yoga from house lord and placement metadata."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    house_lords = _get_house_lords(chart_data)
    if not house_lords:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            reason="House lord metadata is missing.",
        )

    planet_houses = _get_planet_houses(chart_data)
    if not planet_houses:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            reason="Planet house placement metadata is missing.",
        )

    for kendra_house in sorted(KENDRA_HOUSES):
        kendra_lord = house_lords.get(kendra_house)
        if kendra_lord is None:
            continue

        kendra_lord_house = planet_houses.get(kendra_lord)
        if kendra_lord_house is None:
            continue

        for trikona_house in sorted(TRIKONA_HOUSES):
            trikona_lord = house_lords.get(trikona_house)
            if trikona_lord is None:
                continue

            trikona_lord_house = planet_houses.get(trikona_lord)
            if trikona_lord_house is None:
                continue

            if kendra_lord_house == trikona_lord_house:
                return yoga_framework.create_yoga_result(
                    yoga_name=YOGA_NAME,
                    is_present=True,
                    involved_planets=[kendra_lord, trikona_lord],
                    involved_houses=[
                        kendra_house,
                        trikona_house,
                        kendra_lord_house,
                    ],
                    reason="Kendra lord and Trikona lord are in the same house.",
                )

    return yoga_framework.create_yoga_result(
        yoga_name=YOGA_NAME,
        is_present=False,
        reason="No Kendra lord and Trikona lord share the same house.",
    )


def _get_house_lords(chart_data: Mapping[str, Any]) -> dict[int, str]:
    """Return normalized house lords from available house metadata."""

    houses = chart_data.get("houses")
    if not isinstance(houses, list):
        return {}

    house_lords: dict[int, str] = {}
    for house in houses:
        if not isinstance(house, Mapping):
            continue

        house_number = _get_house_number(house)
        lord = _get_lord_name(house)
        if house_number is not None and lord is not None:
            house_lords[house_number] = lord

    return house_lords


def _get_planet_houses(chart_data: Mapping[str, Any]) -> dict[str, int]:
    """Return normalized planet placements from chart planet metadata."""

    planets = chart_data.get("planets")
    if not isinstance(planets, list):
        return {}

    planet_houses: dict[str, int] = {}
    for planet in planets:
        if not isinstance(planet, Mapping):
            continue

        planet_name = planet.get("planet")
        house_number = _get_house_number(planet)
        if isinstance(planet_name, str) and house_number is not None:
            planet_houses[planet_name.strip().casefold()] = house_number

    return planet_houses


def _get_house_number(data: Mapping[str, Any]) -> Optional[int]:
    """Return normalized house number from mapping metadata."""

    house_number = data.get("house_number")
    if isinstance(house_number, bool) or not isinstance(house_number, Integral):
        return None

    return bhava.normalize_house_number(int(house_number))


def _get_lord_name(house: Mapping[str, Any]) -> Optional[str]:
    """Return normalized house lord from supported metadata keys."""

    for key in LORD_KEYS:
        lord = house.get(key)
        if isinstance(lord, str) and lord.strip():
            return lord.strip().casefold()

    return None


yoga_framework.register_yoga_detector("raja_yoga", detect_raja_yoga)
