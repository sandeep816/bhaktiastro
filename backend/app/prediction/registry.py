"""Prediction Rule Registry management."""

from __future__ import annotations

import copy
from typing import Any

from backend.app.prediction.schema import validate_category, validate_rule

# In-memory prediction rules storage mapping rule_id -> validated prediction rule
_registry: dict[str, dict[str, Any]] = {}


def register_rule(rule: dict[str, Any]) -> None:
    """Validate and register a single prediction rule.

    Raises:
        TypeError: If rule is not a dictionary.
        ValueError: If rule is invalid or has a duplicate ID.
    """
    validated = validate_rule(rule)
    rule_id = validated["id"]

    if rule_id in _registry:
        raise ValueError(f"Rule ID '{rule_id}' is already registered")

    _registry[rule_id] = validated


def register_rules(rules: list[dict[str, Any]]) -> None:
    """Validate and register a batch of prediction rules.

    This operation is atomic: if any rule is invalid or has a duplicate ID,
    no rules from the batch will be registered.

    Raises:
        TypeError: If rules batch is not a list.
        ValueError: If any rule is invalid or a duplicate.
    """
    if not isinstance(rules, list):
        raise TypeError("Rules batch must be a list of dictionaries")

    # Validate and check all rules first before modifying the registry
    validated_rules: list[dict[str, Any]] = []
    temp_ids: set[str] = set()

    for idx, rule in enumerate(rules):
        validated = validate_rule(rule)
        rule_id = validated["id"]

        if rule_id in _registry or rule_id in temp_ids:
            raise ValueError(f"Rule ID '{rule_id}' is a duplicate (at index {idx})")

        validated_rules.append(validated)
        temp_ids.add(rule_id)

    # All validation passed, safely register all rules
    for validated in validated_rules:
        _registry[validated["id"]] = validated


def get_registered_rules(category: str | None = None) -> list[dict[str, Any]]:
    """Get all registered prediction rules, optionally filtered by category.

    Validates category if provided. Returns a list of deep copies to prevent mutation.

    Raises:
        TypeError: If category is not a string.
        ValueError: If category is invalid.
    """
    if category is not None:
        category = validate_category(category)

    rules_list: list[dict[str, Any]] = []
    for rule in _registry.values():
        if category is None or rule["category"] == category:
            rules_list.append(copy.deepcopy(rule))

    return rules_list


def clear_rule_registry() -> None:
    """Clear all registered prediction rules from memory."""
    _registry.clear()
