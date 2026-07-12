"""Tests for the Health Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the health rules YAML file
HEALTH_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/health/health_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and health rules are loaded/registered."""
    clear_rule_registry()
    load_rule(HEALTH_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches health rules 001, 002, 003, and 005."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Lagna lord Mars is strong and in 3rd house (matches health.001)
        "mars.strength.status": "strong",
        "mars.house": 3,

        # Sun is strong (matches health.002)
        "sun.strength.status": "strong",

        # Moon is strong (matches health.003)
        "moon.strength.status": "strong",

        # Jupiter in 6th house (matches health.005)
        "jupiter.house": 6,

        # Saturn in 4th house (no malefic in 1st/6th, so health.004 does NOT match)
        "saturn.house": 4,
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the health rules (or only matches malefic pressure)."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Lagna lord Mars is weak
        "mars.strength.status": "weak",

        # Sun is weak
        "sun.strength.status": "weak",

        # Moon is weak
        "moon.strength.status": "weak",

        # Jupiter in 9th house
        "jupiter.house": 9,

        # Saturn in 8th house
        "saturn.house": 8,
    }


def test_health_rules_load_successfully() -> None:
    """Test that health YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "health"
        assert rule["enabled"] is True


def test_health_rule_ids_are_unique_and_sequential() -> None:
    """Test that all health rules have unique IDs matching the health.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"health.001", "health.002", "health.003", "health.004", "health.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # health.001 (Lagna lord Mars strong) should match
    assert matches["health.001"] is True
    # health.002 (Sun strong) should match
    assert matches["health.002"] is True
    # health.003 (Moon strong) should match
    assert matches["health.003"] is True
    # health.004 (Saturn/Mars in 1st/6th) should NOT match since Saturn is in 4th, Mars in 3rd
    assert matches["health.004"] is False
    # health.005 (Jupiter in 6th house) should match
    assert matches["health.005"] is True


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
    expected_order = ["health.001", "health.002", "health.003", "health.004", "health.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating health rules does not mutate the prediction context."""
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


def test_composed_health_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "health" in composition["categories"]

    health_summary = composition["categories"]["health"]
    assert health_summary["category"] == "health"
    
    # We had 4 matched and 1 absent rule
    assert len(health_summary["matched"]) == 4
    assert len(health_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in health_summary["matched"]}
    assert matched_ids == {"health.001", "health.002", "health.003", "health.005"}

    absent_ids = {r["prediction_id"] for r in health_summary["absent"]}
    assert absent_ids == {"health.004"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1


def test_health_results_include_disclaimer_metadata() -> None:
    """Test that all evaluated health rule results include required medical disclaimer metadata."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    
    for res in results:
        # Check that evaluated result metadata has disclaimers
        meta = res["metadata"]
        assert meta.get("not_medical_advice") is True
        assert meta.get("requires_professional_evaluation") is True
