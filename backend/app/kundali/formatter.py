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

    houses: list[FormattedHouse] = [
        {
            **deepcopy(house),
            "planets": [],
        }
        for house in chart["houses"]
    ]

    return {
        "chart_type": chart_type,
        "house_placement_status": HOUSE_PLACEMENT_PLACEHOLDER,
        "houses": houses,
        "lagna_house": {
            "house_number": 1,
            "placement_status": HOUSE_PLACEMENT_PLACEHOLDER,
            "lagna": deepcopy(chart["lagna"]),
        },
        "planets": deepcopy(chart["planets"]),
    }
