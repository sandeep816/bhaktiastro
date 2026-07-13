"""Tests for reusable prediction category loading and evaluation."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

import backend.app.prediction.categories as category_service
from backend.app.prediction.categories import discover_rule_categories
from backend.app.prediction.categories import evaluate_prediction_categories
from backend.app.prediction.categories import load_prediction_categories
from backend.app.prediction.registry import clear_rule_registry
from backend.app.prediction.registry import get_registered_rules

EXPECTED_RULE_CATEGORIES = {
    "career",
    "children",
    "education",
    "finance",
    "health",
    "marriage",
    "personality",
    "spiritual",
}


@pytest.fixture(autouse=True)
def clean_registry() -> None:
    clear_rule_registry()
    yield
    clear_rule_registry()


def test_available_rule_categories_are_discovered() -> None:
    discovered = discover_rule_categories()

    assert EXPECTED_RULE_CATEGORIES <= set(discovered)
    assert discovered == sorted(discovered)
    assert "general" not in discovered
    assert "raj_yoga" not in discovered
    assert "dhana_yoga" not in discovered


def test_single_category_loads_correctly() -> None:
    result = load_prediction_categories(["career"])

    assert result["requested_categories"] == ["career"]
    assert result["loaded_categories"] == ["career"]
    assert result["unavailable_categories"] == []
    assert result["rule_count"] == 5
    assert {rule["category"] for rule in result["rules"]} == {"career"}
    assert {rule["category"] for rule in get_registered_rules()} == {"career"}


def test_multiple_categories_load_correctly() -> None:
    result = load_prediction_categories(["career", "personality"])

    assert result["requested_categories"] == ["career", "personality"]
    assert result["loaded_categories"] == ["career", "personality"]
    assert result["rule_count"] == 10
    assert {rule["category"] for rule in result["rules"]} == {
        "career",
        "personality",
    }


def test_all_categories_load_when_categories_are_omitted() -> None:
    result = load_prediction_categories()
    discovered = discover_rule_categories()

    assert result["requested_categories"] == discovered
    assert result["loaded_categories"] == discovered
    assert result["metadata"]["all_categories_requested"] is True
    assert result["rule_count"] == len(result["rules"])
    assert EXPECTED_RULE_CATEGORIES <= {
        rule["category"] for rule in result["rules"]
    }


def test_unknown_category_is_handled_safely() -> None:
    result = load_prediction_categories(["career", "unknown"])

    assert result["loaded_categories"] == ["career"]
    assert result["unavailable_categories"] == ["unknown"]
    assert result["rule_count"] == 5
    assert result["errors"]
    assert result["errors"][0]["type"] == "invalid_category"


def test_disabled_rules_are_excluded(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    _write_rule_file(
        tmp_path,
        "career",
        """
- id: "career.enabled"
  category: "career"
  priority: 100
  enabled: true
  conditions:
    field: "sun.house"
    operator: "equals"
    value: 10
  result:
    status: "present"
- id: "career.disabled"
  category: "career"
  priority: 90
  enabled: false
  conditions:
    field: "sun.house"
    operator: "equals"
    value: 10
  result:
    status: "present"
""",
    )
    monkeypatch.setattr(category_service, "RULE_LIBRARY_ROOT", tmp_path)

    loaded = load_prediction_categories(["career"])
    evaluated = evaluate_prediction_categories({"sun.house": 10}, ["career"])

    assert loaded["rule_count"] == 1
    assert [rule["id"] for rule in loaded["rules"]] == ["career.enabled"]
    assert [result["rule_id"] for result in evaluated["results"]] == [
        "career.enabled"
    ]


def test_duplicate_rule_ids_are_handled_safely(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    _write_rule_file(
        tmp_path,
        "career",
        """
- id: "career.duplicate"
  category: "career"
  conditions:
    field: "sun.house"
    operator: "equals"
    value: 10
  result:
    status: "present"
- id: "career.duplicate"
  category: "career"
  conditions:
    field: "moon.house"
    operator: "equals"
    value: 4
  result:
    status: "present"
""",
    )
    monkeypatch.setattr(category_service, "RULE_LIBRARY_ROOT", tmp_path)

    result = load_prediction_categories(["career"])

    assert result["loaded_categories"] == []
    assert result["rule_count"] == 0
    assert result["errors"]
    assert result["errors"][0]["type"] == "registry_integration"
    assert get_registered_rules() == []


def test_category_filtering_prevents_cross_category_evaluation() -> None:
    result = evaluate_prediction_categories(_mixed_context(), ["career"])

    assert result["loaded_categories"] == ["career"]
    assert result["rule_count"] == 5
    assert {entry["category"] for entry in result["results"]} == {"career"}
    assert set(result["composed_predictions"]["categories"]) <= {"career"}


def test_matching_synthetic_context_produces_expected_category_result() -> None:
    result = evaluate_prediction_categories(_personality_matching_context(), ["personality"])
    summary = result["composed_predictions"]["summary"]

    assert result["loaded_categories"] == ["personality"]
    assert result["rule_count"] == 5
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 4
    assert summary["absent_count"] == 1
    assert summary["total_rules"] == result["rule_count"]


def test_non_matching_context_produces_structured_result() -> None:
    result = evaluate_prediction_categories(
        _personality_non_matching_context(),
        ["personality"],
    )
    summary = result["composed_predictions"]["summary"]

    assert result["rule_count"] == 5
    assert summary["total_rules"] == 5
    assert summary["matched_count"] == 0
    assert summary["absent_count"] == 5
    assert set(result["composed_predictions"]["categories"]) == {"personality"}


def test_registry_state_does_not_leak_between_evaluations() -> None:
    evaluate_prediction_categories(_mixed_context(), ["career"])
    assert {rule["category"] for rule in get_registered_rules()} == {"career"}

    evaluate_prediction_categories(_personality_matching_context(), ["personality"])
    assert {rule["category"] for rule in get_registered_rules()} == {"personality"}


def test_input_context_is_not_mutated() -> None:
    context = _personality_matching_context()
    original = deepcopy(context)

    evaluate_prediction_categories(context, ["personality"])

    assert context == original


def test_output_is_json_safe() -> None:
    result = evaluate_prediction_categories(_personality_matching_context(), ["personality"])

    json.dumps(result, allow_nan=False)


def test_invalid_context_is_reported_safely() -> None:
    result = evaluate_prediction_categories("bad-context", ["personality"])  # type: ignore[arg-type]

    assert result["errors"]
    assert result["errors"][-1]["type"] == "invalid_context"
    assert result["composed_predictions"]["summary"]["total_rules"] == 5
    json.dumps(result, allow_nan=False)


def _mixed_context() -> dict[str, object]:
    return {
        "lagna.rashi_index": 1,
        "sun.house": 10,
        "saturn.house": 7,
        "saturn.strength.status": "strong",
        "jupiter.house": 10,
        "jupiter.strength.status": "strong",
    }


def _personality_matching_context() -> dict[str, object]:
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


def _personality_non_matching_context() -> dict[str, object]:
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


def _write_rule_file(tmp_path, category: str, contents: str) -> None:
    category_dir = tmp_path / category
    category_dir.mkdir()
    (category_dir / f"{category}_rules.yaml").write_text(
        contents.strip(),
        encoding="utf-8",
    )
