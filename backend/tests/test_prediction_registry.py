"""Tests for the Reusable Prediction Rule Registry."""

from __future__ import annotations

import json
import pytest

from backend.app.prediction.registry import (
    clear_rule_registry,
    get_registered_rules,
    register_rule,
    register_rules,
)


@pytest.fixture(autouse=True)
def clean_registry() -> None:
    """Ensure the registry is cleared before and after each test."""
    clear_rule_registry()
    yield
    clear_rule_registry()


def _valid_rule(rule_id: str, category: str = "general") -> dict[str, object]:
    """Helper to create a minimal valid prediction rule dictionary."""
    return {
        "id": rule_id,
        "category": category,
        "title": f"Test Rule {rule_id}",
        "conditions": {"field": "test.field", "operator": "exists"},
        "result": {"status": "present"},
    }


def test_register_single_rule() -> None:
    """Test that a single valid rule can be registered and retrieved."""
    rule = _valid_rule("rule_1", "career")
    register_rule(rule)

    registered = get_registered_rules()
    assert len(registered) == 1
    assert registered[0]["id"] == "rule_1"
    assert registered[0]["category"] == "career"


def test_register_multiple_rules() -> None:
    """Test that a batch of valid rules can be registered."""
    rules = [
        _valid_rule("rule_1", "career"),
        _valid_rule("rule_2", "marriage"),
        _valid_rule("rule_3", "finance"),
    ]
    register_rules(rules)

    registered = get_registered_rules()
    assert len(registered) == 3
    ids = {r["id"] for r in registered}
    assert ids == {"rule_1", "rule_2", "rule_3"}


def test_duplicate_rule_id_rejected() -> None:
    """Test that duplicate rule IDs are rejected and do not cause duplicate registrations."""
    rule = _valid_rule("dup_rule")
    register_rule(rule)

    # Registering the same ID again raises ValueError
    with pytest.raises(ValueError, match="already registered"):
        register_rule(rule)

    # Storing inside registry remains exactly 1 rule
    assert len(get_registered_rules()) == 1


def test_batch_register_atomicity_and_duplicate_handling() -> None:
    """Test that batch registration is atomic and rejects internal/external duplicates."""
    # 1. Reject batch containing a rule ID already in the registry
    register_rule(_valid_rule("existing_rule"))

    batch = [
        _valid_rule("new_rule_1"),
        _valid_rule("existing_rule"),  # Duplicate of external
        _valid_rule("new_rule_2"),
    ]

    with pytest.raises(ValueError, match="is a duplicate"):
        register_rules(batch)

    # Verification: Atomicity ensures neither new_rule_1 nor new_rule_2 got registered
    registered_ids = {r["id"] for r in get_registered_rules()}
    assert "new_rule_1" not in registered_ids
    assert "new_rule_2" not in registered_ids
    assert len(registered_ids) == 1

    # 2. Reject batch containing internal duplicate IDs
    clear_rule_registry()
    internal_dup_batch = [
        _valid_rule("new_rule_1"),
        _valid_rule("dup_rule"),
        _valid_rule("dup_rule"),  # Internal duplicate
    ]

    with pytest.raises(ValueError, match="is a duplicate"):
        register_rules(internal_dup_batch)

    # Verification: Atomicity ensures absolutely no rules from the batch got registered
    assert len(get_registered_rules()) == 0


def test_category_filtering() -> None:
    """Test that filtering by category returns only the expected rules."""
    rules = [
        _valid_rule("rule_career_1", "career"),
        _valid_rule("rule_career_2", "career"),
        _valid_rule("rule_marriage_1", "marriage"),
    ]
    register_rules(rules)

    # Fetch career rules
    career_rules = get_registered_rules("career")
    assert len(career_rules) == 2
    assert {r["id"] for r in career_rules} == {"rule_career_1", "rule_career_2"}

    # Fetch marriage rules
    marriage_rules = get_registered_rules("marriage")
    assert len(marriage_rules) == 1
    assert marriage_rules[0]["id"] == "rule_marriage_1"

    # Fetch general (empty category)
    general_rules = get_registered_rules("general")
    assert len(general_rules) == 0

    # Invalid category filtering raises ValueError
    with pytest.raises(ValueError, match="Invalid category"):
        get_registered_rules("invalid_category")


def test_clear_registry() -> None:
    """Test that clear_rule_registry removes all registered rules."""
    register_rule(_valid_rule("rule_1"))
    register_rule(_valid_rule("rule_2"))
    assert len(get_registered_rules()) == 2

    clear_rule_registry()
    assert len(get_registered_rules()) == 0


def test_invalid_rule_rejected() -> None:
    """Test that invalid rules fail registration and registry is not modified."""
    invalid_rule = {
        "id": "invalid_rule",
        "category": "invalid_category",  # Bad category
        "conditions": {},
        "result": {},
    }

    with pytest.raises(ValueError, match="Invalid category"):
        register_rule(invalid_rule)

    assert len(get_registered_rules()) == 0


def test_deep_copy_prevents_external_mutation() -> None:
    """Test that modifying returned rule dictionaries does not mutate registry state."""
    rule = _valid_rule("mutable_rule", "career")
    register_rule(rule)

    # Retrieve rules and mutate a field
    retrieved = get_registered_rules()
    assert len(retrieved) == 1
    retrieved[0]["category"] = "mutated_category"
    retrieved[0]["conditions"]["field"] = "mutated_field"

    # Re-retrieve and verify the registry remains unchanged
    fresh_retrieve = get_registered_rules()
    assert fresh_retrieve[0]["category"] == "career"
    assert fresh_retrieve[0]["conditions"]["field"] == "test.field"


def test_registry_output_is_json_serializable() -> None:
    """Test that retrieved rules can be JSON serialized."""
    rules = [
        _valid_rule("rule_1", "career"),
        _valid_rule("rule_2", "marriage"),
    ]
    register_rules(rules)

    registered = get_registered_rules()
    serialized = json.dumps(registered)
    loaded = json.loads(serialized)
    assert len(loaded) == 2
