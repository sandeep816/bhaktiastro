"""Tests for the Finance Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the finance rules YAML file
FINANCE_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/finance/finance_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and finance rules are loaded/registered."""
    clear_rule_registry()
    load_rule(FINANCE_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches finance rules 001, 002, 003, and 004."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Venus (2nd lord) strong and in 11th house (matches finance.001 and finance.004)
        "venus.strength.status": "strong",
        "venus.house": 11,

        # Saturn (11th lord) strong and in 4th house (matches finance.002, no malefic in 2nd/11th)
        "saturn.strength.status": "strong",
        "saturn.house": 4,

        # Jupiter in 2nd house (matches finance.003)
        "jupiter.house": 2,

        # Mars in 8th house (no malefic in 2nd/11th, so finance.005 does NOT match)
        "mars.house": 8,
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the finance rules (or only matches malefic pressure)."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Venus in 6th house and weak
        "venus.house": 6,
        "venus.strength.status": "weak",

        # Jupiter in 3rd house
        "jupiter.house": 3,

        # Saturn in 8th house and weak
        "saturn.house": 8,
        "saturn.strength.status": "weak",

        # Mars in 12th house
        "mars.house": 12,
    }


def test_finance_rules_load_successfully() -> None:
    """Test that finance YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "finance"
        assert rule["enabled"] is True


def test_finance_rule_ids_are_unique_and_sequential() -> None:
    """Test that all finance rules have unique IDs matching the finance.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"finance.001", "finance.002", "finance.003", "finance.004", "finance.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # finance.001 (2nd lord Venus strong) should match
    assert matches["finance.001"] is True
    # finance.002 (11th lord Saturn strong) should match
    assert matches["finance.002"] is True
    # finance.003 (Jupiter in 2nd house) should match
    assert matches["finance.003"] is True
    # finance.004 (Venus in 11th house) should match
    assert matches["finance.004"] is True
    # finance.005 (Saturn/Mars in 2nd/11th) should NOT match since Saturn is in 4th, Mars in 8th
    assert matches["finance.005"] is False


def test_non_matching_context_does_not_trigger_rules() -> None:
    """Test that evaluation against a non-matching context yields absent/false results."""
    rules = get_registered_rules()
    context = _non_matching_context()

    results = evaluate_rules(rules, context)
    for res in results:
        assert res["matched"] is False
        assert res["status"] == "absent"


def test_priority_sorting() -> None:
    """Test that evaluated rules are sorted by priority (highest first)."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    
    # Priority values: 150 (001), 140 (002), 130 (003), 120 (004), 110 (005)
    sorted_ids = [res["rule_id"] for res in results]
    expected_order = ["finance.001", "finance.002", "finance.003", "finance.004", "finance.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating finance rules does not mutate the prediction context."""
    rules = get_registered_rules()
    context = _matching_context()
    original_context = copy.deepcopy(context)

    evaluate_rules(rules, context)
    assert context == original_context


def test_evaluated_results_are_json_safe() -> None:
    """Test that rule evaluation results and composed predictions are fully JSON serializable."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    
    # Verify evaluation results
    json_safe_results = json.dumps(results)
    assert json.loads(json_safe_results) == results

    # Verify composed output
    composed = compose_predictions(results)
    json_safe_composed = json.dumps(composed)
    assert json.loads(json_safe_composed) == composed


def test_composed_finance_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "finance" in composition["categories"]

    finance_summary = composition["categories"]["finance"]
    assert finance_summary["category"] == "finance"
    
    # We had 4 matched and 1 absent rule
    assert len(finance_summary["matched"]) == 4
    assert len(finance_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in finance_summary["matched"]}
    assert matched_ids == {"finance.001", "finance.002", "finance.003", "finance.004"}

    absent_ids = {r["prediction_id"] for r in finance_summary["absent"]}
    assert absent_ids == {"finance.005"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1
