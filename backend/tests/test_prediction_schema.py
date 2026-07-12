"""Tests for the Universal Prediction Rule schema and validation helpers."""

from __future__ import annotations

import json
import pytest
from pydantic import ValidationError

from backend.app.prediction.schema import (
    PredictionRuleModel,
    validate_category,
    validate_priority,
    validate_rule,
    validate_rule_id,
)


def test_valid_rule_dictionary_passes() -> None:
    """Test that a complete, valid rule dictionary passes validation and matches schema."""
    valid_rule = {
        "id": "career_gov_sun_10th",
        "version": "1.0.0",
        "category": "career",
        "subcategory": "government_job",
        "title": "Sun in 10th House",
        "description": "Sun in 10th house indicates government authority.",
        "priority": 150,
        "enabled": True,
        "conditions": {
            "field": "planets.sun.house",
            "operator": "equals",
            "value": 10,
        },
        "result": {
            "status": "present",
            "supporting_factors": ["Sun in 10th house"],
        },
        "tags": ["career", "sun", "authority"],
        "references": ["BPHS Chapter 24"],
        "metadata": {"source": "classical"},
    }

    # Dict validation
    normalized = validate_rule(valid_rule)
    assert normalized["id"] == "career_gov_sun_10th"
    assert normalized["category"] == "career"
    assert normalized["priority"] == 150
    assert normalized["enabled"] is True
    assert normalized["tags"] == ["career", "sun", "authority"]

    # Pydantic validation
    model = PredictionRuleModel.model_validate(valid_rule)
    assert model.id == "career_gov_sun_10th"
    assert model.category == "career"
    assert model.priority == 150
    assert model.enabled is True
    assert model.tags == ["career", "sun", "authority"]


def test_invalid_rule_id() -> None:
    """Test that invalid rule IDs raise correct exceptions."""
    # Non-string raises TypeError
    with pytest.raises(TypeError, match="Rule ID must be a string"):
        validate_rule_id(123)

    # Empty or whitespace raises ValueError
    with pytest.raises(ValueError, match="Rule ID cannot be empty"):
        validate_rule_id("")
    with pytest.raises(ValueError, match="Rule ID cannot be empty"):
        validate_rule_id("   ")

    # Verify ID is case-folded and stripped
    assert validate_rule_id("  Career_ID_123  ") == "career_id_123"


def test_invalid_priority() -> None:
    """Test that invalid priorities raise correct exceptions."""
    # Non-integer raises TypeError
    with pytest.raises(TypeError, match="Priority must be an integer"):
        validate_priority("100")
    with pytest.raises(TypeError, match="Priority must be an integer"):
        validate_priority(10.5)

    # Boolean raises TypeError (since bool is a subclass of int)
    with pytest.raises(TypeError, match="Priority must be an integer, not boolean"):
        validate_priority(True)

    # Valid priority passes
    assert validate_priority(250) == 250


def test_invalid_category() -> None:
    """Test that invalid categories raise correct exceptions."""
    # Non-string raises TypeError
    with pytest.raises(TypeError, match="Category must be a string"):
        validate_category(123)

    # Empty raises ValueError
    with pytest.raises(ValueError, match="Category cannot be empty"):
        validate_category("")
    with pytest.raises(ValueError, match="Category cannot be empty"):
        validate_category("   ")

    # Unsupported category raises ValueError
    with pytest.raises(ValueError, match="Invalid category 'unsupported'"):
        validate_category("unsupported")

    # Valid categories are case-folded and pass
    assert validate_category("  Career  ") == "career"
    assert validate_category("RAJ_YOGA") == "raj_yoga"


def test_missing_required_fields() -> None:
    """Test that missing required fields raise ValueError."""
    base_rule = {
        "id": "test_rule",
        "category": "general",
        "conditions": {},
        "result": {},
    }

    # Missing id
    rule_no_id = base_rule.copy()
    rule_no_id.pop("id")
    with pytest.raises(ValueError, match="Field 'id' is required"):
        validate_rule(rule_no_id)

    # Missing category
    rule_no_cat = base_rule.copy()
    rule_no_cat.pop("category")
    with pytest.raises(ValueError, match="Field 'category' is required"):
        validate_rule(rule_no_cat)

    # Missing conditions
    rule_no_cond = base_rule.copy()
    rule_no_cond.pop("conditions")
    with pytest.raises(ValueError, match="Field 'conditions' is required"):
        validate_rule(rule_no_cond)

    # Missing result
    rule_no_res = base_rule.copy()
    rule_no_res.pop("result")
    with pytest.raises(ValueError, match="Field 'result' is required"):
        validate_rule(rule_no_res)


def test_invalid_field_types() -> None:
    """Test that invalid field types raise TypeError."""
    base_rule = {
        "id": "test_rule",
        "category": "general",
        "conditions": {},
        "result": {},
    }

    # Conditions not a dictionary
    with pytest.raises(TypeError, match="Field 'conditions' must be a dictionary"):
        validate_rule({**base_rule, "conditions": []})

    # Result not a dictionary
    with pytest.raises(TypeError, match="Field 'result' must be a dictionary"):
        validate_rule({**base_rule, "result": "present"})

    # Version not a string
    with pytest.raises(TypeError, match="Field 'version' must be a string"):
        validate_rule({**base_rule, "version": 1})

    # Enabled not a boolean
    with pytest.raises(TypeError, match="Field 'enabled' must be a boolean"):
        validate_rule({**base_rule, "enabled": "yes"})

    # Tags not a list/sequence
    with pytest.raises(TypeError, match="Field 'tags' must be a list of strings"):
        validate_rule({**base_rule, "tags": "astrology"})

    # Tag elements not strings
    with pytest.raises(TypeError, match="Tag at index 1 must be a string"):
        validate_rule({**base_rule, "tags": ["astrology", 123]})


def test_json_serialization_safety() -> None:
    """Test that JSON-unsafe values (NaN, Inf, complex objects) fail validation."""
    base_rule = {
        "id": "test_rule",
        "category": "general",
        "conditions": {},
        "result": {},
    }

    # NaN in conditions
    unsafe_nan = {**base_rule, "conditions": {"threshold": float("nan")}}
    with pytest.raises(ValueError, match="Rule contains JSON-unsafe values"):
        validate_rule(unsafe_nan)

    # Infinity in result
    unsafe_inf = {**base_rule, "result": {"value": float("inf")}}
    with pytest.raises(ValueError, match="Rule contains JSON-unsafe values"):
        validate_rule(unsafe_inf)

    # Complex python object in metadata
    class Dummy:
        pass
    unsafe_obj = {**base_rule, "metadata": {"object": Dummy()}}
    with pytest.raises(ValueError, match="Rule contains JSON-unsafe values"):
        validate_rule(unsafe_obj)


def test_pydantic_validation_fails_on_extra_fields() -> None:
    """Test that Pydantic model forbids extra fields."""
    rule_with_extra = {
        "id": "test_rule",
        "category": "general",
        "conditions": {},
        "result": {},
        "extra_field": "not_allowed",
    }

    with pytest.raises(ValidationError):
        PredictionRuleModel.model_validate(rule_with_extra)
