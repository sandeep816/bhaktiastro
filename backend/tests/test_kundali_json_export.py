"""Tests for Kundali JSON export safety."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import pytest

from backend.app.api.v1.kundali import get_kundali
from backend.app.kundali import chart, json_export
from backend.app.schemas.kundali import KundaliRequest


def test_kundali_chart_can_be_serialized_to_json() -> None:
    chart_data = _jaipur_chart()
    exported = json_export.export_kundali_chart(chart_data)

    payload = json.dumps(exported, allow_nan=False)
    decoded = json.loads(payload)

    assert {"lagna", "planets", "houses", "metadata"}.issubset(decoded)
    assert decoded["metadata"]["engine"] == "kundali"
    assert len(decoded["planets"]) == 9
    assert len(decoded["houses"]) == 12


def test_export_helper_can_omit_metadata_for_backward_compatible_shape() -> None:
    chart_data = _jaipur_chart()
    exported = json_export.export_kundali_chart(
        chart_data,
        include_metadata=False,
    )

    assert set(exported) == {"lagna", "planets", "houses"}
    json.dumps(exported, allow_nan=False)


def test_api_response_remains_json_safe() -> None:
    response = get_kundali(_jaipur_request())
    data = response.model_dump(mode="json")

    payload = json.dumps(data, allow_nan=False)
    decoded = json.loads(payload)

    assert set(decoded) == {"lagna", "planets", "houses"}
    assert decoded["lagna"]["rashi_index"] == decoded["lagna"]["rashi"]["index"]
    assert len(decoded["planets"]) == 9
    assert len(decoded["houses"]) == 12


def test_required_top_level_fields_exist_in_exported_chart() -> None:
    exported = json_export.export_kundali_chart(_jaipur_chart())

    assert "lagna" in exported
    assert "planets" in exported
    assert "houses" in exported
    assert "metadata" in exported


def test_to_json_safe_converts_enums_and_tuples() -> None:
    class SampleStatus(Enum):
        READY = "ready"

    result = json_export.to_json_safe(
        {
            "status": SampleStatus.READY,
            "values": (1, 2.5, "three"),
        }
    )

    assert result == {
        "status": "ready",
        "values": [1, 2.5, "three"],
    }
    json.dumps(result, allow_nan=False)


def test_to_json_safe_rejects_non_finite_float() -> None:
    with pytest.raises(ValueError, match="float values must be finite"):
        json_export.to_json_safe({"bad": float("nan")})


def _jaipur_chart() -> dict[str, Any]:
    return chart.assemble_kundali_chart(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
    )


def _jaipur_request() -> KundaliRequest:
    return KundaliRequest(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        second=0,
        timezone_offset=5.5,
        latitude=26.9124,
        longitude=75.7873,
        ayanamsa="lahiri",
    )
