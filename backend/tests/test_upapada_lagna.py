"""Tests for Upapada Lagna foundation helper."""

from __future__ import annotations

import json

from backend.app.kundali.upapada_lagna import calculate_upapada_lagna


def test_upapada_lagna_normal_calculation() -> None:
    result = calculate_upapada_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=1, lord="jupiter", lord_house=2)
    )

    assert result["upapada_lagna"] == 4
    assert result["upapada_rashi"]["english"] == "Cancer"
    assert result["source_house"] == 12
    assert result["source_rashi"]["english"] == "Pisces"
    assert result["source_lord"] == "jupiter"
    assert result["source_lord_house"] == 2
    assert result["metadata"]["calculation_status"] == "calculated"
    assert result["metadata"]["exception_applied"] is False
    assert [step["step"] for step in result["calculation_steps"]] == [
        "source_house",
        "source_rashi",
        "source_lord",
        "source_lord_house",
        "distance_from_source",
        "initial_upapada_lagna",
        "exception_applied",
        "final_upapada_lagna",
    ]


def test_upapada_lagna_exception_when_result_falls_in_source_house() -> None:
    result = calculate_upapada_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=1, lord="jupiter", lord_house=12)
    )

    assert result["upapada_lagna"] == 9
    assert result["upapada_rashi"]["english"] == "Sagittarius"
    assert result["metadata"]["exception_applied"] is True
    assert result["calculation_steps"][5]["value"] == 12
    assert result["calculation_steps"][-1]["value"] == 9


def test_upapada_lagna_exception_when_result_falls_in_seventh_from_source() -> None:
    result = calculate_upapada_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=1, lord="jupiter", lord_house=3)
    )

    assert result["upapada_lagna"] == 3
    assert result["upapada_rashi"]["english"] == "Gemini"
    assert result["metadata"]["exception_applied"] is True
    assert result["calculation_steps"][5]["value"] == 6
    assert result["calculation_steps"][-1]["value"] == 3


def test_upapada_lagna_missing_lagna_is_handled_safely() -> None:
    result = calculate_upapada_lagna(
        {"planets": [{"planet": "jupiter", "house_number": 2}]}
    )

    assert result["upapada_lagna"] is None
    assert result["upapada_rashi"] is None
    assert result["source_house"] == 12
    assert result["source_rashi"] is None
    assert result["source_lord"] is None
    assert result["source_lord_house"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["lagna_rashi"]
    json.dumps(result)


def test_upapada_lagna_missing_twelfth_lord_placement_is_handled_safely() -> None:
    result = calculate_upapada_lagna(
        {
            "lagna": {"rashi_index": 1},
            "planets": [{"planet": "venus", "house_number": 2}],
        }
    )

    assert result["upapada_lagna"] is None
    assert result["upapada_rashi"] is None
    assert result["source_house"] == 12
    assert result["source_rashi"]["english"] == "Pisces"
    assert result["source_lord"] == "jupiter"
    assert result["source_lord_house"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["source_lord_house"]
    json.dumps(result)


def test_upapada_lagna_output_is_json_safe() -> None:
    result = calculate_upapada_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=2, lord="mars", lord_house=4)
    )

    assert {
        "upapada_lagna",
        "upapada_rashi",
        "source_house",
        "source_rashi",
        "source_lord",
        "source_lord_house",
        "calculation_steps",
        "metadata",
    } <= set(result)
    json.dumps(result)


def _chart_with_lagna_and_lord(
    *,
    lagna_rashi_index: int,
    lord: str,
    lord_house: int,
) -> dict[str, object]:
    return {
        "lagna": {"rashi_index": lagna_rashi_index},
        "planets": [{"planet": lord, "house_number": lord_house}],
    }
