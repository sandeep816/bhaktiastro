"""Tests for Mooltrikona foundation helpers."""

from __future__ import annotations

import pytest

from backend.app.kundali import chart, mooltrikona


@pytest.mark.parametrize(
    ("planet", "rashi"),
    [
        ("sun", "Simha"),
        ("moon", "Vrishabha"),
        ("mars", "Mesha"),
        ("mercury", "Kanya"),
        ("jupiter", "Dhanu"),
        ("venus", "Tula"),
        ("saturn", "Kumbha"),
    ],
)
def test_supported_planets_return_correct_mooltrikona_rashi(
    planet: str,
    rashi: str,
) -> None:
    assert mooltrikona.get_mooltrikona_rashi(planet) == rashi


@pytest.mark.parametrize(
    ("planet", "rashi"),
    [
        ("sun", "Simha"),
        ("moon", {"sanskrit": "Vrishabha"}),
        ("mars", 1),
        ("Mercury", "Kanya"),
    ],
)
def test_is_mooltrikona_returns_true_for_matching_rashi(
    planet: str,
    rashi: object,
) -> None:
    assert mooltrikona.is_mooltrikona(planet, rashi) is True


def test_is_mooltrikona_returns_false_for_non_matching_rashi() -> None:
    assert mooltrikona.is_mooltrikona("jupiter", "Meena") is False
    assert mooltrikona.is_mooltrikona("venus", {"sanskrit": "Kanya"}) is False


@pytest.mark.parametrize("planet", ["rahu", "ketu", "pluto", ""])
def test_unsupported_planet_is_handled_safely(planet: str) -> None:
    with pytest.raises(ValueError, match="Unsupported planet Mooltrikona mapping"):
        mooltrikona.get_mooltrikona_rashi(planet)


def test_attach_mooltrikona_status_enriches_copy_without_mutating_input() -> None:
    data = {
        "planet": "sun",
        "rashi": {"index": 5, "sanskrit": "Simha"},
    }

    enriched = mooltrikona.attach_mooltrikona_status(data)

    assert enriched["mooltrikona"] == {
        "rashi": "Simha",
        "is_mooltrikona": True,
    }
    assert "mooltrikona" not in data


def test_chart_planets_include_mooltrikona_for_supported_planets_only() -> None:
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
        if "mooltrikona" in planet
    }
    unsupported_planets = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "mooltrikona" not in planet
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
        planet["mooltrikona"]["is_mooltrikona"]
        == mooltrikona.is_mooltrikona(planet["planet"], planet["rashi"])
        for planet in supported_planets.values()
    )
