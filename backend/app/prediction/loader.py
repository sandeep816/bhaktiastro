"""Prediction Rule YAML Loader foundation."""

from __future__ import annotations

import os
from typing import Any

import yaml

from backend.app.prediction.registry import register_rules
from backend.app.prediction.schema import validate_rule


class RuleLoaderError(ValueError):
    """Exception raised when loading or validating prediction rules fails."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


def load_rules_from_yaml(data: str) -> list[dict[str, Any]]:
    """Parse, validate, and register prediction rules defined in a YAML string.

    Rules can be a single rule dictionary or a list of rule dictionaries. Valid
    rules are registered automatically.

    Returns:
        A list of validated and registered rule dictionaries.

    Raises:
        RuleLoaderError: If YAML parsing fails or schema validation fails.
    """
    try:
        parsed = yaml.safe_load(data)
    except yaml.YAMLError as e:
        raise RuleLoaderError(
            "Malformed YAML content",
            [{"error": str(e), "type": "yaml_parsing"}],
        ) from e

    if parsed is None:
        return []

    if isinstance(parsed, dict):
        rules_to_load = [parsed]
    elif isinstance(parsed, list):
        rules_to_load = parsed
    else:
        raise RuleLoaderError(
            "YAML root element must be a dictionary or a list of dictionaries",
            [
                {
                    "error": "YAML root element must be a dictionary or list",
                    "type": "structure",
                }
            ],
        )

    validated_rules: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for idx, rule in enumerate(rules_to_load):
        try:
            validated = validate_rule(rule)
            validated_rules.append(validated)
        except (ValueError, TypeError) as e:
            errors.append(
                {
                    "index": idx,
                    "error": str(e),
                    "type": "schema_validation",
                    "rule_id": rule.get("id") if isinstance(rule, dict) else None,
                }
            )

    if errors:
        raise RuleLoaderError("Schema validation failed", errors)

    try:
        register_rules(validated_rules)
    except ValueError as e:
        raise RuleLoaderError(
            "Registry integration failed",
            [{"error": str(e), "type": "registry_integration"}],
        ) from e

    return validated_rules


def load_rule(path: str) -> list[dict[str, Any]]:
    """Load one YAML rule file (which may contain one or more rules) and register them.

    Returns:
        A list of validated and registered rules.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuleLoaderError: If loading or validation fails.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Rule file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return load_rules_from_yaml(content)
    except RuleLoaderError as e:
        # Inject the file path into all errors for structured diagnostics
        for err in e.errors:
            err["path"] = path
        raise
    except Exception as e:
        raise RuleLoaderError(
            f"Failed to read file: {e}",
            [{"path": path, "error": str(e), "type": "file_read"}],
        ) from e


def load_rules(directory: str) -> list[dict[str, Any]]:
    """Traverse a directory, loading and registering all YAML rules.

    Walks the directory recursively to find all .yaml and .yml files.
    Accumulates all errors across files without halting immediately, then
    raises a collected RuleLoaderError if any failures occurred.

    Returns:
        A list of all successfully validated and registered rules.

    Raises:
        NotADirectoryError: If the directory does not exist.
        RuleLoaderError: If any loading or validation errors occurred.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Rules directory not found: {directory}")

    all_registered: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    # Traverse recursively
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                full_path = os.path.join(root, file)
                try:
                    # Note: load_rule registers the rules automatically on success
                    rules = load_rule(full_path)
                    all_registered.extend(rules)
                except RuleLoaderError as e:
                    errors.extend(e.errors)
                except Exception as e:
                    errors.append(
                        {
                            "path": full_path,
                            "error": str(e),
                            "type": "file_read",
                        }
                    )

    if errors:
        raise RuleLoaderError(
            f"Failed to load rules from directory: {len(errors)} error(s) found",
            errors,
        )

    return all_registered
