"""Tests for Prediction Composer foundation."""

from __future__ import annotations

from copy import deepcopy
import json

from backend.app.prediction.composer import compose_predictions


def test_empty_results_are_handled_safely() -> None:
    result = compose_predictions([])

    assert result["categories"] == {}
    assert result["summary"] == {
        "total_rules": 0,
        "matched_count": 0,
        "mixed_count": 0,
        "absent_count": 0,
        "unknown_count": 0,
        "categories_count": 0,
    }
    assert result["metadata"]["calculation_status"] == "foundation"
    assert result["metadata"]["component"] == "prediction_composer"


def test_matched_results_are_grouped_by_category() -> None:
    result = compose_predictions(
        [
            _rule_result("career_10th", "career", "present", 0.8),
            _rule_result("wealth_2nd", "wealth", "present", 0.6),
            _rule_result("career_saturn", "career", "present", 0.4),
        ]
    )

    assert set(result["categories"]) == {"career", "wealth"}
    assert [
        item["prediction_id"] for item in result["categories"]["career"]["matched"]
    ] == ["career_10th", "career_saturn"]
    assert [
        item["prediction_id"] for item in result["categories"]["wealth"]["matched"]
    ] == ["wealth_2nd"]
    assert result["summary"]["matched_count"] == 3
    assert result["summary"]["categories_count"] == 2


def test_mixed_absent_and_unknown_results_are_separated() -> None:
    result = compose_predictions(
        [
            _rule_result("mixed_rule", "career", "mixed", 0.5),
            _rule_result("absent_rule", "career", "absent", 0.25),
            _rule_result("unknown_rule", "career", "unknown", 0.0),
        ]
    )
    career = result["categories"]["career"]

    assert [item["prediction_id"] for item in career["mixed"]] == ["mixed_rule"]
    assert [item["prediction_id"] for item in career["absent"]] == ["absent_rule"]
    assert [item["prediction_id"] for item in career["unknown"]] == ["unknown_rule"]
    assert result["summary"]["mixed_count"] == 1
    assert result["summary"]["absent_count"] == 1
    assert result["summary"]["unknown_count"] == 1


def test_summary_counts_are_correct() -> None:
    result = compose_predictions(
        [
            _rule_result("present_rule", "career", "present", 0.7),
            _rule_result("mixed_rule", "career", "mixed", 0.5),
            _rule_result("absent_rule", "wealth", "absent", 0.2),
            _rule_result("invalid_status", "wealth", "invalid", 0.9),
        ]
    )

    assert result["summary"]["total_rules"] == 4
    assert result["summary"]["matched_count"] == 1
    assert result["summary"]["mixed_count"] == 1
    assert result["summary"]["absent_count"] == 1
    assert result["summary"]["unknown_count"] == 1
    assert result["summary"]["categories_count"] == 2


def test_confidence_average_is_calculated() -> None:
    result = compose_predictions(
        [
            _rule_result("career_1", "career", "present", 0.25),
            _rule_result("career_2", "career", "mixed", 0.75),
            _rule_result("wealth_1", "wealth", "present", 1.0),
        ]
    )

    assert result["categories"]["career"]["confidence_average"] == 0.5
    assert result["categories"]["wealth"]["confidence_average"] == 1.0


def test_reasons_and_involved_factors_are_preserved() -> None:
    result = compose_predictions(
        [
            {
                **_rule_result("career_1", "Career", "present", 0.75),
                "involved_planets": ["Saturn"],
                "involved_houses": [10],
                "involved_rashis": ["Capricorn"],
                "supporting_factors": [{"factor": "house", "value": 10}],
                "challenging_factors": [{"factor": "missing_dasha"}],
                "reasons": ["Structured reason only."],
            }
        ],
        metadata={"source": "unit_test"},
    )
    career = result["categories"]["career"]

    assert career["reasons"] == ["structured reason only."]
    assert career["involved_planets"] == ["saturn"]
    assert career["involved_houses"] == [10]
    assert career["involved_rashis"] == ["capricorn"]
    assert career["supporting_factors"] == [{"factor": "house", "value": 10}]
    assert career["challenging_factors"] == [{"factor": "missing_dasha"}]
    assert result["metadata"]["source"] == "unit_test"


def test_input_is_not_mutated() -> None:
    rule_results = [
        {
            **_rule_result("career_1", "Career", "present", 0.75),
            "supporting_factors": [{"factor": "house", "value": 10}],
        }
    ]
    original = deepcopy(rule_results)

    compose_predictions(rule_results)

    assert rule_results == original


def test_output_is_json_safe() -> None:
    result = compose_predictions(
        [
            {
                **_rule_result("json_safe", "general", "present", 0.5),
                "supporting_factors": [{"not_finite": float("nan")}],
            }
        ],
        metadata={"not_finite": float("nan")},
    )

    assert result["categories"]["general"]["supporting_factors"][0] == {
        "not_finite": None
    }
    assert result["metadata"]["not_finite"] is None
    json.dumps(result)


def _rule_result(
    prediction_id: str,
    category: str,
    status: str,
    confidence: float,
) -> dict[str, object]:
    return {
        "prediction_id": prediction_id,
        "category": category,
        "title": prediction_id.replace("_", " ").title(),
        "status": status,
        "confidence": confidence,
        "involved_planets": [],
        "involved_houses": [],
        "involved_rashis": [],
        "supporting_factors": [],
        "challenging_factors": [],
        "reasons": [],
        "metadata": {"calculation_status": "foundation"},
    }
