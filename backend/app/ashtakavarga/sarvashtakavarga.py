"""Sarvashtakavarga calculation foundation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypedDict

from backend.app.ashtakavarga.bhinnashtakavarga_calculation import (
    BhinnashtakavargaResult,
    calculate_bhinnashtakavarga,
)
from backend.app.ashtakavarga.constants import (
    ASHTAKAVARGA_HOUSES,
    ASHTAKAVARGA_PLANETS,
    ASHTAKAVARGA_REKHA_VALUE,
)


class SarvashtakavargaResult(TypedDict):
    """JSON-safe Sarvashtakavarga aggregate result."""

    houses: dict[int, int]
    total_bindus: int
    planet_totals: dict[str, int]
    bhinnashtakavarga: dict[str, BhinnashtakavargaResult]
    metadata: dict[str, object]


def calculate_sarvashtakavarga(chart_data: dict[str, Any]) -> SarvashtakavargaResult:
    """Calculate foundation-level Sarvashtakavarga from supported BAV rows."""

    houses = _create_empty_houses()
    planet_totals: dict[str, int] = {}
    bhinnashtakavarga: dict[str, BhinnashtakavargaResult] = {}
    missing_sources_by_planet: dict[str, list[str]] = {}

    for planet in ASHTAKAVARGA_PLANETS:
        bav_result = calculate_bhinnashtakavarga(planet, chart_data)
        bhinnashtakavarga[planet] = bav_result
        planet_totals[planet] = bav_result["total_bindus"]

        for house_number, bindus in bav_result["houses"].items():
            if house_number in houses:
                houses[house_number] += bindus

        missing_sources = bav_result["metadata"].get("missing_sources", [])
        if isinstance(missing_sources, list) and missing_sources:
            missing_sources_by_planet[planet] = list(missing_sources)

    return {
        "houses": houses,
        "total_bindus": sum(houses.values()),
        "planet_totals": planet_totals,
        "bhinnashtakavarga": bhinnashtakavarga,
        "metadata": {
            "calculation_status": "calculated",
            "formula_status": "foundation",
            "supported_planets": list(ASHTAKAVARGA_PLANETS),
            "planet_count": len(ASHTAKAVARGA_PLANETS),
            "chart_data_available": isinstance(chart_data, Mapping),
            "missing_sources_by_planet": missing_sources_by_planet,
        },
    }


def _create_empty_houses() -> dict[int, int]:
    """Return a zeroed Sarvashtakavarga house row."""

    return {house_number: ASHTAKAVARGA_REKHA_VALUE for house_number in ASHTAKAVARGA_HOUSES}
