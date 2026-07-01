"""Tests for JSON-ready Kundali chart formatter foundations."""

from __future__ import annotations

from copy import deepcopy

import pytest

from backend.app.kundali import formatter


def test_north_indian_formatter_returns_twelve_houses() -> None:
    formatted = formatter.format_north_indian_chart(_sample_chart())

    assert formatted["chart_type"] == "north_indian"
    assert formatted["house_placement_status"] == "whole_sign_foundation"
    assert len(formatted["houses"]) == 12
    assert formatted["houses"][0]["house_number"] == 1
    assert formatted["houses"][-1]["house_number"] == 12


def test_south_indian_formatter_returns_twelve_houses() -> None:
    formatted = formatter.format_south_indian_chart(_sample_chart())

    assert formatted["chart_type"] == "south_indian"
    assert formatted["house_placement_status"] == "whole_sign_foundation"
    assert len(formatted["houses"]) == 12


def test_formatter_includes_lagna_house() -> None:
    formatted = formatter.format_north_indian_chart(_sample_chart())

    assert formatted["lagna_house"]["house_number"] == 1
    assert formatted["lagna_house"]["placement_status"] == "whole_sign_foundation"
    assert formatted["lagna_house"]["lagna"]["rashi"]["english"] == "Aries"


def test_formatter_groups_planets_by_house_when_house_placement_exists() -> None:
    formatted = formatter.format_south_indian_chart(_sample_chart())

    assert len(formatted["planets"]) == 2
    assert formatted["planets"][0]["planet"] == "sun"
    assert formatted["houses"][0]["planets"] == []
    assert [planet["planet"] for planet in formatted["houses"][1]["planets"]] == [
        "moon"
    ]
    assert [planet["planet"] for planet in formatted["houses"][9]["planets"]] == [
        "sun"
    ]


def test_formatter_does_not_mutate_original_chart_data() -> None:
    chart = _sample_chart()
    original = deepcopy(chart)

    formatted = formatter.format_north_indian_chart(chart)
    formatted["houses"][0]["planets"].append(formatted["planets"][0])
    formatted["planets"][0]["planet"] = "changed"
    formatted["lagna_house"]["lagna"]["rashi"]["english"] = "Changed"

    assert chart == original


def test_unsupported_chart_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unsupported chart_type"):
        formatter.format_chart(_sample_chart(), "east_indian")  # type: ignore[arg-type]


def _sample_chart() -> dict[str, object]:
    return {
        "lagna": {
            "ascendant_longitude": 23.25,
            "sidereal_longitude": 23.25,
            "tropical_longitude": 47.25,
            "ayanamsa": 24.0,
            "rashi": {
                "index": 1,
                "english": "Aries",
                "hindi": "मेष",
                "sanskrit": "Mesha",
                "lord": "Mars",
                "element": "Fire",
                "modality": "Movable",
                "start_degree": 0.0,
                "end_degree": 30.0,
                "degree_in_rashi": 23.25,
            },
            "rashi_index": 1,
            "rashi_degree": 23.25,
        },
        "planets": [
            {
                "planet": "sun",
                "sidereal_longitude": 270.0,
                "rashi_index": 9,
                "rashi_name_hi": "मकर",
                "degree_in_rashi": 0.0,
                "dms": {"degrees": 0, "minutes": 0, "seconds": 0.0},
                "retrograde": False,
                "rashi": {
                    "index": 10,
                    "english": "Capricorn",
                    "hindi": "मकर",
                    "sanskrit": "Makara",
                    "lord": "Saturn",
                    "element": "Earth",
                    "modality": "Movable",
                    "start_degree": 270.0,
                    "end_degree": 300.0,
                    "degree_in_rashi": 0.0,
                },
                "rashi_degree": 0.0,
                "house_number": 10,
                "house_index": 9,
            },
            {
                "planet": "moon",
                "sidereal_longitude": 30.5,
                "rashi_index": 1,
                "rashi_name_hi": "वृषभ",
                "degree_in_rashi": 0.5,
                "dms": {"degrees": 0, "minutes": 30, "seconds": 0.0},
                "retrograde": False,
                "rashi": {
                    "index": 2,
                    "english": "Taurus",
                    "hindi": "वृषभ",
                    "sanskrit": "Vrishabha",
                    "lord": "Venus",
                    "element": "Earth",
                    "modality": "Fixed",
                    "start_degree": 30.0,
                    "end_degree": 60.0,
                    "degree_in_rashi": 0.5,
                },
                "rashi_degree": 0.5,
                "house_number": 2,
                "house_index": 1,
            },
        ],
        "houses": [
            {
                "house_number": house_number,
                "house_index": house_number - 1,
                "start_degree": float((house_number - 1) * 30),
                "end_degree": float(house_number * 30),
                "house_degree": 0.0,
            }
            for house_number in range(1, 13)
        ],
    }
