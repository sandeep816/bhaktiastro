"""Tests for Special Lagna Summary builder."""

from __future__ import annotations

from datetime import datetime
import json

from backend.app.kundali.special_lagna_summary import build_special_lagna_summary


def test_special_lagna_summary_contains_arudha_lagna() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert "arudha_lagna" in result
    assert result["arudha_lagna"]["metadata"]["component"] == "arudha_lagna"
    assert result["arudha_lagna"]["metadata"]["calculation_status"] == "calculated"


def test_special_lagna_summary_contains_upapada_lagna() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert "upapada_lagna" in result
    assert result["upapada_lagna"]["metadata"]["component"] == "upapada_lagna"
    assert result["upapada_lagna"]["metadata"]["calculation_status"] == "calculated"


def test_special_lagna_summary_contains_hora_lagna_result() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert "hora_lagna" in result
    assert result["hora_lagna"]["metadata"]["component"] == "hora_lagna"
    assert result["hora_lagna"]["metadata"]["calculation_status"] == "calculated"
    assert result["hora_lagna"]["hora_lagna_longitude"] == 40.0


def test_special_lagna_summary_contains_ghati_lagna_result() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert "ghati_lagna" in result
    assert result["ghati_lagna"]["metadata"]["component"] == "ghati_lagna"
    assert result["ghati_lagna"]["metadata"]["calculation_status"] == "calculated"
    assert result["ghati_lagna"]["ghati_lagna_longitude"] == 40.0


def test_special_lagna_summary_contains_bhava_cusps() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert "bhava_cusps" in result
    assert result["bhava_cusps"]["house_system"] == "equal_foundation"
    assert len(result["bhava_cusps"]["house_cusps"]) == 12
    assert result["bhava_cusps"]["house_cusps"][0]["cusp_longitude"] == 10.0


def test_special_lagna_summary_missing_context_is_handled_safely() -> None:
    result = build_special_lagna_summary(_sample_chart())

    assert result["metadata"]["context_available"] is False
    assert result["metadata"]["birth_datetime_available"] is False
    assert result["metadata"]["sunrise_datetime_available"] is False
    assert result["hora_lagna"]["metadata"]["calculation_status"] == "missing_data"
    assert result["hora_lagna"]["metadata"]["missing_fields"] == ["birth_datetime"]
    assert result["ghati_lagna"]["metadata"]["calculation_status"] == "missing_data"
    assert result["ghati_lagna"]["metadata"]["missing_fields"] == ["birth_datetime"]
    assert result["bhava_cusps"]["metadata"]["calculation_status"] == "calculated"
    json.dumps(result)


def test_special_lagna_summary_missing_lagna_is_handled_safely() -> None:
    result = build_special_lagna_summary({"planets": []}, _sample_context())

    assert result["metadata"]["lagna_longitude_available"] is False
    assert result["arudha_lagna"]["metadata"]["calculation_status"] == "missing_data"
    assert result["upapada_lagna"]["metadata"]["calculation_status"] == "missing_data"
    assert result["hora_lagna"]["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert result["ghati_lagna"]["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert result["bhava_cusps"]["metadata"]["missing_fields"] == ["lagna_longitude"]
    json.dumps(result)


def test_special_lagna_summary_output_is_json_safe() -> None:
    result = build_special_lagna_summary(_sample_chart(), _sample_context())

    assert {
        "arudha_lagna",
        "upapada_lagna",
        "hora_lagna",
        "ghati_lagna",
        "bhava_cusps",
        "metadata",
    } <= set(result)
    assert result["metadata"]["components"] == [
        "arudha_lagna",
        "upapada_lagna",
        "hora_lagna",
        "ghati_lagna",
        "bhava_cusps",
    ]
    json.dumps(result)


def _sample_chart() -> dict[str, object]:
    return {
        "lagna": {
            "rashi_index": 1,
            "sidereal_longitude": 10.0,
        },
        "planets": [
            {"planet": "mars", "house_number": 2},
            {"planet": "jupiter", "house_number": 2},
        ],
    }


def _sample_context() -> dict[str, datetime]:
    return {
        "birth_datetime": datetime(2026, 1, 1, 8, 0, 0),
        "sunrise_datetime": datetime(2026, 1, 1, 6, 0, 0),
    }
