"""Tests for the Marriage Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the marriage rules YAML file
MARRIAGE_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/marriage/marriage_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and marriage rules are loaded/registered."""
    clear_rule_registry()
    load_rule(MARRIAGE_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches marriage rules 001, 002, 003, and 004."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Venus in 7th house (matches marriage.001, marriage.002, and marriage.003)
        "venus.house": 7,

        # Jupiter in 1st house and strong (matches marriage.004)
        "jupiter.house": 1,
        "jupiter.strength.status": "strong",

        # Saturn and Mars in non-7th houses (so marriage.005 does NOT match)
        "saturn.house": 5,
        "mars.house": 2,
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the marriage rules (or only matches malefic pressure)."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Venus in 6th house
        "venus.house": 6,

        # Jupiter in 3rd house and weak
        "jupiter.house": 3,
        "jupiter.strength.status": "weak",

        # Saturn and Mars in non-7th houses
        "saturn.house": 8,
        "mars.house": 12,
    }


def test_marriage_rules_load_successfully() -> None:
    """Test that marriage YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "marriage"
        assert rule["enabled"] is True


def test_marriage_rule_ids_are_unique_and_sequential() -> None:
    """Test that all marriage rules have unique IDs matching the marriage.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"marriage.001", "marriage.002", "marriage.003", "marriage.004", "marriage.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # marriage.001 (Venus in 7th) should match
    assert matches["marriage.001"] is True
    # marriage.002 (Venus 7th lord in 7th Kendra) should match
    assert matches["marriage.002"] is True
    # marriage.003 (Venus in 7th) should match
    assert matches["marriage.003"] is True
    # marriage.004 (Jupiter strong in 1st aspecting 7th) should match
    assert matches["marriage.004"] is True
    # marriage.005 (Saturn/Mars in 7th) should NOT match since they are in 5th/2nd
    assert matches["marriage.005"] is False


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
    expected_order = ["marriage.001", "marriage.002", "marriage.003", "marriage.004", "marriage.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating marriage rules does not mutate the prediction context."""
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


def test_composed_marriage_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "marriage" in composition["categories"]

    marriage_summary = composition["categories"]["marriage"]
    assert marriage_summary["category"] == "marriage"
    
    # We had 4 matched and 1 absent rule
    assert len(marriage_summary["matched"]) == 4
    assert len(marriage_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in marriage_summary["matched"]}
    assert matched_ids == {"marriage.001", "marriage.002", "marriage.003", "marriage.004"}

    absent_ids = {r["prediction_id"] for r in marriage_summary["absent"]}
    assert absent_ids == {"marriage.005"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1
