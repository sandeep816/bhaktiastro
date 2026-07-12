"""Tests for the Spiritual Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the spiritual rules YAML file
SPIRITUAL_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/spiritual/spiritual_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and spiritual rules are loaded/registered."""
    clear_rule_registry()
    load_rule(SPIRITUAL_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches spiritual rules 001, 002, 003, and 004."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Jupiter (9th lord) is strong (matches spirituality.001)
        # Jupiter is also placed in the 12th house (matches spirituality.002 and spirituality.003)
        "jupiter.house": 12,
        "jupiter.strength.status": "strong",

        # Ketu in 9th house (matches spirituality.004)
        "ketu.house": 9,

        # Moon is strong but placed in 4th house (so spirituality.005 does NOT match)
        "moon.strength.status": "strong",
        "moon.house": 4,
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the spiritual rules."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Jupiter is weak and placed in 4th house
        "jupiter.house": 4,
        "jupiter.strength.status": "weak",

        # Ketu in 8th house
        "ketu.house": 8,

        # Moon is weak and in 5th house
        "moon.strength.status": "weak",
        "moon.house": 5,
    }


def test_spiritual_rules_load_successfully() -> None:
    """Test that spiritual YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "spiritual"
        assert rule["enabled"] is True


def test_spiritual_rule_ids_are_unique_and_sequential() -> None:
    """Test that all spiritual rules have unique IDs matching the spirituality.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"spirituality.001", "spirituality.002", "spirituality.003", "spirituality.004", "spirituality.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # spirituality.001 (strong 9th lord Jupiter) should match
    assert matches["spirituality.001"] is True
    # spirituality.002 (strong Jupiter in 12th) should match
    assert matches["spirituality.002"] is True
    # spirituality.003 (Jupiter in 12th) should match
    assert matches["spirituality.003"] is True
    # spirituality.004 (Ketu in 9th house) should match
    assert matches["spirituality.004"] is True
    # spirituality.005 (reflective Moon in 9th/12th) should NOT match since Moon is in 4th
    assert matches["spirituality.005"] is False


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
    expected_order = ["spirituality.001", "spirituality.002", "spirituality.003", "spirituality.004", "spirituality.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating spiritual rules does not mutate the prediction context."""
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


def test_composed_spiritual_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "spiritual" in composition["categories"]

    spiritual_summary = composition["categories"]["spiritual"]
    assert spiritual_summary["category"] == "spiritual"
    
    # We had 4 matched and 1 absent rule
    assert len(spiritual_summary["matched"]) == 4
    assert len(spiritual_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in spiritual_summary["matched"]}
    assert matched_ids == {"spirituality.001", "spirituality.002", "spirituality.003", "spirituality.004"}

    absent_ids = {r["prediction_id"] for r in spiritual_summary["absent"]}
    assert absent_ids == {"spirituality.005"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1


def test_spiritual_results_include_scope_metadata() -> None:
    """Test that all evaluated spiritual rule results include required safety and scope disclaimer metadata."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    
    for res in results:
        meta = res["metadata"]
        assert meta.get("interpretive_indicator_only") is True
        assert meta.get("no_religious_certainty") is True
        assert meta.get("no_supernatural_claims") is True
