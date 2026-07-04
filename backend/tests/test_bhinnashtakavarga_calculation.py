"""Tests for Bhinnashtakavarga calculation foundation."""

from __future__ import annotations

import json

from backend.app.ashtakavarga.bhinnashtakavarga import BAV_SOURCES
from backend.app.ashtakavarga.bhinnashtakavarga_calculation import (
    calculate_bhinnashtakavarga,
)
from backend.app.ashtakavarga.constants import ASHTAKAVARGA_HOUSES


def test_bav_calculation_returns_twelve_houses() -> None:
    result = calculate_bhinnashtakavarga("sun", _complete_chart())

    assert result["target_planet"] == "sun"
    assert set(result["houses"]) == set(ASHTAKAVARGA_HOUSES)
    assert len(result["houses"]) == 12
    assert result["metadata"]["calculation_status"] == "calculated"
    json.dumps(result)


def test_bav_total_bindus_equals_sum_of_houses() -> None:
    result = calculate_bhinnashtakavarga("sun", _complete_chart())

    assert result["total_bindus"] == sum(result["houses"].values())
    assert result["total_bindus"] == sum(
        contribution["bindus"]
        for contribution in result["source_contributions"].values()
    )


def test_bav_source_contributions_are_recorded() -> None:
    result = calculate_bhinnashtakavarga("sun", _complete_chart())

    assert set(result["source_contributions"]) == set(BAV_SOURCES)
    sun_contribution = result["source_contributions"]["sun"]
    assert sun_contribution == {
        "source": "sun",
        "source_house": 1,
        "contributing_offsets": [1, 2, 4, 7, 8, 9, 10, 11],
        "contributed_houses": [1, 2, 4, 7, 8, 9, 10, 11],
        "bindus": 8,
    }
    lagna_contribution = result["source_contributions"]["lagna"]
    assert lagna_contribution["source_house"] == 1
    assert lagna_contribution["contributed_houses"] == [3, 4, 6, 10, 11, 12]


def test_bav_wraps_contributed_houses_from_source_house() -> None:
    chart_data = _complete_chart()
    chart_data["planets"][0]["house_number"] = 12

    result = calculate_bhinnashtakavarga("sun", chart_data)

    assert result["source_contributions"]["sun"]["source_house"] == 12
    assert result["source_contributions"]["sun"]["contributed_houses"] == [
        12,
        1,
        3,
        6,
        7,
        8,
        9,
        10,
    ]


def test_bav_missing_source_data_is_handled_safely() -> None:
    chart_data = {
        "lagna": {},
        "planets": [
            {"planet": "sun", "house_number": 1},
            {"planet": "moon", "house_number": 2},
        ],
    }

    result = calculate_bhinnashtakavarga("moon", chart_data)

    assert set(result["source_contributions"]) == {"sun", "moon", "lagna"}
    assert result["metadata"]["missing_sources"] == [
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    ]
    assert result["total_bindus"] == sum(result["houses"].values())
    json.dumps(result)


def test_bav_missing_chart_data_is_handled_safely() -> None:
    result = calculate_bhinnashtakavarga("sun", {})

    assert result["source_contributions"] == {}
    assert result["total_bindus"] == 0
    assert result["metadata"]["missing_sources"] == list(BAV_SOURCES)
    assert result["metadata"]["chart_data_available"] is True
    json.dumps(result)


def test_bav_unsupported_target_planet_is_handled_safely() -> None:
    result = calculate_bhinnashtakavarga("rahu", _complete_chart())

    assert result == {
        "target_planet": "rahu",
        "houses": {house_number: 0 for house_number in ASHTAKAVARGA_HOUSES},
        "total_bindus": 0,
        "source_contributions": {},
        "metadata": {
            "calculation_status": "unsupported",
            "formula_status": "foundation",
            "supported_target_planet": False,
            "chart_data_available": True,
            "missing_sources": [],
        },
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
