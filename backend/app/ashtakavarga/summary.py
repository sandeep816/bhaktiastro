"""Ashtakavarga summary builder."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypedDict

from backend.app.ashtakavarga.bhinnashtakavarga_calculation import (
    BhinnashtakavargaResult,
)
from backend.app.ashtakavarga.sarvashtakavarga import (
    SarvashtakavargaResult,
    calculate_sarvashtakavarga,
)

ASHTAKAVARGA_SUMMARY_STATUS = "foundation"
ASHTAKAVARGA_RANKING_BASIS = "sarvashtakavarga.house_bindus"


class AshtakavargaHouseRankingEntry(TypedDict):
    """JSON-safe Ashtakavarga house ranking entry."""

    house_number: int
    bindus: int


class AshtakavargaSummary(TypedDict):
    """JSON-safe Ashtakavarga summary result."""

    sarvashtakavarga: SarvashtakavargaResult
    bhinnashtakavarga: dict[str, BhinnashtakavargaResult]
    strongest_house: AshtakavargaHouseRankingEntry | None
    weakest_house: AshtakavargaHouseRankingEntry | None
    house_ranking: list[AshtakavargaHouseRankingEntry]
    metadata: dict[str, object]


def build_ashtakavarga_summary(chart_data: dict[str, Any]) -> AshtakavargaSummary:
    """Build a foundation-level Ashtakavarga summary from chart data."""

    sarvashtakavarga = calculate_sarvashtakavarga(chart_data)
    bhinnashtakavarga = sarvashtakavarga["bhinnashtakavarga"]
    house_ranking = _build_house_ranking(sarvashtakavarga)

    return {
        "sarvashtakavarga": sarvashtakavarga,
        "bhinnashtakavarga": bhinnashtakavarga,
        "strongest_house": house_ranking[0] if house_ranking else None,
        "weakest_house": house_ranking[-1] if house_ranking else None,
        "house_ranking": house_ranking,
        "metadata": {
            "calculation_status": ASHTAKAVARGA_SUMMARY_STATUS,
            "ranking_basis": ASHTAKAVARGA_RANKING_BASIS,
            "house_count": len(house_ranking),
            "planet_count": len(bhinnashtakavarga),
            "chart_data_available": isinstance(chart_data, Mapping),
        },
    }


def _build_house_ranking(
    sarvashtakavarga: SarvashtakavargaResult,
) -> list[AshtakavargaHouseRankingEntry]:
    """Return houses sorted by bindus descending with house number as tie-breaker."""

    ranking = [
        {"house_number": house_number, "bindus": bindus}
        for house_number, bindus in sarvashtakavarga["houses"].items()
    ]
    return sorted(
        ranking,
        key=lambda entry: (-entry["bindus"], entry["house_number"]),
    )
