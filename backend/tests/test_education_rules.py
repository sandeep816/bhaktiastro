"""Tests for the Education Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import load_rule
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.composer import compose_predictions

# Resolve the absolute path of the education rules YAML file
EDUCATION_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/education/education_rules.yaml",
    )
)


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure the registry is cleared and education rules are loaded/registered."""
    clear_rule_registry()
    load_rule(EDUCATION_RULES_PATH)
    yield
    clear_rule_registry()


def _matching_context() -> dict[str, object]:
    """Synthetic prediction context that matches education rules 001, 002, 003, and 004."""
    return {
        # Aries ascendant (Rashi index 1)
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,

        # Moon (4th lord) is strong (matches education.001)
        "moon.strength.status": "strong",

        # Sun (5th lord) is strong (matches education.002)
        "sun.strength.status": "strong",

        # Mercury is placed in Kendra house 10 (matches education.003)
        "mercury.house": 10,
        "mercury.strength.status": "weak",

        # Jupiter in 5th house (matches education.004)
        "jupiter.house": 5,

        # Saturn and Mars in non-4th/5th houses (so education.005 does NOT match)
        "saturn.house": 12,
        "mars.house": 8,
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic prediction context that does not match the education rules (or only matches malefic pressure)."""
    return {
        # Taurus ascendant (Rashi index 2)
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,

        # Moon is weak
        "moon.strength.status": "weak",

        # Sun is weak
        "sun.strength.status": "weak",

        # Mercury is in 6th house (not Kendra) and weak
        "mercury.house": 6,
        "mercury.strength.status": "weak",

        # Jupiter in 9th house
        "jupiter.house": 9,

        # Saturn and Mars in non-4th/5th houses
        "saturn.house": 8,
        "mars.house": 12,
    }


def test_education_rules_load_successfully() -> None:
    """Test that education YAML file is loaded and registered successfully."""
    registered = get_registered_rules()
    assert len(registered) == 5

    # Check category
    for rule in registered:
        assert rule["category"] == "education"
        assert rule["enabled"] is True


def test_education_rule_ids_are_unique_and_sequential() -> None:
    """Test that all education rules have unique IDs matching the education.XXX format."""
    registered = get_registered_rules()
    ids = [rule["id"] for rule in registered]
    
    # Check uniqueness
    assert len(set(ids)) == len(ids)

    # Check naming pattern
    expected_ids = {"education.001", "education.002", "education.003", "education.004", "education.005"}
    assert set(ids) == expected_ids


def test_matching_context_matches_expected_rules() -> None:
    """Test that evaluation against a matching context triggers expected rules."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    assert len(results) == 5

    # Map rule ID to matched outcome
    matches = {res["rule_id"]: res["matched"] for res in results}

    # education.001 (4th lord Moon strong) should match
    assert matches["education.001"] is True
    # education.002 (5th lord Sun strong) should match
    assert matches["education.002"] is True
    # education.003 (Mercury well placed in Kendra) should match
    assert matches["education.003"] is True
    # education.004 (Jupiter in 5th house) should match
    assert matches["education.004"] is True
    # education.005 (Saturn/Mars in 4th/5th) should NOT match since Saturn is in 12th, Mars in 8th
    assert matches["education.005"] is False


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
    expected_order = ["education.001", "education.002", "education.003", "education.004", "education.005"]
    assert sorted_ids == expected_order


def test_no_input_context_mutation() -> None:
    """Test that evaluating education rules does not mutate the prediction context."""
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


def test_composed_education_prediction_output_is_structured() -> None:
    """Test that the composed prediction object matches the expected nested structure."""
    rules = get_registered_rules()
    context = _matching_context()

    results = evaluate_rules(rules, context)
    composition = compose_predictions(results)

    # Check categories structure
    assert "categories" in composition
    assert "education" in composition["categories"]

    education_summary = composition["categories"]["education"]
    assert education_summary["category"] == "education"
    
    # We had 4 matched and 1 absent rule
    assert len(education_summary["matched"]) == 4
    assert len(education_summary["absent"]) == 1

    matched_ids = {r["prediction_id"] for r in education_summary["matched"]}
    assert matched_ids == {"education.001", "education.002", "education.003", "education.004"}

    absent_ids = {r["prediction_id"] for r in education_summary["absent"]}
    assert absent_ids == {"education.005"}

    # Check summary metrics
    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1
