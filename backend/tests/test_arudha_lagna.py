"""Tests for Arudha Lagna foundation helper."""

from __future__ import annotations

import json

from backend.app.kundali.arudha_lagna import calculate_arudha_lagna


def test_arudha_lagna_normal_calculation() -> None:
    result = calculate_arudha_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=2, lord="venus", lord_house=3)
    )

    assert result["arudha_lagna"] == 5
    assert result["arudha_rashi"]["english"] == "Virgo"
    assert result["lagna_rashi"]["english"] == "Taurus"
    assert result["lagna_lord"] == "venus"
    assert result["lagna_lord_house"] == 3
    assert result["metadata"]["calculation_status"] == "calculated"
    assert result["metadata"]["exception_applied"] is False
    assert [step["step"] for step in result["calculation_steps"]] == [
        "lagna_rashi",
        "lagna_lord",
        "lagna_lord_house",
        "initial_arudha_lagna",
        "exception_applied",
        "final_arudha_lagna",
    ]


def test_arudha_lagna_exception_when_arudha_falls_in_lagna() -> None:
    result = calculate_arudha_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=1, lord="mars", lord_house=1)
    )

    assert result["arudha_lagna"] == 10
    assert result["arudha_rashi"]["english"] == "Capricorn"
    assert result["metadata"]["exception_applied"] is True
    assert result["calculation_steps"][3]["value"] == 1
    assert result["calculation_steps"][-1]["value"] == 10


def test_arudha_lagna_exception_when_arudha_falls_in_seventh_from_lagna() -> None:
    result = calculate_arudha_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=1, lord="mars", lord_house=4)
    )

    assert result["arudha_lagna"] == 4
    assert result["arudha_rashi"]["english"] == "Cancer"
    assert result["metadata"]["exception_applied"] is True
    assert result["calculation_steps"][3]["value"] == 7
    assert result["calculation_steps"][-1]["value"] == 4


def test_arudha_lagna_missing_lagna_is_handled_safely() -> None:
    result = calculate_arudha_lagna({"planets": [{"planet": "mars", "house_number": 1}]})

    assert result["arudha_lagna"] is None
    assert result["arudha_rashi"] is None
    assert result["lagna_rashi"] is None
    assert result["lagna_lord"] is None
    assert result["lagna_lord_house"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["lagna_rashi"]
    json.dumps(result)


def test_arudha_lagna_missing_lagna_lord_placement_is_handled_safely() -> None:
    result = calculate_arudha_lagna(
        {
            "lagna": {"rashi_index": 1},
            "planets": [{"planet": "venus", "house_number": 2}],
        }
    )

    assert result["arudha_lagna"] is None
    assert result["arudha_rashi"] is None
    assert result["lagna_rashi"]["english"] == "Aries"
    assert result["lagna_lord"] == "mars"
    assert result["lagna_lord_house"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["lagna_lord_house"]
    json.dumps(result)


def test_arudha_lagna_output_is_json_safe() -> None:
    result = calculate_arudha_lagna(
        _chart_with_lagna_and_lord(lagna_rashi_index=4, lord="moon", lord_house=2)
    )

    assert {
        "arudha_lagna",
        "arudha_rashi",
        "lagna_rashi",
        "lagna_lord",
        "lagna_lord_house",
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
