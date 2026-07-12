"""Generic Prediction Condition Engine foundation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any, Literal, TypedDict

ConditionOperator = Literal[
    "equals",
    "not_equals",
    "greater_than",
    "greater_or_equal",
    "less_than",
    "less_or_equal",
    "contains",
    "not_contains",
    "exists",
    "not_exists",
    "all_of",
    "any_of",
]

CONDITION_OPERATORS: tuple[ConditionOperator, ...] = (
    "equals",
    "not_equals",
    "greater_than",
    "greater_or_equal",
    "less_than",
    "less_or_equal",
    "contains",
    "not_contains",
    "exists",
    "not_exists",
    "all_of",
    "any_of",
)

_MISSING = object()


class ConditionEvaluation(TypedDict):
    """JSON-safe condition evaluation output."""

    matched: bool
    failed_conditions: list[dict[str, Any]]
    matched_conditions: list[dict[str, Any]]
    metadata: dict[str, Any]


def evaluate_condition(
    condition: Mapping[str, Any],
    context: Mapping[str, Any],
) -> ConditionEvaluation:
    """Evaluate one simple or composite condition against a generic context."""

    source_condition = condition if isinstance(condition, Mapping) else {}
    source_context = context if isinstance(context, Mapping) else {}
    operator = _normalize_operator(source_condition.get("operator"))

    if operator == "all_of":
        return evaluate_all(_get_nested_conditions(source_condition), source_context)

    if operator == "any_of":
        return evaluate_any(_get_nested_conditions(source_condition), source_context)

    if operator not in CONDITION_OPERATORS:
        return _create_result(
            matched=False,
            condition=source_condition,
            metadata={
                "operator": operator,
                "invalid_operator": True,
                "reason": "unsupported_operator",
            },
        )

    matched, metadata = _evaluate_simple_condition(
        source_condition,
        source_context,
        operator,
    )

    return _create_result(
        matched=matched,
        condition=source_condition,
        metadata=metadata,
    )


def evaluate_all(
    conditions: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
) -> ConditionEvaluation:
    """Evaluate nested conditions with all-of semantics."""

    evaluations = _evaluate_conditions(conditions, context)
    matched = bool(evaluations) and all(result["matched"] for result in evaluations)
    return _combine_results(
        matched=matched,
        evaluations=evaluations,
        operator="all_of",
        total_conditions=len(evaluations),
    )


def evaluate_any(
    conditions: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
) -> ConditionEvaluation:
    """Evaluate nested conditions with any-of semantics."""

    evaluations = _evaluate_conditions(conditions, context)
    matched = any(result["matched"] for result in evaluations)
    return _combine_results(
        matched=matched,
        evaluations=evaluations,
        operator="any_of",
        total_conditions=len(evaluations),
    )


def _evaluate_simple_condition(
    condition: Mapping[str, Any],
    context: Mapping[str, Any],
    operator: str,
) -> tuple[bool, dict[str, Any]]:
    """Evaluate a non-composite condition."""

    field = _normalize_field(condition.get("field"))
    expected_value = condition.get("value")
    actual_value = _resolve_context_value(context, field)
    field_exists = actual_value is not _MISSING

    if operator == "exists":
        matched = field_exists
    elif operator == "not_exists":
        matched = not field_exists
    elif not field_exists:
        matched = False
    elif operator == "equals":
        matched = actual_value == expected_value
    elif operator == "not_equals":
        matched = actual_value != expected_value
    elif operator == "greater_than":
        matched = _compare_values(actual_value, expected_value, "greater_than")
    elif operator == "greater_or_equal":
        matched = _compare_values(actual_value, expected_value, "greater_or_equal")
    elif operator == "less_than":
        matched = _compare_values(actual_value, expected_value, "less_than")
    elif operator == "less_or_equal":
        matched = _compare_values(actual_value, expected_value, "less_or_equal")
    elif operator == "contains":
        matched = _contains(actual_value, expected_value)
    elif operator == "not_contains":
        matched = not _contains(actual_value, expected_value)
    else:
        matched = False

    return matched, {
        "operator": operator,
        "field": field,
        "field_exists": field_exists,
        "invalid_operator": False,
    }


def _evaluate_conditions(
    conditions: object,
    context: Mapping[str, Any],
) -> list[ConditionEvaluation]:
    """Evaluate a sequence of nested condition dictionaries."""

    if not isinstance(conditions, Sequence) or isinstance(conditions, (str, bytes)):
        return []

    evaluations: list[ConditionEvaluation] = []
    for condition in conditions:
        if not isinstance(condition, Mapping):
            evaluations.append(
                _create_result(
                    matched=False,
                    condition={},
                    metadata={
                        "invalid_condition": True,
                        "reason": "condition_is_not_mapping",
                    },
                )
            )
            continue
        evaluations.append(evaluate_condition(condition, context))

    return evaluations


def _combine_results(
    *,
    matched: bool,
    evaluations: list[ConditionEvaluation],
    operator: str,
    total_conditions: int,
) -> ConditionEvaluation:
    """Combine nested condition evaluation lists into one result."""

    matched_conditions: list[dict[str, Any]] = []
    failed_conditions: list[dict[str, Any]] = []

    for evaluation in evaluations:
        matched_conditions.extend(evaluation["matched_conditions"])
        failed_conditions.extend(evaluation["failed_conditions"])

    return {
        "matched": matched,
        "failed_conditions": failed_conditions,
        "matched_conditions": matched_conditions,
        "metadata": {
            "operator": operator,
            "total_conditions": total_conditions,
            "matched_count": len(matched_conditions),
            "failed_count": len(failed_conditions),
            "invalid_operator": False,
        },
    }


def _create_result(
    *,
    matched: bool,
    condition: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> ConditionEvaluation:
    """Create a JSON-safe condition evaluation result."""

    normalized_condition = _make_json_safe(condition)
    if not isinstance(normalized_condition, dict):
        normalized_condition = {}

    return {
        "matched": matched,
        "failed_conditions": [] if matched else [normalized_condition],
        "matched_conditions": [normalized_condition] if matched else [],
        "metadata": {
            str(key): _make_json_safe(value) for key, value in metadata.items()
        },
    }


def _get_nested_conditions(condition: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    """Read nested composite conditions from a condition mapping."""

    nested_conditions = condition.get("conditions")
    if isinstance(nested_conditions, Sequence) and not isinstance(
        nested_conditions, (str, bytes)
    ):
        return nested_conditions  # type: ignore[return-value]

    return []


def _normalize_operator(operator: object) -> str:
    """Normalize operator names into lowercase keys."""

    return str(operator or "").strip().casefold()


def _normalize_field(field: object) -> str:
    """Normalize a context field path."""

    return str(field or "").strip()


def _resolve_context_value(context: Mapping[str, Any], field: str) -> object:
    """Resolve exact or dotted-path context values."""

    if field in context:
        return context[field]

    current_value: object = context
    for part in field.split("."):
        if not isinstance(current_value, Mapping) or part not in current_value:
            return _MISSING
        current_value = current_value[part]

    return current_value


def _compare_values(actual_value: object, expected_value: object, operator: str) -> bool:
    """Safely compare numeric or naturally comparable values."""

    if isinstance(actual_value, bool) or isinstance(expected_value, bool):
        return False

    try:
        if operator == "greater_than":
            return actual_value > expected_value  # type: ignore[operator]
        if operator == "greater_or_equal":
            return actual_value >= expected_value  # type: ignore[operator]
        if operator == "less_than":
            return actual_value < expected_value  # type: ignore[operator]
        if operator == "less_or_equal":
            return actual_value <= expected_value  # type: ignore[operator]
    except TypeError:
        return False

    return False


def _contains(actual_value: object, expected_value: object) -> bool:
    """Safely evaluate containment for strings, sequences, and mappings."""

    if isinstance(actual_value, str):
        return str(expected_value) in actual_value

    if isinstance(actual_value, Mapping):
        return expected_value in actual_value

    if isinstance(actual_value, Sequence) and not isinstance(actual_value, (str, bytes)):
        return expected_value in actual_value

    return False


def _make_json_safe(value: object) -> Any:
    """Return a JSON-safe copy of result values."""

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
