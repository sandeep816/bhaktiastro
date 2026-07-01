"""Tests for planet dignity foundation helpers."""

from __future__ import annotations

import pytest

from backend.app.kundali import chart, dignity


@pytest.mark.parametrize(
    ("planet", "rashi"),
    [
        ("sun", "Mesha"),
        ("moon", "Vrishabha"),
        ("mars", "Makara"),
        ("mercury", "Kanya"),
        ("jupiter", "Karka"),
        ("venus", "Meena"),
        ("saturn", "Tula"),
    ],
)
def test_exaltation_mapping(planet: str, rashi: str) -> None:
    assert dignity.get_exaltation_rashi(planet) == rashi


@pytest.mark.parametrize(
    ("planet", "rashi"),
    [
        ("sun", "Tula"),
        ("moon", "Vrishchika"),
        ("mars", "Karka"),
        ("mercury", "Meena"),
        ("jupiter", "Makara"),
        ("venus", "Kanya"),
        ("saturn", "Mesha"),
    ],
)
def test_debilitation_mapping(planet: str, rashi: str) -> None:
    assert dignity.get_debilitation_rashi(planet) == rashi


def test_dignity_status_returns_exalted() -> None:
    assert dignity.get_planet_dignity("sun", "Mesha") == "exalted"
    assert (
        dignity.get_planet_dignity("Moon", {"sanskrit": "Vrishabha"})
        == "exalted"
    )


def test_dignity_status_returns_debilitated() -> None:
    assert dignity.get_planet_dignity("mars", "Karka") == "debilitated"
    assert dignity.get_planet_dignity("moon", "Vrischika") == "debilitated"


def test_dignity_status_returns_neutral() -> None:
    assert dignity.get_planet_dignity("jupiter", "Dhanu") == "neutral"
    assert dignity.get_planet_dignity("venus", 7) == "neutral"


@pytest.mark.parametrize("planet", ["rahu", "ketu", "pluto", ""])
def test_invalid_or_unsupported_planet_is_handled_safely(planet: str) -> None:
    with pytest.raises(ValueError, match="Unsupported planet dignity mapping"):
        dignity.get_exaltation_rashi(planet)


def test_chart_planets_include_dignity_for_supported_planets_only() -> None:
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

    supported_planets = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "dignity" in planet
    }
    unsupported_planets = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "dignity" not in planet
    }

    assert set(supported_planets) == {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }
    assert set(unsupported_planets) == {"rahu", "ketu"}
    assert all(
        planet["dignity"]["status"]
        == dignity.get_planet_dignity(planet["planet"], planet["rashi"])
        for planet in supported_planets.values()
    )
