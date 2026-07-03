"""Validation and regression coverage for Planet Strength foundations."""

from __future__ import annotations

import json
from numbers import Real
from typing import Any

import pytest
from pydantic import ValidationError

from backend.app.api.v1.kundali import get_kundali
from backend.app.schemas.kundali import KundaliRequest
from backend.app.strength.ishta_kashta_bala import calculate_ishta_kashta_bala
from backend.app.strength.shadbala import calculate_shadbala
from backend.app.strength.summary import build_planet_strength_summary


def test_invalid_planet_name_is_handled_safely() -> None:
    result = calculate_shadbala(
        {
            "planet": "pluto",
            "rashi": "Mesha",
            "house_number": 10,
            "received_aspects": [{"from_planet": "jupiter"}],
        }
    )
    ishta_kashta = calculate_ishta_kashta_bala("pluto", result)

    assert result["planet"] == "pluto"
    assert result["status"] == "weak"
    assert result["strength_percentage"] == 0.0
    assert result["components"]["sthana_bala"]["status"] == "invalid_input"
    assert result["components"]["dig_bala"]["status"] == "invalid_input"
    assert result["components"]["naisargika_bala"]["status"] == "unsupported"
    assert result["components"]["drik_bala"]["status"] == "unsupported"
    assert ishta_kashta["status"] == "unsupported"
    assert ishta_kashta["ishta_score"] == 0.0
    assert ishta_kashta["kashta_score"] == 0.0
    _assert_json_safe(result)
    _assert_json_safe(ishta_kashta)


def test_invalid_rashi_name_and_house_number_are_handled_safely() -> None:
    result = calculate_shadbala(
        {
            "planet": "sun",
            "rashi": "not-a-rashi",
            "house_number": 13,
        }
    )

    assert result["components"]["sthana_bala"]["status"] == "invalid_input"
    assert result["components"]["dig_bala"]["status"] == "invalid_input"
    _assert_required_shadbala_shape(result)
    _assert_percentage(result["strength_percentage"])
    _assert_json_safe(result)


def test_missing_planet_data_is_handled_safely() -> None:
    result = calculate_shadbala({})

    assert result["planet"] == ""
    assert result["status"] == "weak"
    assert result["strength_percentage"] == 0.0
    assert result["components"]["sthana_bala"]["status"] == "invalid_input"
    assert result["components"]["dig_bala"]["status"] == "invalid_input"
    _assert_required_shadbala_shape(result)
    _assert_json_safe(result)


def test_missing_chart_data_is_handled_safely() -> None:
    empty_summary = build_planet_strength_summary({})
    partial_summary = build_planet_strength_summary({"planets": [{}, "bad-entry"]})

    assert empty_summary["planets"] == []
    assert empty_summary["ranking"] == []
    assert empty_summary["strongest_planet"] is None
    assert empty_summary["weakest_planet"] is None
    assert partial_summary["metadata"]["source_planet_count"] == 2
    assert partial_summary["metadata"]["planet_count"] == 1
    assert partial_summary["metadata"]["skipped_entries"] == 1
    assert partial_summary["planets"][0]["summary_status"] == "unsupported"
    _assert_json_safe(empty_summary)
    _assert_json_safe(partial_summary)


@pytest.mark.parametrize("planet", ["rahu", "ketu"])
def test_unsupported_rahu_ketu_are_handled_safely(planet: str) -> None:
    result = calculate_shadbala(
        {
            "planet": planet,
            "rashi": "Mesha",
            "house_number": 1,
            "motion_status": "retrograde",
            "received_aspects": [{"from_planet": "jupiter"}],
        }
    )
    ishta_kashta = calculate_ishta_kashta_bala(planet, result)

    assert result["components"]["naisargika_bala"]["status"] == "unsupported"
    assert result["components"]["drik_bala"]["status"] == "unsupported"
    assert result["components"]["chesta_bala"]["status"] == "unsupported"
    assert ishta_kashta["status"] == "unsupported"
    _assert_required_shadbala_shape(result)
    _assert_json_safe(result)
    _assert_json_safe(ishta_kashta)


def test_shadbala_output_is_json_safe_and_structural() -> None:
    result = calculate_shadbala(
        {
            "planet": "sun",
            "rashi": "Mesha",
            "house_number": 10,
            "received_aspects": [{"from_planet": "jupiter"}],
        }
    )

    _assert_required_shadbala_shape(result)
    assert set(result["components"]) == {
        "sthana_bala",
        "dig_bala",
        "kala_bala",
        "chesta_bala",
        "naisargika_bala",
        "drik_bala",
    }
    _assert_numeric(result["total_strength"])
    _assert_numeric(result["max_strength"])
    _assert_percentage(result["strength_percentage"])
    for component in result["components"].values():
        assert {"component", "status", "score", "max_score", "reason"} <= set(
            component
        )
        assert component["score"] is None or _is_number(component["score"])
        _assert_numeric(component["max_score"])
    _assert_json_safe(result)


