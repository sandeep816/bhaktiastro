"""Tests for Bhava Madhya / house cusp foundation helper."""

from __future__ import annotations

import json

from backend.app.kundali.bhava_cusps import calculate_bhava_cusps


def test_bhava_cusps_returns_twelve_house_cusps() -> None:
    result = calculate_bhava_cusps(15.0)

    assert result["house_system"] == "equal_foundation"
    assert len(result["house_cusps"]) == 12
    assert [cusp["house_number"] for cusp in result["house_cusps"]] == list(
        range(1, 13)
    )
    assert result["metadata"]["calculation_status"] == "calculated"


def test_bhava_cusp_house_one_equals_lagna_longitude() -> None:
    result = calculate_bhava_cusps(42.5)

    assert result["house_cusps"][0]["house_number"] == 1
    assert result["house_cusps"][0]["cusp_longitude"] == 42.5
    assert result["metadata"]["lagna_longitude"] == 42.5


def test_bhava_cusps_advance_by_thirty_degrees() -> None:
    result = calculate_bhava_cusps(10.0)

    assert [cusp["cusp_longitude"] for cusp in result["house_cusps"][:4]] == [
        10.0,
        40.0,
        70.0,
        100.0,
    ]
    assert result["house_cusps"][11]["cusp_longitude"] == 340.0
    assert result["metadata"]["house_span_degrees"] == 30.0


def test_bhava_cusp_wrap_around_works() -> None:
    result = calculate_bhava_cusps(350.0)

    assert [cusp["cusp_longitude"] for cusp in result["house_cusps"][:4]] == [
        350.0,
        20.0,
        50.0,
        80.0,
    ]
    assert result["house_cusps"][1]["rashi"]["english"] == "Aries"


def test_bhava_cusp_rashi_metadata_exists() -> None:
    result = calculate_bhava_cusps(35.25)
    first_cusp = result["house_cusps"][0]

    assert first_cusp["rashi"]["english"] == "Taurus"
    assert first_cusp["rashi_index"] == 2
    assert first_cusp["rashi_degree"] == 5.25


def test_bhava_cusp_invalid_longitude_is_handled_safely() -> None:
    result = calculate_bhava_cusps(float("nan"))

    assert result["house_cusps"] == []
    assert result["house_system"] == "equal_foundation"
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["lagna_longitude"]
    assert result["metadata"]["lagna_longitude"] is None
    json.dumps(result)


def test_bhava_cusp_longitude_above_360_is_normalized() -> None:
    result = calculate_bhava_cusps(725.0)

    assert result["house_cusps"][0]["cusp_longitude"] == 5.0
    assert result["house_cusps"][1]["cusp_longitude"] == 35.0
    assert result["metadata"]["lagna_longitude"] == 5.0


def test_bhava_cusp_output_is_json_safe() -> None:
    result = calculate_bhava_cusps(100.0)

    assert {
        "house_cusps",
        "house_system",
        "metadata",
    } <= set(result)
    assert {
        "house_number",
        "cusp_longitude",
        "rashi",
        "rashi_index",
        "rashi_degree",
    } <= set(result["house_cusps"][0])
    json.dumps(result)
