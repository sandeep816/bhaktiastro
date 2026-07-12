"""Tests for basic Kundali chart assembly."""

from __future__ import annotations

import json
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
    assert "strength" not in result
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


def test_assemble_varga_charts_returns_supported_chart_keys() -> None:
    result = chart.assemble_varga_charts(_fake_chart_for_vargas())

    assert set(result) == {
        "D2",
        "D3",
        "D7",
        "D9",
        "D10",
        "D12",
        "D16",
        "D20",
        "D24",
        "D27",
        "D30",
        "D40",
        "D45",
        "D60",
    }


def test_assemble_varga_charts_contains_planet_entries_for_each_chart() -> None:
    result = chart.assemble_varga_charts(_fake_chart_for_vargas())

    assert result
    assert all(len(varga_chart["planets"]) == 2 for varga_chart in result.values())
    assert all(
        "varga_position" in planet
        for varga_chart in result.values()
        for planet in varga_chart["planets"]
    )


def test_assemble_varga_charts_includes_d9_navamsa() -> None:
    result = chart.assemble_varga_charts(_fake_chart_for_vargas())

    assert "D9" in result
    assert result["D9"]["varga_name"] == "Navamsa"
    assert result["D9"]["planets"][0]["varga_position"]["varga_code"] == "D9"


def test_assemble_kundali_chart_can_include_internal_varga_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_lagna = _fake_lagna()
    fake_julian = SimpleNamespace(julian_day_ut=2447893.770833)
    fake_planets = [
        {"planet": "sun", "sidereal_longitude": 270.0},
        {"planet": "moon", "sidereal_longitude": 30.5},
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
        include_vargas=True,
    )

    assert set(result) == {"lagna", "planets", "houses", "vargas"}
    assert "D9" in result["vargas"]
    assert len(result["vargas"]["D9"]["planets"]) == 2


def test_assemble_kundali_chart_can_include_internal_strength_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [
            {"planet": "sun", "sidereal_longitude": 0.0},
            {"planet": "venus", "sidereal_longitude": 30.0, "speed": 1.0},
        ],
        include_strength=True,
    )

    assert set(result) == {"lagna", "planets", "houses", "strength"}
    assert len(result["strength"]["planets"]) == 2
    assert result["strength"]["metadata"]["planet_count"] == 2
    assert result["strength"]["ranking"]


def test_internal_strength_summary_contains_planet_entries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [
            {"planet": "sun", "sidereal_longitude": 0.0},
            {"planet": "moon", "sidereal_longitude": 30.0},
        ],
        include_strength=True,
    )

    planet_entries = result["strength"]["planets"]

    assert [entry["planet"] for entry in planet_entries] == ["sun", "moon"]
    assert all("shadbala" in entry for entry in planet_entries)
    assert all("ishta_kashta" in entry for entry in planet_entries)


def test_assemble_kundali_chart_default_structure_remains_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [{"planet": "sun", "sidereal_longitude": 0.0}],
    )

    assert set(result) == {"lagna", "planets", "houses"}
    assert "strength" not in result


def test_internal_strength_summary_handles_missing_planet_data_safely(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [],
        include_strength=True,
    )

    assert result["planets"] == []
    assert result["strength"]["planets"] == []
    assert result["strength"]["ranking"] == []
    assert result["strength"]["strongest_planet"] is None
    assert result["strength"]["weakest_planet"] is None


def test_internal_strength_summary_output_is_json_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [
            {"planet": "sun", "sidereal_longitude": 0.0},
            {"planet": "moon", "sidereal_longitude": 30.0},
        ],
        include_strength=True,
    )

    json.dumps(result)


def test_assemble_kundali_chart_can_include_internal_ashtakavarga_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_ashtakavarga_planets(),
        include_ashtakavarga=True,
    )

    assert set(result) == {"lagna", "planets", "houses", "ashtakavarga"}
    assert "sarvashtakavarga" in result["ashtakavarga"]
    assert "bhinnashtakavarga" in result["ashtakavarga"]
    assert len(result["ashtakavarga"]["house_ranking"]) == 12


