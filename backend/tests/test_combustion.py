"""Tests for combustion foundation helpers."""

from __future__ import annotations

import pytest

from backend.app.kundali import chart, combustion


def test_angular_distance_normal_case() -> None:
    assert combustion.angular_distance(10.0, 40.0) == 30.0


def test_angular_distance_wrap_around_case() -> None:
    assert combustion.angular_distance(350.0, 10.0) == 20.0


def test_planet_within_orb_is_combust() -> None:
    assert combustion.is_combust("venus", 45.0, 38.0) is True
    assert combustion.get_combustion_status("venus", 45.0, 38.0) == "combust"


def test_planet_outside_orb_is_not_combust() -> None:
    assert combustion.is_combust("jupiter", 60.0, 30.0) is False
    assert combustion.get_combustion_status("jupiter", 60.0, 30.0) == "not_combust"


def test_sun_returns_not_combust_safely() -> None:
    assert combustion.is_combust("sun", 30.0, 30.0) is False
    assert combustion.get_combustion_status("sun", 30.0, 30.0) == "not_combust"


@pytest.mark.parametrize("planet", ["rahu", "ketu", "pluto", ""])
def test_unsupported_planet_handled_safely(planet: str) -> None:
    assert combustion.is_combust(planet, 30.0, 30.0) is False
    assert combustion.get_combustion_status(planet, 30.0, 30.0) == "unsupported"


def test_invalid_longitude_is_handled_safely() -> None:
    with pytest.raises(TypeError, match="longitude must be a real number"):
        combustion.angular_distance("30", 40.0)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="longitude must be finite"):
        combustion.angular_distance(float("inf"), 40.0)


def test_chart_planets_include_combustion_for_supported_planets_only() -> None:
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

    planets_with_combustion = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "combustion" in planet
    }
    planets_without_combustion = {
        planet["planet"]: planet
        for planet in result["planets"]
        if "combustion" not in planet
    }
    sun_longitude = next(
        planet["sidereal_longitude"]
        for planet in result["planets"]
        if planet["planet"] == "sun"
    )

    assert set(planets_with_combustion) == {
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }
    assert set(planets_without_combustion) == {"sun", "rahu", "ketu"}
    assert all(
        planet["combustion"]["status"]
        == combustion.get_combustion_status(
            planet["planet"],
            planet["sidereal_longitude"],
            sun_longitude,
        )
        for planet in planets_with_combustion.values()
    )
