"""Foundation-level Dig Bala directional strength helper."""

from __future__ import annotations

from typing import Literal, TypedDict

from backend.app.kundali import bhava

DIG_BALA_COMPONENT = "dig_bala"
DIG_BALA_MAX_SCORE = 60

DigBalaStatus = Literal[
    "strongest_direction",
    "weakest_direction",
    "other_direction",
    "invalid_input",
]

DIG_BALA_STRONGEST_HOUSE_BY_PLANET: dict[str, int] = {
    "jupiter": 1,
    "mercury": 1,
    "moon": 4,
    "venus": 4,
    "saturn": 7,
    "sun": 10,
    "mars": 10,
}

DIG_BALA_SCORES: dict[DigBalaStatus, int | None] = {
    "strongest_direction": 60,
    "weakest_direction": 0,
    "other_direction": 30,
    "invalid_input": None,
}

DIG_BALA_REASONS: dict[DigBalaStatus, str] = {
    "strongest_direction": "Planet is in its strongest directional house.",
    "weakest_direction": "Planet is in the opposite directional house.",
    "other_direction": "Planet is in another supported house.",
    "invalid_input": "Planet or house is not supported for Dig Bala foundation.",
}


class DigBalaResult(TypedDict):
    """JSON-safe Dig Bala foundation result."""

    planet: str
    house_number: int | None
    component: str
    status: str
    score: int | None
    max_score: int
    reason: str


def calculate_dig_bala(planet: str, house_number: int) -> DigBalaResult:
    """Calculate foundation-level directional strength for a planet placement.

    This helper implements only the Sprint 7 placeholder scoring boundary and
    expects an already-derived one-based house number from Kundali placement
    helpers.
    """

    planet_key = _normalize_planet(planet)
    house_value = _get_valid_house_number(house_number)

    if planet_key not in DIG_BALA_STRONGEST_HOUSE_BY_PLANET or house_value is None:
        return _create_result(planet_key, house_value, "invalid_input")

    strongest_house = DIG_BALA_STRONGEST_HOUSE_BY_PLANET[planet_key]
    weakest_house = bhava.normalize_house_number(strongest_house + 6)

    if house_value == strongest_house:
        return _create_result(planet_key, house_value, "strongest_direction")

    if house_value == weakest_house:
        return _create_result(planet_key, house_value, "weakest_direction")

    return _create_result(planet_key, house_value, "other_direction")


def _create_result(
    planet: str,
    house_number: int | None,
    status: DigBalaStatus,
) -> DigBalaResult:
    """Create a JSON-safe Dig Bala result."""

    return {
        "planet": planet,
        "house_number": house_number,
        "component": DIG_BALA_COMPONENT,
        "status": status,
        "score": DIG_BALA_SCORES[status],
        "max_score": DIG_BALA_MAX_SCORE,
        "reason": DIG_BALA_REASONS[status],
    }


def _normalize_planet(planet: object) -> str:
    """Normalize planet output without validating astrology metadata."""

    return str(planet).strip().casefold()


def _get_valid_house_number(house_number: object) -> int | None:
    """Return a valid one-based house number, or None for unsafe input."""

    if isinstance(house_number, bool) or not isinstance(house_number, int):
        return None

    if house_number not in bhava.HOUSE_NUMBERS:
        return None

    return bhava.normalize_house_number(house_number)
