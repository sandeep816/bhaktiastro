"""Universal Prediction Rule Schema and validation helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Optional, TypedDict

from pydantic import BaseModel, ConfigDict, Field, model_validator

VALID_CATEGORIES: set[str] = {
    "career",
    "marriage",
    "finance",
    "health",
    "education",
    "children",
    "spiritual",
    "raj_yoga",
    "dhana_yoga",
    "general",
}


class PredictionRule(TypedDict, total=False):
    """JSON-safe prediction rule structure for TypedDict usage."""

    id: str
    version: str
    category: str
    subcategory: str | None
    title: str
    description: str | None
    priority: int
    enabled: bool
    conditions: dict[str, Any]
    result: dict[str, Any]
    tags: list[str]
    references: list[str]
    metadata: dict[str, Any]


class PredictionRuleModel(BaseModel):
    """Pydantic model representing a universal prediction rule schema."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique rule identifier (lowercase snake_case).")
    version: str = Field("1.0.0", description="Semantic version of the rule.")
    category: str = Field(..., description="Astrological/life domain category.")
    subcategory: Optional[str] = Field(None, description="Optional subcategory.")
    title: str = Field("", description="Short descriptive title of the rule.")
    description: Optional[str] = Field(None, description="Optional detailed astrological logic description.")
    priority: int = Field(100, description="Precedence priority for rule execution sorting.")
    enabled: bool = Field(True, description="Whether this rule is currently active.")
    conditions: dict[str, Any] = Field(..., description="Boolean or composite conditions for the Condition Engine.")
    result: dict[str, Any] = Field(..., description="Result metadata template to output if conditions match.")
    tags: list[str] = Field(default_factory=list, description="Descriptive labels/tags for categorization/filtering.")
    references: list[str] = Field(default_factory=list, description="Scriptural references/sources.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary additional metadata dictionary.")

    @model_validator(mode="before")
    @classmethod
    def validate_model_rule(cls, data: Any) -> Any:
        """Validate input dictionary using the standard helper."""
        if isinstance(data, dict):
            return validate_rule(data)
        return data


def validate_rule_id(rule_id: Any) -> str:
    """Validate and normalize rule ID. Must be a non-empty string."""
    if not isinstance(rule_id, str):
        raise TypeError("Rule ID must be a string")
    normalized = rule_id.strip()
    if not normalized:
        raise ValueError("Rule ID cannot be empty")
    return normalized.casefold()


def validate_priority(priority: Any) -> int:
    """Validate priority. Must be an integer."""
    if isinstance(priority, bool):  # bool is a subclass of int in Python
        raise TypeError("Priority must be an integer, not boolean")
    if not isinstance(priority, int):
        raise TypeError("Priority must be an integer")
    return int(priority)


def validate_category(category: Any) -> str:
    """Validate and normalize category. Must be a supported category string."""
    if not isinstance(category, str):
        raise TypeError("Category must be a string")
    normalized = category.strip().casefold()
    if not normalized:
        raise ValueError("Category cannot be empty")
    if normalized not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. Must be one of: {sorted(VALID_CATEGORIES)}"
        )
    return normalized


def validate_rule(rule: Any) -> dict[str, Any]:
    """Validate a full prediction rule dictionary against standard schema.

    Enforces required fields, types, categories, and JSON safety.
    Returns a normalized dictionary.
    """
    if not isinstance(rule, Mapping):
        raise TypeError("Rule must be a mapping (dictionary)")

    # Check for unrecognized extra fields
    allowed_fields = {
        "id",
        "version",
        "category",
        "subcategory",
        "title",
        "description",
        "priority",
        "enabled",
        "conditions",
        "result",
        "tags",
        "references",
        "metadata",
    }
    extra_fields = set(rule.keys()) - allowed_fields
    if extra_fields:
        raise ValueError(f"Extra fields not allowed: {sorted(extra_fields)}")

    # Check required fields
    required_fields = ["id", "category", "conditions", "result"]
    for field in required_fields:
        if field not in rule:
            raise ValueError(f"Field '{field}' is required")

    # Validate id
    rule_id = validate_rule_id(rule["id"])

    # Validate category
    category = validate_category(rule["category"])

    # Validate priority
    priority = rule.get("priority", 100)
    if priority is None:
        priority = 100
    priority = validate_priority(priority)

    # Validate conditions
    conditions = rule["conditions"]
    if not isinstance(conditions, Mapping):
        raise TypeError("Field 'conditions' must be a dictionary")

    # Validate result
    result = rule["result"]
    if not isinstance(result, Mapping):
        raise TypeError("Field 'result' must be a dictionary")

    # Validate version
    version = rule.get("version", "1.0.0")
    if not isinstance(version, str):
        raise TypeError("Field 'version' must be a string")

    # Validate subcategory
    subcategory = rule.get("subcategory")
    if subcategory is not None and not isinstance(subcategory, str):
        raise TypeError("Field 'subcategory' must be a string")

    # Validate title
    title = rule.get("title", "")
    if not isinstance(title, str):
        raise TypeError("Field 'title' must be a string")

    # Validate description
    description = rule.get("description")
    if description is not None and not isinstance(description, str):
        raise TypeError("Field 'description' must be a string")

    # Validate enabled
    enabled = rule.get("enabled", True)
    if not isinstance(enabled, bool):
        raise TypeError("Field 'enabled' must be a boolean")

    # Validate tags
    tags = rule.get("tags")
    if tags is None:
        tags = []
    elif not isinstance(tags, Sequence) or isinstance(tags, (str, bytes)):
        raise TypeError("Field 'tags' must be a list of strings")
    else:
        for idx, tag in enumerate(tags):
            if not isinstance(tag, str):
                raise TypeError(f"Tag at index {idx} must be a string")

    # Validate references
    references = rule.get("references")
    if references is None:
        references = []
    elif not isinstance(references, Sequence) or isinstance(references, (str, bytes)):
        raise TypeError("Field 'references' must be a list of strings")
    else:
        for idx, ref in enumerate(references):
            if not isinstance(ref, str):
                raise TypeError(f"Reference at index {idx} must be a string")

    # Validate metadata
    metadata = rule.get("metadata")
    if metadata is None:
        metadata = {}
    elif not isinstance(metadata, Mapping):
        raise TypeError("Field 'metadata' must be a dictionary")

    # JSON safety check
    _check_json_safe(rule)

    return {
        "id": rule_id,
        "version": version,
        "category": category,
        "subcategory": subcategory,
        "title": title,
        "description": description,
        "priority": priority,
        "enabled": enabled,
        "conditions": dict(conditions),
        "result": dict(result),
        "tags": list(tags),
        "references": list(references),
        "metadata": dict(metadata),
    }


def _check_json_safe(value: object) -> None:
    """Helper to verify that a value is JSON-safe (serializable and without NaN/Inf)."""
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Rule contains JSON-unsafe values: {e}") from e
