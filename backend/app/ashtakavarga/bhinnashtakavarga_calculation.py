"""Bhinnashtakavarga calculation foundation."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any, TypedDict

from backend.app.ashtakavarga.bhinnashtakavarga import (
    BAV_SOURCES,
    get_contributing_houses,
)
from backend.app.ashtakavarga.constants import (
    ASHTAKAVARGA_BINDU_VALUE,
    ASHTAKAVARGA_HOUSES,
    ASHTAKAVARGA_REKHA_VALUE,
    is_ashtakavarga_planet,
    normalize_ashtakavarga_house,
)


class BavSourceContribution(TypedDict):
    """JSON-safe contribution details from one source."""

    source: str
    source_house: int
    contributing_offsets: list[int]
    contributed_houses: list[int]
    bindus: int


class BhinnashtakavargaResult(TypedDict):
    """JSON-safe Bhinnashtakavarga result for one target planet."""

    target_planet: str
    houses: dict[int, int]
    total_bindus: int
    source_contributions: dict[str, BavSourceContribution]
    metadata: dict[str, object]


def calculate_bhinnashtakavarga(
    target_planet: str,
    chart_data: dict[str, Any],
) -> BhinnashtakavargaResult:
    """Calculate foundation-level Bhinnashtakavarga bindus for one planet."""

    target_key = _normalize_text(target_planet)
    houses = _create_empty_houses()
    source_contributions: dict[str, BavSourceContribution] = {}
    missing_sources: list[str] = []
    supported_target = is_ashtakavarga_planet(target_key)

    if not supported_target:
        return _create_result(
            target_key,
            houses,
            source_contributions,
            missing_sources,
            supported_target=False,
            chart_data_available=isinstance(chart_data, Mapping),
        )

    source_houses = _get_source_houses(chart_data)
    for source in BAV_SOURCES:
        source_house = source_houses.get(source)
        if source_house is None:
            missing_sources.append(source)
            continue

        contributing_offsets = get_contributing_houses(target_key, source)
        contributed_houses = [
            normalize_ashtakavarga_house(source_house + offset - 1)
            for offset in contributing_offsets
        ]
        for house_number in contributed_houses:
            houses[house_number] += ASHTAKAVARGA_BINDU_VALUE

        source_contributions[source] = {
            "source": source,
            "source_house": source_house,
            "contributing_offsets": contributing_offsets,
            "contributed_houses": contributed_houses,
            "bindus": len(contributed_houses),
        }

    return _create_result(
        target_key,
        houses,
        source_contributions,
        missing_sources,
        supported_target=True,
        chart_data_available=isinstance(chart_data, Mapping),
    )


def _create_result(
    target_planet: str,
    houses: dict[int, int],
    source_contributions: dict[str, BavSourceContribution],
    missing_sources: list[str],
    *,
    supported_target: bool,
    chart_data_available: bool,
) -> BhinnashtakavargaResult:
    """Create the public JSON-safe result shape."""

    return {
        "target_planet": target_planet,
        "houses": dict(houses),
        "total_bindus": sum(houses.values()),
        "source_contributions": {
            source: {
                "source": contribution["source"],
                "source_house": contribution["source_house"],
                "contributing_offsets": list(contribution["contributing_offsets"]),
                "contributed_houses": list(contribution["contributed_houses"]),
                "bindus": contribution["bindus"],
            }
            for source, contribution in source_contributions.items()
        },
        "metadata": {
            "calculation_status": "calculated" if supported_target else "unsupported",
            "formula_status": "foundation",
            "supported_target_planet": supported_target,
            "chart_data_available": chart_data_available,
            "missing_sources": list(missing_sources),
        },
    }


def _create_empty_houses() -> dict[int, int]:
    """Return a zeroed house row for all 12 houses."""

    return {house_number: ASHTAKAVARGA_REKHA_VALUE for house_number in ASHTAKAVARGA_HOUSES}


def _get_source_houses(chart_data: object) -> dict[str, int]:
    """Extract supported source house placements from Kundali-style chart data."""

    if not isinstance(chart_data, Mapping):
        return {}

    source_houses = _get_planet_source_houses(chart_data)
    lagna_house = _get_lagna_house(chart_data)
    if lagna_house is not None:
        source_houses["lagna"] = lagna_house

    return source_houses


def _get_planet_source_houses(chart_data: Mapping[str, Any]) -> dict[str, int]:
    """Extract supported planet house placements from chart planet entries."""

    planets = chart_data.get("planets")
    if not isinstance(planets, list):
        return {}

    source_houses: dict[str, int] = {}
    for planet_data in planets:
        if not isinstance(planet_data, Mapping):
            continue

        planet = _normalize_text(planet_data.get("planet"))
        if not is_ashtakavarga_planet(planet):
            continue

        house_number = _get_house_number(planet_data)
        if house_number is not None:
            source_houses[planet] = house_number

    return source_houses


def _get_lagna_house(chart_data: Mapping[str, Any]) -> int | None:
    """Return Lagna house from chart metadata, defaulting to house 1 when present."""

    lagna = chart_data.get("lagna")
    if not isinstance(lagna, Mapping):
        return None

    house_number = _get_house_number(lagna)
    if house_number is not None:
        return house_number

    return 1


def _get_house_number(data: Mapping[str, Any]) -> int | None:
    """Return normalized house number from mapping metadata."""

    house_number = data.get("house_number")
    if isinstance(house_number, bool) or not isinstance(house_number, Integral):
        return None

    return normalize_ashtakavarga_house(int(house_number))


def _normalize_text(value: object) -> str:
    """Normalize text output without validating astrology metadata."""

    return str(value or "").strip().casefold()
