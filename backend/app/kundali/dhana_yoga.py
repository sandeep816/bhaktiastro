"""Foundation detector for Dhana Yoga."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.kundali import raja_yoga, yoga_framework

YOGA_NAME = "Dhana Yoga"
SECOND_HOUSE = 2
ELEVENTH_HOUSE = 11


def detect_dhana_yoga(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Detect foundational Dhana Yoga from house lord and placement metadata."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    house_lords = raja_yoga._get_house_lords(chart_data)
    if not house_lords:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            reason="House lord metadata is missing.",
        )

    planet_houses = raja_yoga._get_planet_houses(chart_data)
    if not planet_houses:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            reason="Planet house placement metadata is missing.",
        )

    second_lord = house_lords.get(SECOND_HOUSE)
    eleventh_lord = house_lords.get(ELEVENTH_HOUSE)
    if second_lord is None or eleventh_lord is None:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            reason="Second or eleventh house lord metadata is missing.",
        )

    second_lord_house = planet_houses.get(second_lord)
    eleventh_lord_house = planet_houses.get(eleventh_lord)
    if second_lord_house is None or eleventh_lord_house is None:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=False,
            involved_planets=[second_lord, eleventh_lord],
            reason="Second or eleventh lord house placement metadata is missing.",
        )

    if second_lord_house == eleventh_lord_house:
        return yoga_framework.create_yoga_result(
            yoga_name=YOGA_NAME,
            is_present=True,
            involved_planets=[second_lord, eleventh_lord],
            involved_houses=[SECOND_HOUSE, ELEVENTH_HOUSE, second_lord_house],
            reason="Second lord and eleventh lord are in the same house.",
        )

    return yoga_framework.create_yoga_result(
        yoga_name=YOGA_NAME,
        is_present=False,
        involved_planets=[second_lord, eleventh_lord],
        reason="Second lord and eleventh lord do not share the same house.",
    )


yoga_framework.register_yoga_detector("dhana_yoga", detect_dhana_yoga)
