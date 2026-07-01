"""Tests for natural Graha relationship helpers."""

from __future__ import annotations

from backend.app.kundali import graha_relationship


def test_sun_to_moon_is_friend() -> None:
    assert graha_relationship.get_natural_relationship("sun", "moon") == "friend"
    assert "moon" in graha_relationship.get_planet_friends("sun")


def test_sun_to_venus_is_enemy() -> None:
    assert graha_relationship.get_natural_relationship("sun", "venus") == "enemy"
    assert "venus" in graha_relationship.get_planet_enemies("sun")


def test_moon_to_saturn_is_neutral() -> None:
    assert graha_relationship.get_natural_relationship("moon", "saturn") == "neutral"
    assert "saturn" in graha_relationship.get_planet_neutrals("moon")


def test_mercury_to_moon_is_enemy() -> None:
    assert graha_relationship.get_natural_relationship("Mercury", "Moon") == "enemy"
    assert "moon" in graha_relationship.get_planet_enemies("mercury")


def test_all_classical_planets_have_relationship_groups() -> None:
    expected = {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }

    assert set(graha_relationship.NATURAL_RELATIONSHIPS) == expected
    for planet in expected:
        related_planets = (
            set(graha_relationship.get_planet_friends(planet))
            | set(graha_relationship.get_planet_neutrals(planet))
            | set(graha_relationship.get_planet_enemies(planet))
        )
        assert related_planets == expected - {planet}


def test_unsupported_planet_is_handled_safely() -> None:
    assert graha_relationship.get_natural_relationship("rahu", "sun") == "unsupported"
    assert graha_relationship.get_natural_relationship("sun", "ketu") == "unsupported"
    assert graha_relationship.get_natural_relationship("pluto", "moon") == "unsupported"
    assert graha_relationship.get_planet_friends("rahu") == ()
    assert graha_relationship.get_planet_neutrals("ketu") == ()
    assert graha_relationship.get_planet_enemies("") == ()
