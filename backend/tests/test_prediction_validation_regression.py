"""Validation and regression coverage for Prediction Framework foundations."""

from __future__ import annotations

from copy import deepcopy
import json

from backend.app.api.v1.kundali import get_kundali
from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.conditions import evaluate_condition
from backend.app.prediction.context import build_prediction_context
from backend.app.prediction.framework import build_prediction_framework_output
from backend.app.prediction.result import PREDICTION_STATUSES
from backend.app.prediction.result import create_prediction_result
from backend.app.prediction.rules import evaluate_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.schemas.kundali import KundaliRequest


def test_prediction_result_validation_keeps_status_and_confidence_safe() -> None:
    invalid_status = create_prediction_result(status="definitely", confidence=1.25)
    invalid_confidence = create_prediction_result(confidence=float("nan"))

    assert invalid_status["status"] == "unknown"
    assert invalid_status["status"] in PREDICTION_STATUSES
    assert invalid_status["confidence"] == 1.0
    assert invalid_status["metadata"]["invalid_status_provided"] is True
    assert invalid_status["metadata"]["confidence_was_clamped"] is True

    assert invalid_confidence["status"] in PREDICTION_STATUSES
    assert invalid_confidence["confidence"] == 0.0
    assert invalid_confidence["metadata"]["confidence_was_clamped"] is True
    _assert_confidence_range(invalid_status)
    _assert_confidence_range(invalid_confidence)
    _assert_json_safe(invalid_status)
    _assert_json_safe(invalid_confidence)


def test_condition_engine_validation_handles_bad_operator_and_structure() -> None:
    invalid_operator = evaluate_condition(
        {"field": "mars.house", "operator": "between", "value": [1, 12]},
        {"mars.house": 10},
    )
    malformed_nested = evaluate_condition(
        {"operator": "all_of", "conditions": ["bad-condition"]},
        {},
    )
    missing_field = evaluate_condition(
        {"field": "missing.house", "operator": "equals", "value": 1},
        {},
    )

    assert invalid_operator["matched"] is False
    assert invalid_operator["metadata"]["invalid_operator"] is True
    assert isinstance(invalid_operator["failed_conditions"], list)
    assert isinstance(invalid_operator["matched_conditions"], list)

    assert malformed_nested["matched"] is False
    assert malformed_nested["metadata"]["operator"] == "all_of"
    assert malformed_nested["metadata"]["failed_count"] == 1
    assert isinstance(malformed_nested["failed_conditions"], list)

    assert missing_field["matched"] is False
    assert missing_field["metadata"]["field_exists"] is False
    _assert_json_safe(invalid_operator)
    _assert_json_safe(malformed_nested)
    _assert_json_safe(missing_field)


def test_rule_engine_validation_handles_malformed_rules_and_missing_context() -> None:
    malformed_rule = evaluate_rule(
        {
            "category": "career",
            "conditions": {
                "all_of": [
                    {"field": "mars.house", "operator": "equals", "value": 10}
                ]
            },
        },
        {"mars.house": 10},
    )
    missing_context = evaluate_rule(
        {
            "id": "career.missing_context",
            "category": "career",
            "title": "Missing Context Probe",
            "conditions": {
                "all_of": [
                    {"field": "mars.house", "operator": "equals", "value": 10}
                ]
            },
        },
        {},
    )

    assert malformed_rule["matched"] is False
    assert malformed_rule["status"] == "unknown"
    assert malformed_rule["status"] in PREDICTION_STATUSES
    assert malformed_rule["metadata"]["invalid_rule"] is True
    assert malformed_rule["metadata"]["invalid_reason"] == "missing_rule_id"

    assert missing_context["matched"] is False
    assert missing_context["status"] == "absent"
    assert missing_context["status"] in PREDICTION_STATUSES
    assert missing_context["challenging_factors"] == [
        {"field": "mars.house", "operator": "equals", "value": 10}
    ]
    _assert_confidence_range(malformed_rule)
    _assert_confidence_range(missing_context)
    _assert_json_safe(malformed_rule)
    _assert_json_safe(missing_context)


def test_empty_rule_lists_and_composer_summary_remain_stable() -> None:
    rule_results = evaluate_rules([], {"mars.house": 10})
    composed = compose_predictions(rule_results)

    assert rule_results == []
    assert composed["categories"] == {}
    assert composed["summary"] == {
        "total_rules": 0,
        "matched_count": 0,
        "mixed_count": 0,
        "absent_count": 0,
        "unknown_count": 0,
        "categories_count": 0,
    }
    _assert_json_safe(composed)


