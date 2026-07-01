"""Tests for basic Kundali chart assembly."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.app.kundali import chart


def test_assemble_kundali_chart_creates_basic_chart(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_lagna = _fake_lagna()
    fake_julian = SimpleNamespace(julian_day_ut=2447893.770833)
    fake_planets = [
        {
            "planet": "sun",
            "tropical_longitude": 294.0,
            "sidereal_longitude": 270.0,
            "rashi_index": 9,
            "rashi_name_hi": "मकर",
            "degree_in_rashi": 0.0,
            "dms": {"degrees": 0, "minutes": 0, "seconds": 0.0},
            "speed": 1.0,
            "retrograde": False,
        },
        {
            "planet": "moon",
            "tropical_longitude": 54.5,
            "sidereal_longitude": 30.5,
            "rashi_index": 1,
            "rashi_name_hi": "वृषभ",
            "degree_in_rashi": 0.5,
            "dms": {"degrees": 0, "minutes": 30, "seconds": 0.0},
            "speed": 13.0,
            "retrograde": False,
        },
    ]
    monkeypatch.setattr(chart.julian, "calculate_julian_day", lambda *args: fake_julian)
    monkeypatch.setattr(chart.ayanamsa, "get_ayanamsa", lambda *args: 24.0)
    monkeypatch.setattr(
        chart.planet_positions,
        "get_planet_positions",
        lambda *args: fake_planets,
    )
    monkeypatch.setattr(chart.lagna, "calculate_lagna", lambda *args: fake_lagna)

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

    assert set(result) == {"lagna", "planets", "houses"}
    assert result["lagna"] == fake_lagna
    assert len(result["planets"]) == 2
    assert len(result["houses"]) == 12
    assert all("house_number" in planet for planet in result["planets"])
    assert all("house_index" in planet for planet in result["planets"])


def test_assemble_kundali_chart_attaches_rashi_metadata_to_planets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_julian = SimpleNamespace(julian_day_ut=2447893.770833)
    monkeypatch.setattr(chart.julian, "calculate_julian_day", lambda *args: fake_julian)
    monkeypatch.setattr(chart.ayanamsa, "get_ayanamsa", lambda *args: 24.0)
    monkeypatch.setattr(chart.lagna, "calculate_lagna", lambda *args: _fake_lagna())
    monkeypatch.setattr(
        chart.planet_positions,
        "get_planet_positions",
        lambda *args: [
            {
                "planet": "sun",
                "sidereal_longitude": 30.5,
                "rashi_index": 1,
                "rashi_name_hi": "वृषभ",
                "degree_in_rashi": 0.5,
            }
        ],
    )

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
    sun = result["planets"][0]

    assert sun["planet"] == "sun"
    assert sun["rashi"]["english"] == "Taurus"
    assert sun["rashi"]["hindi"] == "वृषभ"
    assert sun["rashi_degree"] == 0.5
    assert sun["rashi_index"] == 1
    assert sun["degree_in_rashi"] == 0.5
    assert sun["house_number"] == 2
    assert sun["house_index"] == 1


def test_placeholder_houses_have_twelve_houses() -> None:
    houses = chart._build_placeholder_houses()

    assert len(houses) == 12
    assert houses[0] == {
        "house_number": 1,
        "house_index": 0,
        "start_degree": 0.0,
        "end_degree": 30.0,
        "house_degree": 0.0,
        "planets": [],
    }
    assert houses[-1] == {
        "house_number": 12,
        "house_index": 11,
        "start_degree": 330.0,
        "end_degree": 360.0,
        "house_degree": 0.0,
        "planets": [],
    }


def test_placeholder_houses_group_planets_by_house() -> None:
    planets = [
        {
            "planet": "sun",
            "sidereal_longitude": 30.5,
            "rashi_index": 1,
            "rashi_name_hi": "वृषभ",
            "degree_in_rashi": 0.5,
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
        }
    ]

    houses = chart._build_placeholder_houses(planets)

    assert houses[0]["planets"] == []
    assert houses[1]["planets"] == planets


def test_assemble_kundali_chart_works_for_jaipur_sample_birth_data() -> None:
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

    assert 0.0 <= result["lagna"]["ascendant_longitude"] < 360.0
    assert "rashi" in result["lagna"]
    assert result["lagna"]["rashi_index"] == result["lagna"]["rashi"]["index"]
    assert len(result["planets"]) == 9
    assert all("rashi" in planet for planet in result["planets"])
    assert all("rashi_degree" in planet for planet in result["planets"])
    assert all("house_number" in planet for planet in result["planets"])
    assert len(result["houses"]) == 12
    assert sum(len(house["planets"]) for house in result["houses"]) == 9


def _fake_lagna() -> chart.lagna.LagnaResult:
    return {
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
    }