def test_internal_ashtakavarga_summary_contains_sav_and_bav(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_ashtakavarga_planets(),
        include_ashtakavarga=True,
    )

    ashtakavarga = result["ashtakavarga"]

    assert set(ashtakavarga["sarvashtakavarga"]["houses"]) == set(range(1, 13))
    assert set(ashtakavarga["bhinnashtakavarga"]) == {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }


def test_assemble_kundali_chart_default_structure_excludes_ashtakavarga(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_ashtakavarga_planets(),
    )

    assert set(result) == {"lagna", "planets", "houses"}
    assert "ashtakavarga" not in result


def test_internal_ashtakavarga_summary_handles_missing_planet_data_safely(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [],
        include_ashtakavarga=True,
    )

    assert result["planets"] == []
    assert "sarvashtakavarga" in result["ashtakavarga"]
    assert "bhinnashtakavarga" in result["ashtakavarga"]
    assert result["ashtakavarga"]["strongest_house"] is not None
    assert result["ashtakavarga"]["weakest_house"] is not None


def test_internal_ashtakavarga_summary_output_is_json_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_ashtakavarga_planets(),
        include_ashtakavarga=True,
    )

    json.dumps(result)


def test_assemble_kundali_chart_can_include_internal_special_lagna_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_special_lagna_planets(),
        include_special_lagna=True,
    )

    assert set(result) == {"lagna", "planets", "houses", "special_lagna"}
    assert "arudha_lagna" in result["special_lagna"]
    assert "upapada_lagna" in result["special_lagna"]
    assert "bhava_cusps" in result["special_lagna"]


def test_internal_special_lagna_summary_contains_arudha_and_upapada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_special_lagna_planets(),
        include_special_lagna=True,
    )

    special_lagna = result["special_lagna"]

    assert special_lagna["arudha_lagna"]["metadata"]["component"] == "arudha_lagna"
    assert (
        special_lagna["arudha_lagna"]["metadata"]["calculation_status"]
        == "calculated"
    )
    assert special_lagna["upapada_lagna"]["metadata"]["component"] == "upapada_lagna"
    assert (
        special_lagna["upapada_lagna"]["metadata"]["calculation_status"]
        == "calculated"
    )


def test_internal_special_lagna_summary_contains_bhava_cusps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_special_lagna_planets(),
        include_special_lagna=True,
    )

    bhava_cusps = result["special_lagna"]["bhava_cusps"]

    assert bhava_cusps["house_system"] == "equal_foundation"
    assert len(bhava_cusps["house_cusps"]) == 12
    assert bhava_cusps["house_cusps"][0]["cusp_longitude"] == 23.25


def test_assemble_kundali_chart_default_structure_excludes_special_lagna(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_special_lagna_planets(),
    )

    assert set(result) == {"lagna", "planets", "houses"}
    assert "special_lagna" not in result


def test_internal_special_lagna_summary_handles_missing_context_safely(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_special_lagna_planets(),
        include_special_lagna=True,
    )

    special_lagna = result["special_lagna"]

    assert special_lagna["metadata"]["context_available"] is True
    assert special_lagna["metadata"]["birth_datetime_available"] is True
    assert special_lagna["metadata"]["sunrise_datetime_available"] is False
    assert (
        special_lagna["hora_lagna"]["metadata"]["calculation_status"]
        == "missing_data"
    )
    assert special_lagna["hora_lagna"]["metadata"]["missing_fields"] == [
        "sunrise_datetime"
    ]
    assert special_lagna["ghati_lagna"]["metadata"]["calculation_status"] == (
        "missing_data"
    )
    assert special_lagna["ghati_lagna"]["metadata"]["missing_fields"] == [
        "sunrise_datetime"
    ]


def test_internal_special_lagna_summary_output_is_json_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        _fake_special_lagna_planets(),
        include_special_lagna=True,
    )

    json.dumps(result)


def test_assemble_kundali_chart_can_include_internal_prediction_framework(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [{"planet": "sun", "sidereal_longitude": 0.0}],
        include_prediction_framework=True,
    )

    assert set(result) == {"lagna", "planets", "houses", "prediction_framework"}
    assert result["prediction_framework"]["context"]["metadata"]["planet_count"] == 1
    assert result["prediction_framework"]["context"]["planets"][0]["planet"] == "sun"


