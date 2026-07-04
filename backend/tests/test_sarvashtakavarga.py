"""Tests for Sarvashtakavarga calculation foundation."""

from __future__ import annotations

import json

from backend.app.ashtakavarga.bhinnashtakavarga import BAV_SOURCES
from backend.app.ashtakavarga.constants import ASHTAKAVARGA_HOUSES, ASHTAKAVARGA_PLANETS
from backend.app.ashtakavarga.sarvashtakavarga import calculate_sarvashtakavarga


def test_sav_returns_twelve_houses() -> None:
    result = calculate_sarvashtakavarga(_complete_chart())

    assert set(result["houses"]) == set(ASHTAKAVARGA_HOUSES)
    assert len(result["houses"]) == 12
    assert result["metadata"]["calculation_status"] == "calculated"
    assert result["metadata"]["formula_status"] == "foundation"
    json.dumps(result)


def test_sav_total_bindus_equals_sum_of_houses() -> None:
    result = calculate_sarvashtakavarga(_complete_chart())

    assert result["total_bindus"] == sum(result["houses"].values())
    assert result["total_bindus"] == sum(result["planet_totals"].values())


def test_sav_planet_totals_exist() -> None:
    result = calculate_sarvashtakavarga(_complete_chart())

    assert set(result["planet_totals"]) == set(ASHTAKAVARGA_PLANETS)
    for planet, total in result["planet_totals"].items():
        assert isinstance(total, int)
        assert total == result["bhinnashtakavarga"][planet]["total_bindus"]


def test_sav_bhinnashtakavarga_results_exist() -> None:
    result = calculate_sarvashtakavarga(_complete_chart())

    assert set(result["bhinnashtakavarga"]) == set(ASHTAKAVARGA_PLANETS)
    for planet, bav_result in result["bhinnashtakavarga"].items():
        assert bav_result["target_planet"] == planet
        assert set(bav_result["houses"]) == set(ASHTAKAVARGA_HOUSES)
        assert bav_result["metadata"]["missing_sources"] == []


def test_sav_house_bindus_are_aggregated_from_bav_results() -> None:
    result = calculate_sarvashtakavarga(_complete_chart())

    for house_number in ASHTAKAVARGA_HOUSES:
        assert result["houses"][house_number] == sum(
            bav_result["houses"][house_number]
            for bav_result in result["bhinnashtakavarga"].values()
        )


def test_sav_missing_chart_data_is_handled_safely() -> None:
    result = calculate_sarvashtakavarga({})

    assert result["houses"] == {house_number: 0 for house_number in ASHTAKAVARGA_HOUSES}
    assert result["total_bindus"] == 0
    assert result["planet_totals"] == {planet: 0 for planet in ASHTAKAVARGA_PLANETS}
    assert set(result["bhinnashtakavarga"]) == set(ASHTAKAVARGA_PLANETS)
    assert result["metadata"]["missing_sources_by_planet"] == {
        planet: list(BAV_SOURCES) for planet in ASHTAKAVARGA_PLANETS
    }
    json.dumps(result)


def _complete_chart() -> dict[str, object]:
    return {
        "lagna": {},
        "planets": [
            {"planet": "sun", "house_number": 1},
            {"planet": "moon", "house_number": 2},
            {"planet": "mars", "house_number": 3},
            {"planet": "mercury", "house_number": 4},
            {"planet": "jupiter", "house_number": 5},
            {"planet": "venus", "house_number": 6},
            {"planet": "saturn", "house_number": 7},
        ],
    }
