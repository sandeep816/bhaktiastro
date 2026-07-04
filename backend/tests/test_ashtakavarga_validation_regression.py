"""Validation and regression coverage for Ashtakavarga foundations."""

from __future__ import annotations

import json
from numbers import Real
from typing import Any

import pytest
from pydantic import ValidationError

from backend.app.api.v1.kundali import get_kundali
from backend.app.ashtakavarga.bhinnashtakavarga import (
    BAV_SOURCES,
    get_contributing_houses,
    is_valid_bav_source,
)
from backend.app.ashtakavarga.bhinnashtakavarga_calculation import (
    calculate_bhinnashtakavarga,
)
from backend.app.ashtakavarga.constants import ASHTAKAVARGA_HOUSES, ASHTAKAVARGA_PLANETS
from backend.app.ashtakavarga.sarvashtakavarga import calculate_sarvashtakavarga
from backend.app.ashtakavarga.summary import build_ashtakavarga_summary
from backend.app.schemas.kundali import KundaliRequest


@pytest.mark.parametrize("planet", ["pluto", "", "rahu", "ketu"])
def test_invalid_and_unsupported_planet_names_are_handled_safely(
    planet: str,
) -> None:
    result = calculate_bhinnashtakavarga(planet, _complete_chart())

    assert result["target_planet"] == planet
    assert result["metadata"]["calculation_status"] == "unsupported"
    assert result["metadata"]["supported_target_planet"] is False
    assert result["source_contributions"] == {}
    assert result["total_bindus"] == 0
    _assert_bav_shape(result)
    _assert_json_safe(result)


def test_invalid_house_numbers_are_handled_safely() -> None:
    result = calculate_bhinnashtakavarga(
        "sun",
        {
            "lagna": {"house_number": "bad-house"},
            "planets": [
                {"planet": "sun", "house_number": "1"},
                {"planet": "moon", "house_number": True},
                {"planet": "mars", "house_number": 13},
            ],
        },
    )

    assert set(result["source_contributions"]) == {"mars", "lagna"}
    assert result["source_contributions"]["mars"]["source_house"] == 1
    assert result["source_contributions"]["lagna"]["source_house"] == 1
    assert result["metadata"]["missing_sources"] == [
        "sun",
        "moon",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    ]
    _assert_bav_shape(result)
    _assert_json_safe(result)


def test_missing_chart_data_is_handled_safely() -> None:
    bav = calculate_bhinnashtakavarga("sun", None)  # type: ignore[arg-type]
    sav = calculate_sarvashtakavarga(None)  # type: ignore[arg-type]
    summary = build_ashtakavarga_summary(None)  # type: ignore[arg-type]

    assert bav["metadata"]["chart_data_available"] is False
    assert bav["metadata"]["missing_sources"] == list(BAV_SOURCES)
    assert sav["metadata"]["chart_data_available"] is False
    assert summary["metadata"]["chart_data_available"] is False
    _assert_bav_shape(bav)
    _assert_sav_shape(sav)
    _assert_summary_shape(summary)


def test_missing_planet_house_placement_is_recorded_safely() -> None:
    result = calculate_bhinnashtakavarga(
        "moon",
        {
            "lagna": {},
            "planets": [
                {"planet": "sun"},
                {"planet": "moon", "house_number": 2},
                {"planet": "mars", "house_number": None},
            ],
        },
    )

    assert set(result["source_contributions"]) == {"moon", "lagna"}
    assert result["metadata"]["missing_sources"] == [
        "sun",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    ]
    _assert_bav_shape(result)
    _assert_json_safe(result)


def test_unsupported_bav_source_is_handled_safely() -> None:
    assert is_valid_bav_source("rahu") is False
    assert is_valid_bav_source("ketu") is False
    assert is_valid_bav_source("not-a-source") is False
    assert get_contributing_houses("sun", "rahu") == []
    assert get_contributing_houses("sun", "ketu") == []
    assert get_contributing_houses("sun", "not-a-source") == []


def test_bhinnashtakavarga_output_is_json_safe_and_structural() -> None:
    result = calculate_bhinnashtakavarga("sun", _complete_chart())

    _assert_bav_shape(result)
    assert set(result["source_contributions"]) == set(BAV_SOURCES)
    for contribution in result["source_contributions"].values():
        assert {
            "source",
            "source_house",
            "contributing_offsets",
            "contributed_houses",
            "bindus",
        } <= set(contribution)
        _assert_numeric(contribution["bindus"])
        assert contribution["bindus"] == len(contribution["contributed_houses"])
        assert all(
            house_number in ASHTAKAVARGA_HOUSES
            for house_number in contribution["contributed_houses"]
        )
    _assert_json_safe(result)


