"""Bhinnashtakavarga rule table foundation."""

from __future__ import annotations

from typing import Literal, TypedDict

from backend.app.ashtakavarga.constants import (
    ASHTAKAVARGA_HOUSES,
    ASHTAKAVARGA_PLANETS,
    AshtakavargaPlanet,
)

BAV_LAGNA_SOURCE = "lagna"
BAV_SOURCES: tuple[str, ...] = (*ASHTAKAVARGA_PLANETS, BAV_LAGNA_SOURCE)

BavSource = Literal[
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
    "lagna",
]

_BAV_SOURCE_SET = frozenset(BAV_SOURCES)
_BAV_HOUSE_SET = frozenset(ASHTAKAVARGA_HOUSES)


class BavRule(TypedDict):
    """JSON-safe Bhinnashtakavarga rule row for one target planet."""

    planet: str
    sources: dict[str, list[int]]
    metadata: dict[str, str]


BAV_RULES: dict[AshtakavargaPlanet, dict[BavSource, list[int]]] = {
    "sun": {
        "sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "moon": [3, 6, 10, 11],
        "mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "mercury": [3, 5, 6, 9, 10, 11, 12],
        "jupiter": [5, 6, 9, 11],
        "venus": [6, 7, 12],
        "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "lagna": [3, 4, 6, 10, 11, 12],
    },
    "moon": {
        "sun": [3, 6, 7, 8, 10, 11],
        "moon": [1, 3, 6, 7, 10, 11],
        "mars": [2, 3, 5, 6, 9, 10, 11],
        "mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "jupiter": [1, 4, 7, 8, 10, 11, 12],
        "venus": [3, 4, 5, 7, 9, 10, 11],
        "saturn": [3, 5, 6, 11],
        "lagna": [3, 6, 10, 11],
    },
    "mars": {
        "sun": [3, 5, 6, 10, 11],
        "moon": [3, 6, 11],
        "mars": [1, 2, 4, 7, 8, 10, 11],
        "mercury": [3, 5, 6, 11],
        "jupiter": [6, 10, 11, 12],
        "venus": [6, 8, 11, 12],
        "saturn": [1, 4, 7, 8, 9, 10, 11],
        "lagna": [1, 3, 6, 10, 11],
    },
    "mercury": {
        "sun": [5, 6, 9, 11, 12],
        "moon": [2, 4, 6, 8, 10, 11],
        "mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "jupiter": [6, 8, 11, 12],
        "venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "jupiter": {
        "sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "moon": [2, 5, 7, 9, 11],
        "mars": [1, 2, 4, 7, 8, 10, 11],
        "mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "venus": [2, 5, 6, 9, 10, 11],
        "saturn": [3, 5, 6, 12],
        "lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "venus": {
        "sun": [8, 11, 12],
        "moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "mars": [3, 5, 6, 9, 11, 12],
        "mercury": [3, 5, 6, 9, 11],
        "jupiter": [5, 8, 9, 10, 11],
        "venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "saturn": [3, 4, 5, 8, 9, 10, 11],
        "lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "saturn": {
        "sun": [1, 2, 4, 7, 8, 10, 11],
        "moon": [3, 6, 11],
        "mars": [3, 5, 6, 10, 11, 12],
        "mercury": [6, 8, 9, 10, 11, 12],
        "jupiter": [5, 6, 11, 12],
        "venus": [6, 11, 12],
        "saturn": [3, 5, 6, 11],
        "lagna": [1, 3, 4, 6, 10, 11],
    },
}


def get_bav_rule(planet: str) -> BavRule:
    """Return a JSON-safe Bhinnashtakavarga rule row for a target planet."""

    planet_key = _normalize_text(planet)
    rule = BAV_RULES.get(planet_key)  # type: ignore[arg-type]
    if rule is None:
        return _create_rule_result(planet_key, {})

    return _create_rule_result(planet_key, rule)


def get_contributing_houses(target_planet: str, source: str) -> list[int]:
    """Return contributing 1-based house offsets for a target/source pair."""

    planet_key = _normalize_text(target_planet)
    source_key = _normalize_text(source)
    if source_key not in _BAV_SOURCE_SET:
        return []

    rule = BAV_RULES.get(planet_key)  # type: ignore[arg-type]
    if rule is None:
        return []

    return list(rule[source_key])  # type: ignore[index]


def is_valid_bav_source(source: str) -> bool:
    """Return whether a source is supported in BAV rule tables."""

    return _normalize_text(source) in _BAV_SOURCE_SET


def _create_rule_result(
    planet: str,
    sources: dict[BavSource, list[int]],
) -> BavRule:
    """Create a JSON-safe rule-table result."""

    copied_sources = {
        source: list(houses)
        for source, houses in sources.items()
        if source in _BAV_SOURCE_SET and _houses_are_valid(houses)
    }
    return {
        "planet": planet,
        "sources": copied_sources,
        "metadata": {
            "calculation_status": "rule_table",
            "rule_status": "foundation",
        },
    }


def _houses_are_valid(houses: list[int]) -> bool:
    """Return whether all house offsets are valid Ashtakavarga houses."""

    return all(house in _BAV_HOUSE_SET for house in houses)


def _normalize_text(value: object) -> str:
    """Normalize text output without validating astrology metadata."""

    return str(value or "").strip().casefold()
