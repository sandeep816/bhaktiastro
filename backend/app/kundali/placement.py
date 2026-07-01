"""Whole-sign planet house placement foundation."""

from __future__ import annotations

from typing import TypedDict

from backend.app.kundali import bhava, rashi as rashi_engine


class HousePlacement(TypedDict):
    """House placement metadata for a sidereal longitude."""

    house_number: int
    house_index: int
    rashi: rashi_engine.RashiResult
    rashi_index: int
    rashi_degree: float


def get_house_number_from_rashi(
    lagna_rashi_index: int,
    planet_rashi_index: int,
) -> int:
    """Return whole-sign house number from Lagna and planet Rashi indexes.

    Args:
        lagna_rashi_index: One-based Lagna Rashi index.
        planet_rashi_index: One-based planet Rashi index.

    Returns:
        One-based house number where Lagna Rashi is House 1.
    """

    lagna_index = rashi_engine.get_rashi_index(
        (bhava.normalize_house_number(lagna_rashi_index) - 1)
        * bhava.HOUSE_SPAN_DEGREES
    )
    planet_index = rashi_engine.get_rashi_index(
        (bhava.normalize_house_number(planet_rashi_index) - 1)
        * bhava.HOUSE_SPAN_DEGREES
    )
    return ((planet_index - lagna_index) % bhava.HOUSE_COUNT) + 1


def get_house_index_from_rashi(
    lagna_rashi_index: int,
    planet_rashi_index: int,
) -> int:
    """Return zero-based whole-sign house index from Rashi indexes."""

    return get_house_number_from_rashi(lagna_rashi_index, planet_rashi_index) - 1


def get_planet_house_placement(
    lagna_rashi_index: int,
    sidereal_longitude: float,
) -> HousePlacement:
    """Return whole-sign house placement for a planet longitude."""

    rashi = rashi_engine.get_rashi(sidereal_longitude)
    house_number = get_house_number_from_rashi(lagna_rashi_index, rashi["index"])
    return {
        "house_number": house_number,
        "house_index": house_number - 1,
        "rashi": rashi,
        "rashi_index": rashi["index"],
        "rashi_degree": rashi_engine.get_rashi_degree(sidereal_longitude),
    }
