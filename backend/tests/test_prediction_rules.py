"""Tests for generic Prediction Rule Engine foundation."""

from __future__ import annotations

import json

from backend.app.prediction.rules import evaluate_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.rules import sort_rules_by_priority


def test_single_rule_match_returns_prediction_result() -> None:
    result = evaluate_rule(_rule("career.001", 100, 10), _context())

    assert result["rule_id"] == "career.001"
    assert result["prediction_id"] == "career.001"
    assert result["category"] == "career"
    assert result["title"] == "Mars in 10th House"
    assert result["matched"] is True
    assert result["status"] == "present"
    assert result["confidence"] == 1.0
    assert result["supporting_factors"] == [_condition(10)]
    assert result["challenging_factors"] == []
    assert result["metadata"]["priority"] == 100
    assert result["metadata"]["invalid_rule"] is False


def test_single_rule_fail_returns_absent_result() -> None:
    result = evaluate_rule(_rule("career.001", 100, 9), _context())

    assert result["matched"] is False
    assert result["status"] == "absent"
    assert result["confidence"] == 0.0
    assert result["supporting_factors"] == []
    assert result["challenging_factors"] == [
        {"field": "mars.house", "operator": "equals", "value": 9}
    ]


def test_multiple_rules_are_evaluated_in_priority_order() -> None:
    results = evaluate_rules(
        [
            _rule("career.low", 10, 10),
            _rule("career.high", 100, 10),
            _rule("career.mid", 50, 9),
        ],
        _context(),
    )

    assert [result["rule_id"] for result in results] == [
        "career.high",
        "career.mid",
        "career.low",
    ]
    assert [result["matched"] for result in results] == [True, False, True]


def test_sort_rules_by_priority_orders_highest_first() -> None:
    sorted_rules = sort_rules_by_priority(
        [
            _rule("low", 1, 10),
            _rule("missing", None, 10),
            _rule("high", 999, 10),
        ]
    )

    assert [rule["id"] for rule in sorted_rules] == ["high", "low", "missing"]


def test_invalid_rule_structure_is_handled_safely() -> None:
    result = evaluate_rule(
        {
            "category": "career",
            "title": "Missing Identifier",
            "conditions": {"all_of": [_condition(10)]},
        },
        _context(),
    )

    assert result["rule_id"] == ""
    assert result["matched"] is False
    assert result["status"] == "unknown"
    assert result["confidence"] == 0.0
    assert result["metadata"]["invalid_rule"] is True
    assert result["metadata"]["invalid_reason"] == "missing_rule_id"
    assert result["reasons"] == ["missing_rule_id"]


def test_invalid_conditions_are_handled_safely() -> None:
    result = evaluate_rule(
        {"id": "invalid.conditions", "category": "general", "conditions": []},
        _context(),
    )

    assert result["rule_id"] == "invalid.conditions"
    assert result["matched"] is False
    assert result["status"] == "unknown"
    assert result["metadata"]["invalid_rule"] is True
    assert result["metadata"]["invalid_reason"] == "invalid_conditions"


def test_empty_rule_list_returns_empty_results() -> None:
    assert evaluate_rules([], _context()) == []


def test_rule_result_output_is_json_serializable() -> None:
    result = evaluate_rule(
        {
            **_rule("json.safe", 1, 10),
            "conditions": {
                "all_of": [
                    _condition(10),
                    {
                        "field": "metadata.not_finite",
                        "operator": "equals",
                        "value": float("nan"),
                    },
                ]
            },
        },
        {**_context(), "metadata": {"not_finite": float("nan")}},
    )

    json.dumps(result)


def _rule(rule_id: str, priority: int | None, house_value: int) -> dict[str, object]:
    rule: dict[str, object] = {
        "id": rule_id,
        "category": "career",
        "title": "Mars in 10th House",
        "conditions": {"all_of": [_condition(house_value)]},
    }
    if priority is not None:
        rule["priority"] = priority
    return rule


def _condition(house_value: int) -> dict[str, object]:
    return {"field": "mars.house", "operator": "equals", "value": house_value}


def _context() -> dict[str, object]:
    return {"mars.house": 10, "saturn.house": 7}
