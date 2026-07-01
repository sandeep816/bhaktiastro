"""Foundation detector for Panch Mahapurusha Yogas."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any

from backend.app.kundali import bhava, dignity, graha_lordship, yoga_framework

KENDRA_HOUSES = {1, 4, 7, 10}
PANCH_MAHAPURUSHA_YOGAS = {
    "mars": "Ruchaka Yoga",
    "mercury": "Bhadra Yoga",
    "jupiter": "Hamsa Yoga",
    "venus": "Malavya Yoga",
    "saturn": "Shasha Yoga",
}


def detect_panch_mahapurusha_yogas(chart_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect foundational Panch Mahapurusha Yogas from chart metadata."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    planets = chart_data.get("planets")
    if not isinstance(planets, list):
        return [
            _create_missing_result(
                planet,
                "Planet placement metadata is missing.",
            )
            for planet in PANCH_MAHAPURUSHA_YOGAS
        ]

    planet_lookup = _get_supported_planets(planets)
    return [
        _detect_planet_yoga(planet, planet_lookup.get(planet))
        for planet in PANCH_MAHAPURUSHA_YOGAS
    ]


def _detect_planet_yoga(
    planet: str,
    planet_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Detect one Panch Mahapurusha Yoga for a supported planet."""

    if planet_data is None:
        return _create_missing_result(
            planet,
            "Planet placement metadata is missing.",
        )

    house_number = _get_house_number(planet_data)
    if house_number is None:
        return _create_missing_result(
            planet,
            "Planet house metadata is missing.",
        )

    rashi = planet_data.get("rashi")
    if not isinstance(rashi, Mapping):
        return _create_missing_result(
            planet,
            "Planet Rashi metadata is missing.",
        )

    if house_number not in KENDRA_HOUSES:
        return yoga_framework.create_yoga_result(
            yoga_name=PANCH_MAHAPURUSHA_YOGAS[planet],
            is_present=False,
            involved_planets=[planet],
            involved_houses=[house_number],
            reason="Planet is not placed in a Kendra house.",
        )

    if _is_own_or_exalted_sign(planet, rashi):
        return yoga_framework.create_yoga_result(
            yoga_name=PANCH_MAHAPURUSHA_YOGAS[planet],
            is_present=True,
            involved_planets=[planet],
            involved_houses=[house_number],
            reason="Planet is in own or exaltation sign and placed in a Kendra house.",
        )

    return yoga_framework.create_yoga_result(
        yoga_name=PANCH_MAHAPURUSHA_YOGAS[planet],
        is_present=False,
        involved_planets=[planet],
        involved_houses=[house_number],
        reason="Planet is not in own or exaltation sign.",
    )


def _get_supported_planets(
    planets: list[Any],
) -> dict[str, Mapping[str, Any]]:
    """Return chart planet metadata keyed by supported planet name."""

    planet_lookup: dict[str, Mapping[str, Any]] = {}
    for planet_data in planets:
        if not isinstance(planet_data, Mapping):
            continue

        planet_name = planet_data.get("planet")
        if not isinstance(planet_name, str):
            continue

        planet_key = planet_name.strip().casefold()
        if planet_key in PANCH_MAHAPURUSHA_YOGAS:
            planet_lookup[planet_key] = planet_data

    return planet_lookup


def _get_house_number(planet_data: Mapping[str, Any]) -> int | None:
    """Return normalized house number from planet metadata."""

    house_number = planet_data.get("house_number")
    if isinstance(house_number, bool) or not isinstance(house_number, Integral):
        return None

    return bhava.normalize_house_number(int(house_number))


def _is_own_or_exalted_sign(planet: str, rashi: Mapping[str, Any]) -> bool:
    """Return whether a planet is in own or exaltation sign."""

    try:
        return (
            graha_lordship.get_rashi_lord(rashi).casefold() == planet
            or dignity.get_planet_dignity(planet, rashi) == "exalted"
        )
    except (TypeError, ValueError):
        return False


def _create_missing_result(planet: str, reason: str) -> dict[str, Any]:
    """Create a not-present result for missing required metadata."""

    return yoga_framework.create_yoga_result(
        yoga_name=PANCH_MAHAPURUSHA_YOGAS[planet],
        is_present=False,
        involved_planets=[planet],
        reason=reason,
    )


yoga_framework.register_yoga_detector(
    "panch_mahapurusha_yogas",
    detect_panch_mahapurusha_yogas,
)