def test_sarvashtakavarga_output_is_json_safe_and_structural() -> None:
    result = calculate_sarvashtakavarga(_complete_chart())

    _assert_sav_shape(result)
    assert set(result["planet_totals"]) == set(ASHTAKAVARGA_PLANETS)
    assert set(result["bhinnashtakavarga"]) == set(ASHTAKAVARGA_PLANETS)
    assert result["total_bindus"] == sum(result["planet_totals"].values())
    for planet, bav_result in result["bhinnashtakavarga"].items():
        assert result["planet_totals"][planet] == bav_result["total_bindus"]
        _assert_bav_shape(bav_result)
    _assert_json_safe(result)


def test_ashtakavarga_summary_output_is_json_safe_and_sorted() -> None:
    result = build_ashtakavarga_summary(_complete_chart())

    _assert_summary_shape(result)
    bindus = [entry["bindus"] for entry in result["house_ranking"]]
    assert bindus == sorted(bindus, reverse=True)
    assert result["strongest_house"] == result["house_ranking"][0]
    assert result["weakest_house"] == result["house_ranking"][-1]
    for previous, current in zip(result["house_ranking"], result["house_ranking"][1:]):
        if previous["bindus"] == current["bindus"]:
            assert previous["house_number"] < current["house_number"]
    _assert_json_safe(result)


def test_kundali_api_with_include_ashtakavarga_is_json_safe() -> None:
    response = get_kundali(_jaipur_request(include_ashtakavarga=True))
    data = response.model_dump(mode="json")

    assert "ashtakavarga" in data
    _assert_summary_shape(data["ashtakavarga"], json_mode=True)
    _assert_json_safe(data)


def test_kundali_api_without_include_ashtakavarga_remains_backward_compatible() -> None:
    response = get_kundali(_jaipur_request())
    data = response.model_dump(mode="json")

    assert set(data) == {"lagna", "planets", "houses"}
    assert "ashtakavarga" not in data
    assert "strength" not in data
    assert "vargas" not in data
    _assert_json_safe(data)


def test_invalid_kundali_request_still_returns_validation_error() -> None:
    with pytest.raises(ValidationError):
        _jaipur_request(latitude=91.0, include_ashtakavarga=True)


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


def _jaipur_request(
    *,
    latitude: float = 26.9124,
    include_ashtakavarga: bool = False,
) -> KundaliRequest:
    return KundaliRequest(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        second=0,
        timezone_offset=5.5,
        latitude=latitude,
        longitude=75.7873,
        ayanamsa="lahiri",
        include_ashtakavarga=include_ashtakavarga,
    )


def _assert_bav_shape(result: dict[str, Any]) -> None:
    assert {
        "target_planet",
        "houses",
        "total_bindus",
        "source_contributions",
        "metadata",
    } <= set(result)
    _assert_houses(result["houses"])
    _assert_numeric(result["total_bindus"])
    assert result["total_bindus"] == sum(result["houses"].values())


def _assert_sav_shape(
    result: dict[str, Any],
    *,
    json_mode: bool = False,
) -> None:
    assert {
        "houses",
        "total_bindus",
        "planet_totals",
        "bhinnashtakavarga",
        "metadata",
    } <= set(result)
    _assert_houses(result["houses"], json_mode=json_mode)
    _assert_numeric(result["total_bindus"])
    assert result["total_bindus"] == sum(result["houses"].values())


def _assert_summary_shape(
    result: dict[str, Any],
    *,
    json_mode: bool = False,
) -> None:
    assert {
        "sarvashtakavarga",
        "bhinnashtakavarga",
        "strongest_house",
        "weakest_house",
        "house_ranking",
        "metadata",
    } <= set(result)
    _assert_sav_shape(result["sarvashtakavarga"], json_mode=json_mode)
    assert len(result["bhinnashtakavarga"]) == len(ASHTAKAVARGA_PLANETS)
    assert len(result["house_ranking"]) == 12
    for entry in result["house_ranking"]:
        assert {"house_number", "bindus"} <= set(entry)
        assert entry["house_number"] in ASHTAKAVARGA_HOUSES
        _assert_numeric(entry["bindus"])
    if not json_mode:
        assert result["bhinnashtakavarga"] == result["sarvashtakavarga"][
            "bhinnashtakavarga"
        ]


def _assert_houses(
    houses: dict[Any, Any],
    *,
    json_mode: bool = False,
) -> None:
    expected_houses = (
        {str(house_number) for house_number in ASHTAKAVARGA_HOUSES}
        if json_mode
        else set(ASHTAKAVARGA_HOUSES)
    )
    assert set(houses) == expected_houses
    assert len(houses) == 12
    for bindus in houses.values():
        _assert_numeric(bindus)


def _assert_json_safe(value: object) -> None:
    json.dumps(value)


def _assert_numeric(value: object) -> None:
    assert isinstance(value, Real) and not isinstance(value, bool)
