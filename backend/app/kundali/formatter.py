"""JSON-ready Kundali chart format helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Literal, TypedDict

from backend.app.kundali.chart import (
    HousePlaceholder,
    KundaliChart,
    PlanetChartPosition,
)
from backend.app.kundali.lagna import LagnaResult

ChartType = Literal["north_indian", "south_indian"]
HOUSE_PLACEMENT_PLACEHOLDER = "placeholder"
HOUSE_PLACEMENT_WHOLE_SIGN = "whole_sign_foundation"


class FormattedHouse(HousePlaceholder):
    """Formatted house with placeholder planet grouping."""

    planets: list[PlanetChartPosition]


class LagnaHouse(TypedDict):
    """Lagna house metadata for chart-format foundations."""

    house_number: int
    placement_status: str
    lagna: LagnaResult


class FormattedChart(TypedDict):
    """JSON-ready chart format foundation."""

    chart_type: ChartType
    house_placement_status: str
    houses: list[FormattedHouse]
    lagna_house: LagnaHouse
    planets: list[PlanetChartPosition]


def format_north_indian_chart(chart: KundaliChart) -> FormattedChart:
    """Return a JSON-ready North Indian chart foundation."""

    return _format_chart(chart, "north_indian")


def format_south_indian_chart(chart: KundaliChart) -> FormattedChart:
    """Return a JSON-ready South Indian chart foundation."""

    return _format_chart(chart, "south_indian")


def format_chart(chart: KundaliChart, chart_type: ChartType) -> FormattedChart:
    """Return a JSON-ready chart foundation for a supported chart type."""

    return _format_chart(chart, chart_type)


def _format_chart(chart: KundaliChart, chart_type: ChartType) -> FormattedChart:
    """Format a chart without mutating the assembled chart data."""

    if chart_type not in ("north_indian", "south_indian"):
        raise ValueError(f"Unsupported chart_type: {chart_type}")

    houses = _format_houses(chart)

    return {
        "chart_type": chart_type,
        "house_placement_status": _house_placement_status(chart),
        "houses": houses,
        "lagna_house": {
            "house_number": 1,
            "placement_status": _house_placement_status(chart),
            "lagna": deepcopy(chart["lagna"]),
        },
        "planets": deepcopy(chart["planets"]),
    }


def _format_houses(chart: KundaliChart) -> list[FormattedHouse]:
    """Return houses with planets grouped when placement data is available."""

    if any("planets" in house for house in chart["houses"]):
        return [
            {
                **deepcopy(house),
                "planets": deepcopy(house.get("planets", [])),
            }
            for house in chart["houses"]
        ]

    planets_by_house: dict[int, list[PlanetChartPosition]] = {
        int(house["house_number"]): [] for house in chart["houses"]
    }
    for planet in chart["planets"]:
        house_number = planet.get("house_number")
        if house_number in planets_by_house:
            planets_by_house[house_number].append(deepcopy(planet))

    return [
        {
            **deepcopy(house),
            "planets": planets_by_house[int(house["house_number"])],
        }
        for house in chart["houses"]
    ]


def _house_placement_status(chart: KundaliChart) -> str:
    """Return formatter placement status for the supplied chart."""

    if any("house_number" in planet for planet in chart["planets"]):
        return HOUSE_PLACEMENT_WHOLE_SIGN
    return HOUSE_PLACEMENT_PLACEHOLDER
