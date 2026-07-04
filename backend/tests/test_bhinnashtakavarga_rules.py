"""Tests for Bhinnashtakavarga rule table foundation."""

from __future__ import annotations

import json

from backend.app.ashtakavarga.bhinnashtakavarga import (
    BAV_SOURCES,
    get_bav_rule,
    get_contributing_houses,
    is_valid_bav_source,
)
from backend.app.ashtakavarga.constants import ASHTAKAVARGA_HOUSES


def test_rule_exists_for_all_supported_planets() -> None:
    for planet in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        rule = get_bav_rule(planet)

        assert rule["planet"] == planet
        assert set(rule["sources"]) == set(BAV_SOURCES)
        assert rule["metadata"]["calculation_status"] == "rule_table"
        for houses in rule["sources"].values():
            assert houses
            assert all(house in ASHTAKAVARGA_HOUSES for house in houses)


def test_sun_rule_can_be_fetched() -> None:
    rule = get_bav_rule(" Sun ")

    assert rule["planet"] == "sun"
    assert rule["sources"]["sun"] == [1, 2, 4, 7, 8, 9, 10, 11]
    assert rule["sources"]["lagna"] == [3, 4, 6, 10, 11, 12]
    json.dumps(rule)


def test_moon_rule_can_be_fetched() -> None:
    rule = get_bav_rule("Moon")

    assert rule["planet"] == "moon"
    assert rule["sources"]["moon"] == [1, 3, 6, 7, 10, 11]
    assert rule["sources"]["lagna"] == [3, 6, 10, 11]
    json.dumps(rule)


def test_lagna_source_is_supported() -> None:
    assert is_valid_bav_source("lagna") is True
    assert is_valid_bav_source(" Lagna ") is True
    assert get_contributing_houses("sun", "lagna") == [3, 4, 6, 10, 11, 12]


def test_unsupported_planet_is_handled_safely() -> None:
    rule = get_bav_rule("rahu")

    assert rule == {
        "planet": "rahu",
        "sources": {},
        "metadata": {
            "calculation_status": "rule_table",
            "rule_status": "foundation",
        },
    }
    assert get_contributing_houses("ketu", "sun") == []
    json.dumps(rule)


def test_unsupported_source_is_handled_safely() -> None:
    assert is_valid_bav_source("rahu") is False
    assert is_valid_bav_source("") is False
    assert is_valid_bav_source(None) is False  # type: ignore[arg-type]
    assert get_contributing_houses("sun", "rahu") == []
    assert get_contributing_houses("sun", None) == []  # type: ignore[arg-type]


def test_contributing_houses_are_returned_as_copies() -> None:
    houses = get_contributing_houses("sun", "sun")
    houses.append(12)

    assert get_contributing_houses("sun", "sun") == [1, 2, 4, 7, 8, 9, 10, 11]
