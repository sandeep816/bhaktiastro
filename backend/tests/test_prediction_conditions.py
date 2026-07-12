"""Tests for generic Prediction Condition Engine foundation."""

from __future__ import annotations

import json

from backend.app.prediction.conditions import evaluate_all
from backend.app.prediction.conditions import evaluate_any
from backend.app.prediction.conditions import evaluate_condition


def test_equals_condition_matches_context_value() -> None:
    result = evaluate_condition(
        {"field": "mars.house", "operator": "equals", "value": 10},
        _context(),
    )

    assert result["matched"] is True
    assert result["matched_conditions"] == [
        {"field": "mars.house", "operator": "equals", "value": 10}
    ]
    assert result["failed_conditions"] == []
    assert result["metadata"]["field_exists"] is True


def test_greater_than_condition_matches_numeric_context_value() -> None:
    result = evaluate_condition(
        {"field": "strength.score", "operator": "greater_than", "value": 70},
        _context(),
    )

    assert result["matched"] is True
    assert result["metadata"]["operator"] == "greater_than"


def test_contains_condition_matches_sequence_value() -> None:
    result = evaluate_condition(
        {"field": "planet.tags", "operator": "contains", "value": "benefic"},
        _context(),
    )

    assert result["matched"] is True


def test_exists_condition_handles_present_and_missing_fields() -> None:
    present = evaluate_condition(
        {"field": "moon.rashi", "operator": "exists"},
        _context(),
    )
    missing = evaluate_condition(
        {"field": "venus.house", "operator": "exists"},
        _context(),
    )

    assert present["matched"] is True
    assert missing["matched"] is False
    assert missing["metadata"]["field_exists"] is False


def test_all_of_requires_all_conditions_to_match() -> None:
    result = evaluate_all(
        [
            {"field": "mars.house", "operator": "equals", "value": 10},
            {"field": "saturn.house", "operator": "equals", "value": 7},
        ],
        _context(),
    )

    assert result["matched"] is True
    assert result["metadata"]["operator"] == "all_of"
    assert result["metadata"]["matched_count"] == 2
    assert result["metadata"]["failed_count"] == 0


def test_any_of_matches_when_one_condition_matches() -> None:
    result = evaluate_any(
        [
            {"field": "mars.house", "operator": "equals", "value": 1},
            {"field": "saturn.house", "operator": "equals", "value": 7},
        ],
        _context(),
    )

    assert result["matched"] is True
    assert result["metadata"]["operator"] == "any_of"
    assert result["metadata"]["matched_count"] == 1
    assert result["metadata"]["failed_count"] == 1


def test_nested_composite_conditions_are_supported() -> None:
    result = evaluate_condition(
        {
            "operator": "all_of",
            "conditions": [
                {"field": "mars.house", "operator": "equals", "value": 10},
                {
                    "operator": "any_of",
                    "conditions": [
                        {
                            "field": "moon.rashi",
                            "operator": "equals",
                            "value": "aries",
                        },
                        {
                            "field": "moon.rashi",
                            "operator": "equals",
                            "value": "cancer",
                        },
                    ],
                },
            ],
        },
        _context(),
    )

    assert result["matched"] is True
    assert result["metadata"]["operator"] == "all_of"
    assert len(result["matched_conditions"]) == 2


def test_invalid_operator_is_handled_safely() -> None:
    result = evaluate_condition(
        {"field": "mars.house", "operator": "between", "value": [1, 12]},
        _context(),
    )

    assert result["matched"] is False
    assert result["metadata"]["invalid_operator"] is True
    assert result["failed_conditions"] == [
        {"field": "mars.house", "operator": "between", "value": [1, 12]}
    ]


def test_not_operators_are_supported() -> None:
    not_equals = evaluate_condition(
        {"field": "mars.house", "operator": "not_equals", "value": 1},
        _context(),
    )
    not_contains = evaluate_condition(
        {"field": "planet.tags", "operator": "not_contains", "value": "weak"},
        _context(),
    )
    not_exists = evaluate_condition(
        {"field": "missing.field", "operator": "not_exists"},
        _context(),
    )

    assert not_equals["matched"] is True
    assert not_contains["matched"] is True
    assert not_exists["matched"] is True


def test_condition_output_is_json_serializable() -> None:
    result = evaluate_condition(
        {"field": "metadata.not_finite", "operator": "equals", "value": float("nan")},
        {"metadata": {"not_finite": float("nan")}},
    )

    json.dumps(result)


def _context() -> dict[str, object]:
    return {
        "mars.house": 10,
        "saturn.house": 7,
        "moon": {"rashi": "cancer"},
        "planet": {"tags": ["benefic", "fast"]},
        "strength": {"score": 82.5},
    }
