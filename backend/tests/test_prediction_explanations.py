"""Tests for the reusable Prediction Explanation layer."""

from __future__ import annotations

from copy import deepcopy
import json

from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.explanations import create_prediction_explanation
from backend.app.prediction.explanations import create_prediction_explanations
from backend.app.prediction.explanations import explain_composed_predictions
from backend.app.prediction.result import create_prediction_result


def test_create_prediction_explanation_from_result_object() -> None:
    result = _sample_prediction_result()

    explanation = create_prediction_explanation(result)

    assert set(explanation) == {
        "title",
        "summary",
        "reasoning",
        "confidence",
        "references",
        "notes",
        "metadata",
    }
    assert explanation["title"] == "Career Foundation"
    assert explanation["summary"] == {
        "prediction_id": "career_foundation",
        "category": "career",
        "status": "present",
        "rule_id": "career.001",
        "matched": True,
    }
    assert explanation["confidence"] == 0.75
    assert explanation["reasoning"]["supporting_factors"] == [
        {"field": "sun.house", "operator": "equals", "value": 10}
    ]
    assert explanation["reasoning"]["challenging_factors"] == []
    assert explanation["reasoning"]["reasons"] == ["rule career.001 matched"]
    assert explanation["references"] == [
        "Rule Library Foundation",
        "Structured Source",
    ]
    assert explanation["notes"] == [
        "foundation-only",
        {"scope": "deterministic"},
    ]
    assert explanation["metadata"]["component"] == "prediction_explanation"


def test_prediction_explanation_does_not_mutate_input() -> None:
    result = _sample_prediction_result()
    original = deepcopy(result)

    create_prediction_explanation(result)

    assert result == original


def test_prediction_explanation_handles_missing_or_invalid_input_safely() -> None:
    explanation = create_prediction_explanation("bad-input")  # type: ignore[arg-type]

    assert explanation["title"] == ""
    assert explanation["summary"] == {
        "prediction_id": "",
        "category": "",
        "status": "unknown",
    }
    assert explanation["confidence"] == 0.0
    assert explanation["reasoning"] == {
        "supporting_factors": [],
        "challenging_factors": [],
        "reasons": [],
    }


def test_prediction_explanation_clamps_confidence_and_sanitizes_values() -> None:
    result = {
        **_sample_prediction_result(),
        "confidence": 7.5,
        "supporting_factors": [{"not_finite": float("nan")}],
        "notes": [{"not_finite": float("inf")}],
    }

    explanation = create_prediction_explanation(result)

    assert explanation["confidence"] == 1.0
    assert explanation["reasoning"]["supporting_factors"] == [{"not_finite": None}]
    assert explanation["notes"] == [{"not_finite": None}, {"scope": "deterministic"}]
    json.dumps(explanation, allow_nan=False)


def test_create_prediction_explanations_handles_sequences() -> None:
    explanations = create_prediction_explanations(
        [
            _sample_prediction_result(),
            "bad-entry",  # type: ignore[list-item]
            {**_sample_prediction_result(), "prediction_id": "career_absent"},
        ]
    )

    assert len(explanations) == 2
    assert [item["summary"]["prediction_id"] for item in explanations] == [
        "career_foundation",
        "career_absent",
    ]


def test_explain_composed_predictions_groups_sections() -> None:
    present_result = _sample_prediction_result()
    absent_result = {
        **create_prediction_result(
            prediction_id="career_absent",
            category="career",
            title="Career Absent",
            status="absent",
            confidence=0.0,
            challenging_factors=[
                {"field": "sun.house", "operator": "equals", "value": 10}
            ],
            reasons=["rule career.absent not_matched"],
        ),
        "rule_id": "career.absent",
        "matched": False,
    }
    composed = compose_predictions(
        [present_result, absent_result],
        metadata={"component": "prediction_composer"},
    )

    explanations = explain_composed_predictions(composed)
    career = explanations["categories"]["career"]

    assert len(career["matched"]) == 1
    assert len(career["absent"]) == 1
    assert career["matched"][0]["summary"]["prediction_id"] == "career_foundation"
    assert career["absent"][0]["summary"]["prediction_id"] == "career_absent"
    assert explanations["summary"] == composed["summary"]
    assert explanations["metadata"]["source_component"] == "prediction_composer"
    json.dumps(explanations, allow_nan=False)


def test_explanation_summary_is_structured_not_ui_copy() -> None:
    explanation = create_prediction_explanation(_sample_prediction_result())

    assert isinstance(explanation["summary"], dict)
    assert explanation["title"] == "Career Foundation"
    assert "status" in explanation["summary"]


def _sample_prediction_result() -> dict[str, object]:
    result = create_prediction_result(
        prediction_id="career_foundation",
        category="career",
        title="Career Foundation",
        status="present",
        confidence=0.75,
        supporting_factors=[
            {"field": "sun.house", "operator": "equals", "value": 10}
        ],
        challenging_factors=[],
        reasons=["rule career.001 matched"],
        metadata={"calculation_status": "foundation"},
    )
    result.update(
        {
            "rule_id": "career.001",
            "matched": True,
            "references": ["Rule Library Foundation"],
            "notes": ["foundation-only"],
            "metadata": {
                **result["metadata"],
                "references": ["Structured Source"],
                "notes": [{"scope": "deterministic"}],
            },
        }
    )
    return result
