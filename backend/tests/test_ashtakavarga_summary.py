"""Tests for Ashtakavarga summary builder."""

from __future__ import annotations

import json

from backend.app.ashtakavarga.constants import ASHTAKAVARGA_HOUSES, ASHTAKAVARGA_PLANETS
from backend.app.ashtakavarga.summary import build_ashtakavarga_summary


def test_summary_contains_sarvashtakavarga() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    assert "sarvashtakavarga" in result
    assert set(result["sarvashtakavarga"]["houses"]) == set(ASHTAKAVARGA_HOUSES)
    assert result["sarvashtakavarga"]["total_bindus"] == sum(
        result["sarvashtakavarga"]["houses"].values()
    )


def test_summary_contains_bhinnashtakavarga() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    assert set(result["bhinnashtakavarga"]) == set(ASHTAKAVARGA_PLANETS)
    assert result["bhinnashtakavarga"] == result["sarvashtakavarga"]["bhinnashtakavarga"]


def test_summary_strongest_house_exists() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    strongest_house = result["strongest_house"]
    assert strongest_house is not None
    assert strongest_house == result["house_ranking"][0]
    assert strongest_house["house_number"] in ASHTAKAVARGA_HOUSES


def test_summary_weakest_house_exists() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    weakest_house = result["weakest_house"]
    assert weakest_house is not None
    assert weakest_house == result["house_ranking"][-1]
    assert weakest_house["house_number"] in ASHTAKAVARGA_HOUSES


def test_summary_house_ranking_is_sorted_by_bindus_descending() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    ranking = result["house_ranking"]
    assert len(ranking) == 12
    assert [entry["bindus"] for entry in ranking] == sorted(
        [entry["bindus"] for entry in ranking],
        reverse=True,
    )


def test_summary_missing_chart_data_is_handled_safely() -> None:
    result = build_ashtakavarga_summary({})

    assert result["sarvashtakavarga"]["total_bindus"] == 0
    assert result["strongest_house"] == {"house_number": 1, "bindus": 0}
    assert result["weakest_house"] == {"house_number": 12, "bindus": 0}
    assert result["metadata"]["chart_data_available"] is True


def test_summary_output_is_json_safe() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    assert result["metadata"] == {
        "calculation_status": "foundation",
        "ranking_basis": "sarvashtakavarga.house_bindus",
        "house_count": 12,
        "planet_count": 7,
        "chart_data_available": True,
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
