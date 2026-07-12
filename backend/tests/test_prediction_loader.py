"""Tests for the YAML Rule Loader foundation."""

from __future__ import annotations

import json
import os
import pytest

from backend.app.prediction.registry import clear_rule_registry, get_registered_rules
from backend.app.prediction.loader import (
    RuleLoaderError,
    load_rule,
    load_rules,
    load_rules_from_yaml,
)


@pytest.fixture(autouse=True)
def clean_registry() -> None:
    """Ensure the registry is cleared before and after each test."""
    clear_rule_registry()
    yield
    clear_rule_registry()


# Valid YAML strings for testing
VALID_SINGLE_RULE_YAML = """
id: career_gov_sun_10th
category: career
title: Sun in 10th House
priority: 150
conditions:
  field: planets.sun.house
  operator: equals
  value: 10
result:
  status: present
"""

VALID_MULTIPLE_RULES_YAML = """
- id: career_gov_sun_10th
  category: career
  title: Sun in 10th House
  priority: 150
  conditions:
    field: planets.sun.house
    operator: equals
    value: 10
  result:
    status: present

- id: marriage_delay_saturn
  category: marriage
  title: Saturn in 7th House
  priority: 120
  conditions:
    field: planets.saturn.house
    operator: equals
    value: 7
  result:
    status: present
"""

MALFORMED_YAML = """
id: career_rule
category: career
title: Bad indentation
priority:
  - 100
 - invalid_indentation
"""

INVALID_SCHEMA_YAML = """
id: career_rule
category: invalid_category
title: Invalid Category Rule
conditions: {}
result: {}
"""


def test_load_rules_from_yaml_single() -> None:
    """Test loading a single rule from a YAML string."""
    rules = load_rules_from_yaml(VALID_SINGLE_RULE_YAML)
    assert len(rules) == 1
    assert rules[0]["id"] == "career_gov_sun_10th"
    assert rules[0]["category"] == "career"

    # Check registered rules
    registered = get_registered_rules()
    assert len(registered) == 1
    assert registered[0]["id"] == "career_gov_sun_10th"


def test_load_rules_from_yaml_multiple() -> None:
    """Test loading multiple rules from a YAML list string."""
    rules = load_rules_from_yaml(VALID_MULTIPLE_RULES_YAML)
    assert len(rules) == 2
    ids = {r["id"] for r in rules}
    assert ids == {"career_gov_sun_10th", "marriage_delay_saturn"}

    registered = get_registered_rules()
    assert len(registered) == 2


def test_load_rule_from_file(tmp_path) -> None:
    """Test loading rule from a temporary file path."""
    file_path = tmp_path / "rules.yaml"
    file_path.write_text(VALID_SINGLE_RULE_YAML, encoding="utf-8")

    rules = load_rule(str(file_path))
    assert len(rules) == 1
    assert rules[0]["id"] == "career_gov_sun_10th"

    assert len(get_registered_rules()) == 1


def test_load_rules_from_directory(tmp_path) -> None:
    """Test traversing a directory and loading all YAML rule files."""
    # Create subfolders and files
    career_dir = tmp_path / "career"
    career_dir.mkdir()
    career_file = career_dir / "career_rules.yaml"
    career_file.write_text(VALID_SINGLE_RULE_YAML, encoding="utf-8")

    marriage_dir = tmp_path / "marriage"
    marriage_dir.mkdir()
    marriage_file = marriage_dir / "marriage_rules.yml"  # Test .yml extension
    
    marriage_rule_yaml = """
    id: marriage_delay_saturn
    category: marriage
    title: Saturn in 7th House
    conditions:
      field: planets.saturn.house
      operator: equals
      value: 7
    result:
      status: present
    """
    marriage_file.write_text(marriage_rule_yaml, encoding="utf-8")

    # Load rules from root temp directory
    rules = load_rules(str(tmp_path))
    assert len(rules) == 2
    ids = {r["id"] for r in rules}
    assert ids == {"career_gov_sun_10th", "marriage_delay_saturn"}

    registered = get_registered_rules()
    assert len(registered) == 2


def test_malformed_yaml_raises_rule_loader_error() -> None:
    """Test that malformed YAML does not crash python and raises RuleLoaderError."""
    with pytest.raises(RuleLoaderError) as exc_info:
        load_rules_from_yaml(MALFORMED_YAML)

    errs = exc_info.value.errors
    assert len(errs) == 1
    assert errs[0]["type"] == "yaml_parsing"
    assert "error" in errs[0]


def test_invalid_schema_yaml_raises_rule_loader_error() -> None:
    """Test that a YAML rule with invalid schema raises RuleLoaderError."""
    with pytest.raises(RuleLoaderError) as exc_info:
        load_rules_from_yaml(INVALID_SCHEMA_YAML)

    errs = exc_info.value.errors
    assert len(errs) == 1
    assert errs[0]["type"] == "schema_validation"
    assert "invalid_category" in errs[0]["error"]


def test_duplicate_rule_ids_during_load() -> None:
    """Test that duplicate rule IDs raise RuleLoaderError via registry validation."""
    load_rules_from_yaml(VALID_SINGLE_RULE_YAML)

    # Re-loading the same rule ID causes registry duplicate error
    with pytest.raises(RuleLoaderError) as exc_info:
        load_rules_from_yaml(VALID_SINGLE_RULE_YAML)

    errs = exc_info.value.errors
    assert len(errs) == 1
    assert errs[0]["type"] == "registry_integration"
    assert "duplicate" in errs[0]["error"]


def test_file_not_found_raises_exception() -> None:
    """Test that loading a non-existent file path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_rule("non_existent_file.yaml")


def test_directory_not_found_raises_exception() -> None:
    """Test that loading a non-existent directory raises NotADirectoryError."""
    with pytest.raises(NotADirectoryError):
        load_rules("non_existent_directory")


def test_json_serialization_of_yaml_loaded_rules() -> None:
    """Test that rules successfully loaded from YAML are JSON serializable."""
    load_rules_from_yaml(VALID_SINGLE_RULE_YAML)
    registered = get_registered_rules()
    
    # Verify serializability
    serialized = json.dumps(registered)
    loaded = json.loads(serialized)
    assert len(loaded) == 1
    assert loaded[0]["id"] == "career_gov_sun_10th"
