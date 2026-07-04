"""Tests for Hora Lagna foundation helper."""

from __future__ import annotations

from datetime import datetime, timezone
import json

from backend.app.kundali.hora_lagna import calculate_hora_lagna


def test_hora_lagna_longitude_is_normalized() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=350.0,
        birth_datetime=datetime(2026, 1, 1, 8, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert result["hora_lagna_longitude"] == 20.0
    assert 0.0 <= result["hora_lagna_longitude"] < 360.0
    assert result["metadata"]["calculation_status"] == "calculated"


def test_hora_lagna_rashi_metadata_exists() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=10.0,
        birth_datetime=datetime(2026, 1, 1, 7, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert result["hora_lagna_longitude"] == 25.0
    assert result["rashi"]["english"] == "Aries"
    assert result["rashi_index"] == 1
    assert result["rashi_degree"] == 25.0


def test_hora_lagna_elapsed_time_is_calculated() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=100.0,
        birth_datetime=datetime(2026, 1, 1, 9, 30, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert result["elapsed_time"]["seconds"] == 12600.0
    assert result["elapsed_time"]["hours"] == 3.5
    assert result["calculation_steps"][1]["step"] == "elapsed_hours_from_sunrise"
    assert result["calculation_steps"][1]["value"] == 3.5
    assert result["calculation_steps"][2]["value"] == 52.5


def test_hora_lagna_missing_sunrise_is_handled_safely() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=100.0,
        birth_datetime=datetime(2026, 1, 1, 9, 0, 0),
        sunrise_datetime=None,
    )

    assert result["hora_lagna_longitude"] is None
    assert result["rashi"] is None
    assert result["rashi_index"] is None
    assert result["rashi_degree"] is None
    assert result["elapsed_time"]["birth_datetime"] == "2026-01-01T09:00:00"
    assert result["elapsed_time"]["sunrise_datetime"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["sunrise_datetime"]
    json.dumps(result)


def test_hora_lagna_longitude_above_360_is_handled_safely() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=725.0,
        birth_datetime=datetime(2026, 1, 1, 7, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert result["hora_lagna_longitude"] == 20.0
    assert result["rashi"]["english"] == "Aries"
    assert result["rashi_degree"] == 20.0


def test_hora_lagna_accepts_iso_datetime_strings() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=30.0,
        birth_datetime="2026-01-01T08:00:00+00:00",
        sunrise_datetime="2026-01-01T06:00:00+00:00",
    )

    assert result["hora_lagna_longitude"] == 60.0
    assert result["elapsed_time"]["birth_datetime"] == "2026-01-01T08:00:00+00:00"
    assert result["elapsed_time"]["sunrise_datetime"] == "2026-01-01T06:00:00+00:00"


def test_hora_lagna_mixed_timezone_inputs_are_handled_safely() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=30.0,
        birth_datetime=datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert result["hora_lagna_longitude"] is None
    assert result["metadata"]["calculation_status"] == "missing_data"
    assert result["metadata"]["missing_fields"] == ["datetime_timezone"]
    json.dumps(result)


def test_hora_lagna_output_is_json_safe() -> None:
    result = calculate_hora_lagna(
        lagna_longitude=100.0,
        birth_datetime=datetime(2026, 1, 1, 10, 0, 0),
        sunrise_datetime=datetime(2026, 1, 1, 6, 0, 0),
    )

    assert {
        "hora_lagna_longitude",
        "rashi",
        "rashi_index",
        "rashi_degree",
        "elapsed_time",
        "calculation_steps",
        "metadata",
    } <= set(result)
    json.dumps(result)
