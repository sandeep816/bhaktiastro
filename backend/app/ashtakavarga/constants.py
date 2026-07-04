"""Ashtakavarga foundation constants and helpers."""

from __future__ import annotations

from typing import Literal, TypedDict

from backend.app.kundali import bhava

ASHTAKAVARGA_HOUSE_COUNT = bhava.HOUSE_COUNT
ASHTAKAVARGA_HOUSES = bhava.HOUSE_NUMBERS
ASHTAKAVARGA_BINDU_VALUE = 1
ASHTAKAVARGA_REKHA_VALUE = 0
ASHTAKAVARGA_STATUS_NOT_EVALUATED = "not_evaluated"

AshtakavargaPlanet = Literal[
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
]

ASHTAKAVARGA_PLANETS: tuple[AshtakavargaPlanet, ...] = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)

_ASHTAKAVARGA_PLANET_SET = frozenset(ASHTAKAVARGA_PLANETS)


class EmptyBinduRowMetadata(TypedDict):
    """JSON-safe metadata for a placeholder Ashtakavarga bindu row."""

    calculation_status: str
    formula_status: str
    supported_planet: bool
    house_count: int


class EmptyBinduRow(TypedDict):
    """JSON-safe placeholder bindu row for one planet."""

    planet: str
    houses: dict[int, int]
    total_bindus: int
    metadata: EmptyBinduRowMetadata


def get_ashtakavarga_planets() -> tuple[AshtakavargaPlanet, ...]:
    """Return supported Ashtakavarga planets in deterministic order."""

    return ASHTAKAVARGA_PLANETS


def is_ashtakavarga_planet(planet: str) -> bool:
    """Return whether a planet is supported for Ashtakavarga foundations."""

    return _normalize_planet(planet) in _ASHTAKAVARGA_PLANET_SET


def normalize_ashtakavarga_house(house_number: int) -> int:
    """Normalize a house number into the Ashtakavarga `1..12` range."""

    return bhava.normalize_house_number(house_number)


def create_empty_bindu_row(planet: str) -> EmptyBinduRow:
    """Create a JSON-safe placeholder bindu row without applying rules."""

    planet_key = _normalize_planet(planet)
    return {
        "planet": planet_key,
        "houses": {
            house_number: ASHTAKAVARGA_REKHA_VALUE
            for house_number in ASHTAKAVARGA_HOUSES
        },
        "total_bindus": 0,
        "metadata": {
            "calculation_status": "placeholder",
            "formula_status": ASHTAKAVARGA_STATUS_NOT_EVALUATED,
            "supported_planet": is_ashtakavarga_planet(planet_key),
            "house_count": ASHTAKAVARGA_HOUSE_COUNT,
        },
    }


def _normalize_planet(planet: object) -> str:
    """Normalize planet output without validating astrology metadata."""

    return str(planet).strip().casefold()
