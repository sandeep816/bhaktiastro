"""Tests for whole-sign planet house placement foundation."""

from __future__ import annotations

from backend.app.kundali.placement import (
    get_house_index_from_rashi,
    get_house_number_from_rashi,
    get_planet_house_placement,
)


def test_lagna_rashi_maps_to_house_one() -> None:
    assert get_house_number_from_rashi(1, 1) == 1
    assert get_house_index_from_rashi(1, 1) == 0


def test_next_rashi_maps_to_house_two() -> None:
    assert get_house_number_from_rashi(1, 2) == 2
    assert get_house_index_from_rashi(1, 2) == 1


def test_wrap_around_from_meena_to_mesha_maps_to_house_two() -> None:
    assert get_house_number_from_rashi(12, 1) == 2
    assert get_house_index_from_rashi(12, 1) == 1


def test_planet_house_placement_contains_rashi_and_house_metadata() -> None:
    placement = get_planet_house_placement(12, 15.25)

    assert placement["house_number"] == 2
    assert placement["house_index"] == 1
    assert placement["rashi"]["english"] == "Aries"
    assert placement["rashi_index"] == 1
    assert placement["rashi_degree"] == 15.25
