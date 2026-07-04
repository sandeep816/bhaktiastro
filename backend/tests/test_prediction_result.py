"""Tests for Prediction Result schema foundation."""

from __future__ import annotations

import json

from backend.app.prediction.result import (
    PREDICTION_STATUSES,
    create_empty_prediction_result,
    create_prediction_result,
)


def test_create_empty_prediction_result() -> None:
    result = create_empty_prediction_result("career")

    assert result["prediction_id"] == ""
    assert result["category"] == "career"
    assert result["title"] == ""
    assert result["status"] == "unknown"
    assert result["confidence"] == 0.0
    assert result["involved_planets"] == []
    assert result["involved_houses"] == []
    assert result["involved_rashis"] == []
    assert result["supporting_factors"] == []
    assert result["challenging_factors"] == []
    assert result["reasons"] == []
    assert result["metadata"]["calculation_status"] == "placeholder"
    assert result["metadata"]["formula_status"] == "schema"


def test_create_populated_prediction_result() -> None:
    result = create_prediction_result(
        prediction_id="career_foundation",
        category="Career",
        title="Career Foundation",
        status="present",
        confidence=0.87555,
        involved_planets=["Saturn", "Mercury"],
        involved_houses=[10, 6, "bad", True],
        involved_rashis=["Capricorn"],
        supporting_factors=[
            {"factor": "house_strength", "score": 0.8},
            "structured note",
        ],
        challenging_factors=[{"factor": "missing_context", "value": None}],
        reasons=["Tenth house context is available."],
    )

    assert result["prediction_id"] == "career_foundation"
    assert result["category"] == "career"
    assert result["title"] == "Career Foundation"
    assert result["status"] == "present"
    assert result["confidence"] == 0.8756
    assert result["involved_planets"] == ["saturn", "mercury"]
    assert result["involved_houses"] == [10, 6]
    assert result["involved_rashis"] == ["capricorn"]
    assert result["supporting_factors"][0] == {
        "factor": "house_strength",
        "score": 0.8,
    }
    assert result["challenging_factors"][0] == {
        "factor": "missing_context",
        "value": None,
    }
    assert result["reasons"] == ["tenth house context is available."]


def test_invalid_status_is_handled_safely() -> None:
    result = create_prediction_result(status="definitely")

    assert result["status"] == "unknown"
    assert result["status"] in PREDICTION_STATUSES
    assert result["metadata"]["invalid_status_provided"] is True


def test_confidence_is_clamped_or_defaulted_safely() -> None:
    high_result = create_prediction_result(confidence=1.5)
    low_result = create_prediction_result(confidence=-0.25)
    invalid_result = create_prediction_result(
        confidence="high",  # type: ignore[arg-type]
    )

    assert high_result["confidence"] == 1.0
    assert high_result["metadata"]["confidence_was_clamped"] is True
    assert low_result["confidence"] == 0.0
    assert low_result["metadata"]["confidence_was_clamped"] is True
    assert invalid_result["confidence"] == 0.0
    assert invalid_result["metadata"]["confidence_was_clamped"] is True


def test_prediction_result_output_is_json_safe() -> None:
    result = create_prediction_result(
        prediction_id="json_safe",
        category="general",
        status="mixed",
        confidence=0.5,
        supporting_factors=[
            {"finite": 1.25, "not_finite": float("nan"), "nested": [1, "ok"]},
            {"set_like_value": {"inner": "value"}},
        ],
        reasons=["JSON-safe output only."],
    )

    assert {
        "prediction_id",
        "category",
        "title",
        "status",
        "confidence",
        "involved_planets",
        "involved_houses",
        "involved_rashis",
        "supporting_factors",
        "challenging_factors",
        "reasons",
        "metadata",
    } <= set(result)
    assert result["supporting_factors"][0]["not_finite"] is None
    json.dumps(result)