def test_ishta_kashta_output_is_json_safe_and_structural() -> None:
    result = calculate_ishta_kashta_bala(
        "sun",
        {"strength_percentage": 72.5, "status": "strong"},
        dignity_status="exalted",
    )

    assert {
        "planet",
        "ishta_score",
        "kashta_score",
        "total",
        "status",
        "reason",
        "metadata",
    } <= set(result)
    _assert_percentage(result["ishta_score"])
    _assert_percentage(result["kashta_score"])
    _assert_numeric(result["total"])
    assert result["status"] == "favorable"
    _assert_json_safe(result)


def test_planet_strength_summary_output_is_json_safe_and_sorted() -> None:
    result = build_planet_strength_summary(_sample_strength_chart())

    assert {"planets", "ranking", "strongest_planet", "weakest_planet", "metadata"} <= set(
        result
    )
    assert len(result["planets"]) == 4
    assert len(result["ranking"]) == 4
    strengths = [entry["strength_percentage"] for entry in result["ranking"]]
    assert strengths == sorted(strengths, reverse=True)
    assert [entry["planet"] for entry in result["ranking"][-2:]] == ["rahu", "ketu"]
    for entry in result["ranking"]:
        _assert_percentage(entry["strength_percentage"])
        _assert_numeric(entry["total_strength"])
    _assert_json_safe(result)


def test_kundali_api_with_include_strength_is_json_safe() -> None:
    response = get_kundali(_jaipur_request(include_strength=True))
    data = response.model_dump(mode="json")

    assert "strength" in data
    assert {"planets", "ranking", "strongest_planet", "weakest_planet", "metadata"} <= set(
        data["strength"]
    )
    assert len(data["strength"]["planets"]) == 9
    strengths = [
        entry["strength_percentage"] for entry in data["strength"]["ranking"]
    ]
    assert strengths == sorted(strengths, reverse=True)
    for entry in data["strength"]["ranking"]:
        _assert_percentage(entry["strength_percentage"])
    _assert_json_safe(data)


def test_kundali_api_without_include_strength_remains_backward_compatible() -> None:
    response = get_kundali(_jaipur_request())
    data = response.model_dump(mode="json")

    assert set(data) == {"lagna", "planets", "houses"}
    assert "strength" not in data
    assert "vargas" not in data
    _assert_json_safe(data)


def test_invalid_kundali_request_still_returns_validation_error() -> None:
    with pytest.raises(ValidationError):
        _jaipur_request(latitude=91.0, include_strength=True)


def _sample_strength_chart() -> dict[str, list[dict[str, Any]]]:
    return {
        "planets": [
            {
                "planet": "sun",
                "rashi": {"sanskrit": "Mesha", "english": "Aries", "index": 1},
                "house_number": 10,
                "aspects": {"aspected_houses": [4]},
            },
            {
                "planet": "venus",
                "rashi": {"sanskrit": "Vrishabha", "english": "Taurus", "index": 2},
                "house_number": 4,
                "motion_status": "direct",
                "aspects": {"aspected_houses": [10]},
            },
            {
                "planet": "rahu",
                "rashi": {"sanskrit": "Mesha", "english": "Aries", "index": 1},
                "house_number": 1,
            },
            {
                "planet": "ketu",
                "rashi": {"sanskrit": "Tula", "english": "Libra", "index": 7},
                "house_number": 7,
            },
        ]
    }


def _jaipur_request(
    *,
    latitude: float = 26.9124,
    include_strength: bool = False,
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
        include_strength=include_strength,
    )


def _assert_required_shadbala_shape(result: dict[str, Any]) -> None:
    assert {
        "planet",
        "total_strength",
        "max_strength",
        "strength_percentage",
        "components",
        "status",
        "metadata",
    } <= set(result)
    assert len(result["components"]) == 6


def _assert_json_safe(value: object) -> None:
    json.dumps(value)


def _assert_numeric(value: object) -> None:
    assert _is_number(value)


def _assert_percentage(value: object) -> None:
    _assert_numeric(value)
    assert 0.0 <= float(value) <= 100.0


def _is_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)