def test_internal_prediction_framework_empty_rules_produce_empty_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [{"planet": "sun", "sidereal_longitude": 0.0}],
        include_prediction_framework=True,
    )

    prediction_framework = result["prediction_framework"]

    assert prediction_framework["rule_results"] == []
    assert prediction_framework["predictions"]["categories"] == {}
    assert prediction_framework["predictions"]["summary"]["total_rules"] == 0
    assert prediction_framework["metadata"]["rules_count"] == 0
    assert prediction_framework["metadata"]["real_prediction_rules_enabled"] is False


def test_assemble_kundali_chart_default_structure_excludes_prediction_framework(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [{"planet": "sun", "sidereal_longitude": 0.0}],
    )

    assert set(result) == {"lagna", "planets", "houses"}
    assert "prediction_framework" not in result


def test_internal_prediction_framework_handles_missing_optional_data_safely(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [],
        include_prediction_framework=True,
    )

    prediction_context = result["prediction_framework"]["context"]

    assert prediction_context["metadata"]["planet_count"] == 0
    assert prediction_context["metadata"]["missing_optional_components"] == [
        "vargas",
        "strength",
        "ashtakavarga",
        "special_lagna",
    ]
    assert result["prediction_framework"]["predictions"]["summary"]["total_rules"] == 0


def test_internal_prediction_framework_output_is_json_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _assemble_fake_chart(
        monkeypatch,
        [{"planet": "sun", "sidereal_longitude": 0.0}],
        include_prediction_framework=True,
    )

    json.dumps(result)


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


def _assemble_fake_chart(
    monkeypatch: pytest.MonkeyPatch,
    fake_planets: list[dict[str, object]],
    include_strength: bool = False,
    include_ashtakavarga: bool = False,
    include_special_lagna: bool = False,
    include_prediction_framework: bool = False,
) -> chart.KundaliChart:
    fake_julian = SimpleNamespace(julian_day_ut=2447893.770833)
    monkeypatch.setattr(chart.julian, "calculate_julian_day", lambda *args: fake_julian)
    monkeypatch.setattr(chart.ayanamsa, "get_ayanamsa", lambda *args: 24.0)
    monkeypatch.setattr(
        chart.planet_positions,
        "get_planet_positions",
        lambda *args: fake_planets,
    )
    monkeypatch.setattr(chart.lagna, "calculate_lagna", lambda *args: _fake_lagna())

    return chart.assemble_kundali_chart(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
        include_strength=include_strength,
        include_ashtakavarga=include_ashtakavarga,
        include_special_lagna=include_special_lagna,
        include_prediction_framework=include_prediction_framework,
    )


def _fake_ashtakavarga_planets() -> list[dict[str, object]]:
    return [
        {"planet": "sun", "sidereal_longitude": 0.0},
        {"planet": "moon", "sidereal_longitude": 30.0},
        {"planet": "mars", "sidereal_longitude": 60.0, "speed": 1.0},
        {"planet": "mercury", "sidereal_longitude": 90.0, "speed": 1.0},
        {"planet": "jupiter", "sidereal_longitude": 120.0, "speed": 1.0},
        {"planet": "venus", "sidereal_longitude": 150.0, "speed": 1.0},
        {"planet": "saturn", "sidereal_longitude": 180.0, "speed": 1.0},
    ]


def _fake_special_lagna_planets() -> list[dict[str, object]]:
    return [
        {"planet": "mars", "sidereal_longitude": 30.0, "speed": 1.0},
        {"planet": "jupiter", "sidereal_longitude": 30.0, "speed": 1.0},
    ]


def _fake_chart_for_vargas() -> chart.KundaliChart:
    return {
        "lagna": _fake_lagna(),
        "planets": [
            {
                "planet": "sun",
                "sidereal_longitude": 270.0,
            },
            {
                "planet": "moon",
                "sidereal_longitude": 30.5,
            },
        ],
        "houses": [],
    }
