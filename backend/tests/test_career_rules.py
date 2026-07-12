"""Tests for the Career Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the career rules YAML file
CAREER_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/career/career_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and career rules are loaded/registered."""
    clear_rule_registry()
    load_rule(CAREER_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches career rules 001, 002, 003, and 005."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Sun in 10th house (matches career.003)
        "sun.house": 10,

        # Saturn placed in 4th house (matches career.002 - 10th lord Saturn in Kendra)
        "saturn.house": 4,
        # Saturn has strong strength (matches career.005)
        "saturn.strength.status": "strong",

        # Jupiter in 10th house and strong (matches career.001)
        "jupiter.house": 10,
        "jupiter.strength.status": "strong",
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the career rules."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Sun in 5th house
        "sun.house": 5,

        # Saturn in 8th house
        "saturn.house": 8,
        "saturn.strength.status": "weak",

        # Jupiter in 9th house
        "jupiter.house": 9,
        "jupiter.strength.status": "weak",
    }


def test_career_rules_load_successfully() -> None:
    """Test that career YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "career"
        assert rule["enabled"] is True


def test_career_rule_ids_are_unique_and_sequential() -> None:
    """Test that all career rules have unique IDs matching the career.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"career.001", "career.002", "career.003", "career.004", "career.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # career.001 (Jupiter strong in 10th) should match
    assert matches["career.001"] is True
    # career.002 (Saturn 10th lord in 4th Kendra) should match
    assert matches["career.002"] is True
    # career.003 (Sun in 10th) should match
    assert matches["career.003"] is True
    # career.004 (Saturn in 10th) should NOT match since Saturn is in 4th
    assert matches["career.004"] is False
    # career.005 (Saturn 10th lord strong) should match
    assert matches["career.005"] is True


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
    expected_order = ["career.001", "career.002", "career.003", "career.004", "career.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating career rules does not mutate the prediction context."""
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


def test_composed_career_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "career" in composition["categories"]

    career_summary = composition["categories"]["career"]
    assert career_summary["category"] == "career"
    
    # We had 4 matched and 1 absent rule
    assert len(career_summary["matched"]) == 4
    assert len(career_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in career_summary["matched"]}
    assert matched_ids == {"career.001", "career.002", "career.003", "career.005"}

    absent_ids = {r["prediction_id"] for r in career_summary["absent"]}
    assert absent_ids == {"career.004"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1
