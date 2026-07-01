"""Tests for house-based Graha Drishti foundation helpers."""

from __future__ import annotations

import pytest

from backend.app.kundali import chart, drishti


def test_sun_aspects_seventh_from_placement() -> None:
    assert drishti.get_aspected_houses("sun", 1) == [7]


def test_mars_aspects_fourth_seventh_and_eighth() -> None:
    assert drishti.get_aspected_houses("mars", 1) == [4, 7, 8]


def test_jupiter_aspects_fifth_seventh_and_ninth() -> None:
    assert drishti.get_aspected_houses("jupiter", 1) == [5, 7, 9]


def test_saturn_aspects_third_seventh_and_tenth() -> None:
    assert drishti.get_aspected_houses("saturn", 1) == [3, 7, 10]


def test_wrap_around_house_calculation() -> None:
    assert drishti.get_aspected_houses("sun", 10) == [4]
    assert drishti.get_aspected_houses("mars", 10) == [1, 4, 5]
    assert drishti.normalize_house_number(13) == 1


@pytest.mark.parametrize("planet", ["rahu", "ketu", "pluto", ""])
def test_unsupported_planet_handled_safely(planet: str) -> None:
    assert drishti.get_aspected_houses(planet, 1) == []
    assert drishti.supports_drishti(planet) is False


def test_get_planet_aspects_returns_metadata() -> None:
    aspects = drishti.get_planet_aspects({"planet": "Saturn", "house_number": 10})

    assert aspects == {
        "planet": "saturn",
        "house_number": 10,
        "aspected_houses": [12, 4, 7],
    }


def test_get_planet_aspects_rejects_missing_house_number() -> None:
    with pytest.raises(ValueError, match="house_number"):
        drishti.get_planet_aspects({"planet": "sun"})


def test_chart_planets_include_aspects_for_supported_planets_only() -> None:
    result = chart.assemble_kundali_chart(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
    )

    planets_with_aspects = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "aspects" in planet
    }
    planets_without_aspects = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "aspects" not in planet
    }

    assert set(planets_with_aspects) == {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }
    assert set(planets_without_aspects) == {"rahu", "ketu"}
    assert all(
        planet["aspects"]["aspected_houses"]
        == drishti.get_aspected_houses(planet["planet"], planet["house_number"])
        for planet in planets_with_aspects.values()
    )
