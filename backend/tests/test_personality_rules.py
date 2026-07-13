"""Tests for the General Personality Rule Library foundation."""

from __future__ import annotations

import copy
import json
import os

import pytest

from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.loader import load_rule
from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.schema import PredictionRuleModel, validate_rule

PERSONALITY_RULES_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../app/prediction/prediction_rules/personality/personality_rules.yaml",
    )
)

REQUIRED_SCOPE_METADATA = {
    "tendency_only",
    "not_psychological_diagnosis",
    "context_dependent",
}


@pytest.fixture(autouse=True)
def clean_and_load_registry() -> None:
    """Ensure personality rules are loaded through the generic registry path."""
    clear_rule_registry()
    load_rule(PERSONALITY_RULES_PATH)
    yield
    clear_rule_registry()


def test_personality_yaml_loads_successfully() -> None:
    registered = get_registered_rules("personality")

    assert len(registered) == 5
    assert all(rule["enabled"] is True for rule in registered)


def test_personality_rules_pass_universal_schema_validation() -> None:
    for rule in get_registered_rules("personality"):
        normalized = validate_rule(rule)
        model = PredictionRuleModel.model_validate(rule)

        assert normalized["id"] == rule["id"]
        assert model.category == "personality"
        assert _result_has_required_scope_metadata(rule)
        assert {"status", "confidence", "metadata"} <= set(rule["result"])
        _assert_json_safe(rule)


def test_personality_rule_ids_are_unique_and_stable() -> None:
    rules = get_registered_rules("personality")
    rule_ids = [rule["id"] for rule in rules]

    assert len(set(rule_ids)) == len(rule_ids)
    assert set(rule_ids) == {
        "personality.001",
        "personality.002",
        "personality.003",
        "personality.004",
        "personality.005",
    }


def test_personality_rules_use_personality_category() -> None:
    assert {
        rule["category"] for rule in get_registered_rules("personality")
    } == {"personality"}


def test_matching_context_matches_expected_personality_rules() -> None:
    results = evaluate_rules(get_registered_rules("personality"), _matching_context())
    matches = {result["rule_id"]: result["matched"] for result in results}

    assert matches["personality.001"] is True
    assert matches["personality.002"] is True
    assert matches["personality.003"] is False
    assert matches["personality.004"] is True
    assert matches["personality.005"] is True


def test_non_matching_context_does_not_match_lagna_lord_rule() -> None:
    results = evaluate_rules(get_registered_rules("personality"), _non_matching_context())
    result_by_id = {result["rule_id"]: result for result in results}

    assert result_by_id["personality.001"]["matched"] is False
    assert result_by_id["personality.001"]["status"] == "absent"
    assert all(result["matched"] is False for result in results)


def test_personality_priority_sorting_is_stable() -> None:
    results = evaluate_rules(get_registered_rules("personality"), _matching_context())

    assert [result["rule_id"] for result in results] == [
        "personality.001",
        "personality.002",
        "personality.003",
        "personality.004",
        "personality.005",
    ]


def test_evaluated_personality_results_are_json_safe() -> None:
    results = evaluate_rules(get_registered_rules("personality"), _matching_context())

    _assert_json_safe(results)


def test_composed_personality_output_is_structured() -> None:
    results = evaluate_rules(get_registered_rules("personality"), _matching_context())
    composition = compose_predictions(results)

    assert {"categories", "summary", "metadata"} <= set(composition)
    assert "personality" in composition["categories"]

    personality = composition["categories"]["personality"]
    assert personality["category"] == "personality"
    assert len(personality["matched"]) == 4
    assert len(personality["absent"]) == 1
    assert {result["prediction_id"] for result in personality["matched"]} == {
        "personality.001",
        "personality.002",
        "personality.004",
        "personality.005",
    }
    assert {result["prediction_id"] for result in personality["absent"]} == {
        "personality.003",
    }

    summary = composition["summary"]
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["categories_count"] == 1
    _assert_json_safe(composition)


def test_personality_scope_metadata_is_present_on_evaluated_results() -> None:
    results = evaluate_rules(get_registered_rules("personality"), _matching_context())

    for result in results:
        metadata = result["metadata"]
        assert metadata["tendency_only"] is True
        assert metadata["not_psychological_diagnosis"] is True
        assert metadata["context_dependent"] is True


def test_personality_rule_evaluation_does_not_mutate_context() -> None:
    context = _matching_context()
    original_context = copy.deepcopy(context)

    evaluate_rules(get_registered_rules("personality"), context)

    assert context == original_context


def _matching_context() -> dict[str, object]:
    """Synthetic context using keys produced by the Prediction Context Builder."""
    return {
        "lagna.rashi_index": 1,
        "lagna.rashi": "Mesha",
        "lagna.house": 1,
        "mars.strength.status": "strong",
        "sun.strength.status": "strong",
        "moon.strength.status": "weak",
        "mercury.strength.status": "strong",
        "saturn.strength.status": "strong",
    }


def _non_matching_context() -> dict[str, object]:
    """Synthetic context that keeps all personality starter rules absent."""
    return {
        "lagna.rashi_index": 2,
        "lagna.rashi": "Vrishabha",
        "lagna.house": 1,
        "mars.strength.status": "weak",
        "sun.strength.status": "weak",
        "moon.strength.status": "weak",
        "mercury.strength.status": "weak",
        "saturn.strength.status": "weak",
    }


def _result_has_required_scope_metadata(rule: dict[str, object]) -> bool:
    result = rule.get("result")
    if not isinstance(result, dict):
        return False
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        return False
    return all(metadata.get(key) is True for key in REQUIRED_SCOPE_METADATA)


def _assert_json_safe(value: object) -> None:
    json.dumps(value, allow_nan=False)
