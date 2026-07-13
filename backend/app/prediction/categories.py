"""Reusable Prediction Rule category loading and evaluation service."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from pathlib import Path
from typing import Any, TypedDict

from backend.app.prediction.composer import PredictionComposition
from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.loader import RuleLoaderError
from backend.app.prediction.loader import load_rules
from backend.app.prediction.registry import clear_rule_registry
from backend.app.prediction.registry import get_registered_rules
from backend.app.prediction.registry import register_rules
from backend.app.prediction.rules import RuleEvaluationResult
from backend.app.prediction.rules import evaluate_rules
from backend.app.prediction.schema import validate_category

RULE_LIBRARY_ROOT = Path(__file__).resolve().parent / "prediction_rules"


class CategoryLoadResult(TypedDict):
    """JSON-safe rule category loading result."""

    requested_categories: list[str]
    loaded_categories: list[str]
    unavailable_categories: list[str]
    rule_count: int
    rules: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    metadata: dict[str, Any]


class CategoryEvaluationResult(TypedDict):
    """JSON-safe category evaluation and composition result."""

    requested_categories: list[str]
    loaded_categories: list[str]
    unavailable_categories: list[str]
    rule_count: int
    results: list[RuleEvaluationResult]
    composed_predictions: PredictionComposition
    errors: list[dict[str, Any]]
    metadata: dict[str, Any]


def discover_rule_categories() -> list[str]:
    """Discover available rule categories from valid rule-library directories."""

    if not RULE_LIBRARY_ROOT.is_dir():
        return []

    discovered: list[str] = []
    for category_dir in RULE_LIBRARY_ROOT.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        if not _has_yaml_files(category_dir):
            continue

        category = _normalize_category_name(category_dir.name)
        if category is None:
            continue
        discovered.append(category)

    return sorted(set(discovered))


def load_prediction_categories(
    categories: list[str] | None = None,
) -> CategoryLoadResult:
    """Load selected prediction rule categories through the generic YAML loader.

    When `categories` is omitted, all discovered categories are loaded. Empty
    lists intentionally load no categories.
    """

    discovered_categories = discover_rule_categories()
    requested_categories, unavailable_categories, errors = _resolve_categories(
        categories,
        discovered_categories,
    )
    loaded_categories: list[str] = []
    enabled_rules: list[dict[str, Any]] = []
    seen_rule_ids: set[str] = set()

    clear_rule_registry()
    for category in requested_categories:
        category_path = RULE_LIBRARY_ROOT / category
        clear_rule_registry()
        try:
            load_rules(str(category_path))
            category_rules = [
                rule
                for rule in get_registered_rules(category)
                if rule.get("enabled", True) is True
            ]
            duplicate_ids = sorted(
                rule["id"] for rule in category_rules if rule["id"] in seen_rule_ids
            )
            if duplicate_ids:
                errors.append(
                    {
                        "category": category,
                        "type": "duplicate_rule_id",
                        "rule_ids": duplicate_ids,
                    }
                )
                continue

            enabled_rules.extend(category_rules)
            seen_rule_ids.update(rule["id"] for rule in category_rules)
            loaded_categories.append(category)
        except RuleLoaderError as exc:
            errors.extend(_format_loader_errors(category, exc))
        except (OSError, ValueError, TypeError) as exc:
            errors.append(
                {
                    "category": category,
                    "type": "category_load_error",
                    "error": str(exc),
                }
            )
        finally:
            clear_rule_registry()

    if enabled_rules:
        try:
            register_rules(enabled_rules)
        except (ValueError, TypeError) as exc:
            clear_rule_registry()
            enabled_rules = []
            loaded_categories = []
            errors.append(
                {
                    "type": "registry_integration",
                    "error": str(exc),
                }
            )

    registered_rules = get_registered_rules()
    return _make_json_safe(
        {
            "requested_categories": requested_categories,
            "loaded_categories": loaded_categories,
            "unavailable_categories": unavailable_categories,
            "rule_count": len(registered_rules),
            "rules": registered_rules,
            "errors": errors,
            "metadata": _create_metadata(
                all_categories_requested=categories is None,
                discovered_categories=discovered_categories,
                component="prediction_category_loader",
            ),
        }
    )


def evaluate_prediction_categories(
    context: dict,
    categories: list[str] | None = None,
) -> CategoryEvaluationResult:
    """Load, evaluate, and compose selected prediction rule categories."""

    source_context: Mapping[str, Any]
    context_errors: list[dict[str, Any]] = []
    if isinstance(context, Mapping):
        source_context = context
    else:
        source_context = {}
        context_errors.append(
            {
                "type": "invalid_context",
                "error": "context must be a dictionary-like mapping",
            }
        )

    loaded = load_prediction_categories(categories)
    results = evaluate_rules(loaded["rules"], source_context)
    composed = compose_predictions(
        results,
        metadata={
            "engine": "prediction",
            "layer": "rule_library",
            "deterministic": True,
            "component": "prediction_category_evaluator",
        },
    )

    return _make_json_safe(
        {
            "requested_categories": loaded["requested_categories"],
            "loaded_categories": loaded["loaded_categories"],
            "unavailable_categories": loaded["unavailable_categories"],
            "rule_count": loaded["rule_count"],
            "results": results,
            "composed_predictions": composed,
            "errors": [*loaded["errors"], *context_errors],
            "metadata": _create_metadata(
                all_categories_requested=categories is None,
                discovered_categories=loaded["metadata"]["discovered_categories"],
                component="prediction_category_evaluator",
            ),
        }
    )


def _resolve_categories(
    categories: list[str] | None,
    discovered_categories: list[str],
) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    """Resolve requested categories against discovered rule-library categories."""

    if categories is None:
        return list(discovered_categories), [], []

    if not isinstance(categories, Sequence) or isinstance(categories, (str, bytes)):
        return (
            [],
            [],
            [
                {
                    "type": "invalid_categories_argument",
                    "error": "categories must be a list of category strings or None",
                }
            ],
        )

    requested: list[str] = []
    unavailable: list[str] = []
    errors: list[dict[str, Any]] = []
    discovered_set = set(discovered_categories)

    for category in categories:
        normalized_category = _normalize_category_name(category)
        if normalized_category is None:
            category_text = str(category or "").strip().casefold()
            if category_text and category_text not in unavailable:
                unavailable.append(category_text)
            errors.append(
                {
                    "category": category_text,
                    "type": "invalid_category",
                    "error": f"Unknown or unsupported category: {category}",
                }
            )
            continue

        if normalized_category not in discovered_set:
            if normalized_category not in unavailable:
                unavailable.append(normalized_category)
            errors.append(
                {
                    "category": normalized_category,
                    "type": "unavailable_category",
                    "error": f"Rule category is not available: {normalized_category}",
                }
            )
            continue

        if normalized_category not in requested:
            requested.append(normalized_category)

    return requested, unavailable, errors


def _normalize_category_name(category: object) -> str | None:
    """Normalize a category name through the universal schema validator."""

    try:
        return validate_category(category)
    except (TypeError, ValueError):
        return None


def _has_yaml_files(directory: Path) -> bool:
    """Return whether a directory contains YAML rule files."""

    return any(
        path.is_file() and path.suffix.casefold() in {".yaml", ".yml"}
        for path in directory.rglob("*")
    )


def _format_loader_errors(
    category: str,
    exc: RuleLoaderError,
) -> list[dict[str, Any]]:
    """Attach category information to loader errors."""

    if not exc.errors:
        return [
            {
                "category": category,
                "type": "category_load_error",
                "error": str(exc),
            }
        ]

    return [
        {
            "category": category,
            **{
                str(key): _make_json_safe(value)
                for key, value in error.items()
            },
        }
        for error in exc.errors
    ]


def _create_metadata(
    *,
    all_categories_requested: bool,
    discovered_categories: list[str],
    component: str,
) -> dict[str, Any]:
    """Create JSON-safe category service metadata."""

    return {
        "calculation_status": "foundation",
        "component": component,
        "engine": "prediction",
        "layer": "rule_library",
        "deterministic": True,
        "all_categories_requested": all_categories_requested,
        "discovered_categories": list(discovered_categories),
    }


def _make_json_safe(value: object) -> Any:
    """Return a JSON-safe scalar or nested value."""

    if value is None or isinstance(value, (str, bool)):
        return value

    if isinstance(value, Real):
        if isinstance(value, bool):
            return value
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            return None
        if isinstance(value, Integral):
            return int(value)
        return numeric_value

    if isinstance(value, Mapping):
        return {str(key): _make_json_safe(nested) for key, nested in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_make_json_safe(item) for item in value]

    return str(value)