def test_prediction_context_handles_missing_optional_data_without_mutation() -> None:
    chart_data = {
        "lagna": {"sidereal_longitude": float("nan")},
        "planets": [
            {
                "planet": "Moon",
                "sidereal_longitude": float("nan"),
                "house_number": 1,
            },
            {},
            "bad-planet",
        ],
        "houses": [{}],
    }
    original = deepcopy(chart_data)

    context = build_prediction_context(chart_data)

    assert chart_data == original
    assert context["metadata.chart_data_available"] is True
    assert context["metadata.planet_count"] == 1
    assert context["metadata.house_count"] == 0
    assert context["moon.longitude"] is None
    assert {"strength", "dasha", "yogas"} <= set(
        context["metadata.missing_optional_components"]
    )
    _assert_json_safe(context)


def test_prediction_framework_regression_outputs_are_json_safe() -> None:
    framework = build_prediction_framework_output(
        {"planets": [], "houses": []},
        rules=[],
        metadata={"not_finite": float("nan")},
    )

    assert set(framework) == {"context", "rule_results", "predictions", "metadata"}
    assert framework["rule_results"] == []
    assert framework["predictions"]["summary"]["total_rules"] == 0
    assert framework["predictions"]["summary"]["categories_count"] == 0
    assert framework["metadata"]["not_finite"] is None
    assert framework["metadata"]["real_prediction_rules_enabled"] is False
    _assert_json_safe(framework)


def test_prediction_composer_preserves_counts_and_sanitizes_inputs() -> None:
    results = [
        _rule_result("career.present", "career", "present", 0.75),
        _rule_result("career.mixed", "career", "mixed", 0.5),
        _rule_result("career.absent", "career", "absent", 1.5),
        _rule_result("career.invalid", "career", "impossible", float("nan")),
    ]
    original = deepcopy(results)

    composed = compose_predictions(results, metadata={"not_finite": float("nan")})

    assert results == original
    assert composed["summary"]["total_rules"] == 4
    assert composed["summary"]["matched_count"] == 1
    assert composed["summary"]["mixed_count"] == 1
    assert composed["summary"]["absent_count"] == 1
    assert composed["summary"]["unknown_count"] == 1
    assert composed["categories"]["career"]["confidence_average"] == 0.5625
    assert composed["metadata"]["not_finite"] is None
    _assert_json_safe(composed)


def test_kundali_api_with_include_predictions_is_json_safe() -> None:
    response = get_kundali(_jaipur_request(include_predictions=True))
    data = response.model_dump(mode="json")

    assert "predictions" in data
    assert {"categories", "summary", "metadata"} <= set(data["predictions"])
    assert data["predictions"]["categories"] == {}
    assert data["predictions"]["summary"]["total_rules"] == 0
    assert data["predictions"]["summary"]["categories_count"] == 0
    _assert_json_safe(data)


def test_kundali_api_without_include_predictions_stays_backward_compatible() -> None:
    response = get_kundali(_jaipur_request())
    data = response.model_dump(mode="json")

    assert set(data) == {"lagna", "planets", "houses"}
    assert "predictions" not in data
    _assert_json_safe(data)


def _rule_result(
    prediction_id: str,
    category: str,
    status: str,
    confidence: float,
) -> dict[str, object]:
    return {
        "prediction_id": prediction_id,
        "category": category,
        "title": prediction_id.replace(".", " ").title(),
        "status": status,
        "confidence": confidence,
        "involved_planets": [],
        "involved_houses": [],
        "involved_rashis": [],
        "supporting_factors": [{"not_finite": float("nan")}],
        "challenging_factors": [],
        "reasons": [],
        "metadata": {"calculation_status": "foundation"},
    }


def _jaipur_request(include_predictions: bool = False) -> KundaliRequest:
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
        include_predictions=include_predictions,
    )


def _assert_confidence_range(result: dict[str, object]) -> None:
    assert isinstance(result["confidence"], (int, float))
    assert 0.0 <= float(result["confidence"]) <= 1.0


def _assert_json_safe(value: object) -> None:
    json.dumps(value, allow_nan=False)
