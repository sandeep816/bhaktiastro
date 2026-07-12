"""Tests for the Children Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the children rules YAML file
CHILDREN_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/children/children_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and children rules are loaded/registered."""
    clear_rule_registry()
    load_rule(CHILDREN_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches children rules 001, 002, 003, and 004."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Sun (5th lord) is strong (matches children.004)
        "sun.strength.status": "strong",

        # Jupiter in 1st house and strong (aspects 5th, matches children.002)
        "jupiter.house": 1,
        "jupiter.strength.status": "strong",

        # Venus placed in 5th house and exalted (matches children.001 and children.003)
        "venus.house": 5,
        "venus.dignity.is_exalted": True,

        # Saturn and Mars in non-5th houses (so children.005 does NOT match)
        "saturn.house": 12,
        "mars.house": 8,
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the children rules (or only matches malefic pressure)."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Sun is weak
        "sun.strength.status": "weak",

        # Jupiter in 9th house and weak
        "jupiter.house": 9,
        "jupiter.strength.status": "weak",

        # Venus in 6th house, not exalted
        "venus.house": 6,
        "venus.dignity.is_exalted": False,

        # Saturn and Mars in non-5th houses
        "saturn.house": 8,
        "mars.house": 12,
    }


def test_children_rules_load_successfully() -> None:
    """Test that children YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "children"
        assert rule["enabled"] is True


def test_children_rule_ids_are_unique_and_sequential() -> None:
    """Test that all children rules have unique IDs matching the children.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"children.001", "children.002", "children.003", "children.004", "children.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # children.001 (Venus exalted in 5th) should match
    assert matches["children.001"] is True
    # children.002 (Jupiter strong in 1st aspecting 5th) should match
    assert matches["children.002"] is True
    # children.003 (Venus benefic in 5th) should match
    assert matches["children.003"] is True
    # children.004 (5th lord Sun strong) should match
    assert matches["children.004"] is True
    # children.005 (Saturn/Mars in 5th) should NOT match since Saturn is in 12th, Mars in 8th
    assert matches["children.005"] is False


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
    expected_order = ["children.001", "children.002", "children.003", "children.004", "children.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating children rules does not mutate the prediction context."""
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


def test_composed_children_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "children" in composition["categories"]

    children_summary = composition["categories"]["children"]
    assert children_summary["category"] == "children"
    
    # We had 4 matched and 1 absent rule
    assert len(children_summary["matched"]) == 4
    assert len(children_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in children_summary["matched"]}
    assert matched_ids == {"children.001", "children.002", "children.003", "children.004"}

    absent_ids = {r["prediction_id"] for r in children_summary["absent"]}
    assert absent_ids == {"children.005"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1


def test_children_results_include_safety_metadata() -> None:
    """Test that all evaluated children rule results include required safety disclaimer metadata."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    
    for res in results:
        meta = res["metadata"]
        assert meta.get("not_medical_advice") is True
        assert meta.get("no_fertility_diagnosis") is True
        assert meta.get("requires_professional_evaluation") is True
