"""Generic Prediction Rule Engine foundation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any, TypedDict

from backend.app.prediction.conditions import ConditionEvaluation
from backend.app.prediction.conditions import evaluate_condition
from backend.app.prediction.result import PredictionResult
from backend.app.prediction.result import create_prediction_result

RULE_DEFAULT_CATEGORY = "uncategorized"
RULE_DEFAULT_PRIORITY = 0
RULE_MATCH_CONFIDENCE = 1.0
RULE_FAIL_CONFIDENCE = 0.0


class RuleEvaluationResult(PredictionResult, total=False):
    """JSON-safe Prediction Result with rule evaluation metadata fields."""

    rule_id: str
    matched: bool


def evaluate_rule(
    rule: Mapping[str, Any],
    context: Mapping[str, Any],
) -> RuleEvaluationResult:
    """Evaluate one data-driven prediction rule against a generic context."""

    if not isinstance(rule, Mapping):
        return _create_invalid_rule_result("rule_is_not_mapping")

    source_context = context if isinstance(context, Mapping) else {}
    rule_id = _normalize_text(rule.get("id") or rule.get("rule_id"))
    category = _normalize_text(rule.get("category")) or RULE_DEFAULT_CATEGORY
    title = _normalize_title(rule.get("title"))
    conditions = _normalize_rule_conditions(rule.get("conditions"))

    if not rule_id:
        return _create_invalid_rule_result(
            "missing_rule_id",
            category=category,
            title=title,
        )

    if conditions is None:
        return _create_invalid_rule_result(
            "invalid_conditions",
            rule_id=rule_id,
            category=category,
            title=title,
        )

    condition_result = evaluate_condition(conditions, source_context)
    matched = condition_result["matched"]
    result = create_prediction_result(
        prediction_id=rule_id,
        category=category,
        title=title,
        status="present" if matched else "absent",
        confidence=RULE_MATCH_CONFIDENCE if matched else RULE_FAIL_CONFIDENCE,
        supporting_factors=condition_result["matched_conditions"],
        challenging_factors=condition_result["failed_conditions"],
        reasons=_create_reasons(matched, rule_id),
        metadata={
            "calculation_status": "foundation",
            "formula_status": "rule_engine",
        },
    )

    return _with_rule_fields(
        result,
        rule_id=rule_id,
        matched=matched,
        metadata={
            "priority": _normalize_priority(rule.get("priority")),
            "invalid_rule": False,
            "condition_result": condition_result,
        },
    )


def evaluate_rules(
    rules: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
) -> list[RuleEvaluationResult]:
    """Evaluate priority-sorted rules against a generic context."""

    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)):
        return []

    return [evaluate_rule(rule, context) for rule in sort_rules_by_priority(rules)]


def sort_rules_by_priority(
    rules: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Return rules sorted by numeric priority, highest first."""

    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)):
        return []

    return sorted(
        [rule for rule in rules if isinstance(rule, Mapping)],
        key=lambda rule: _normalize_priority(rule.get("priority")),
        reverse=True,
    )


def _normalize_rule_conditions(condition_data: object) -> dict[str, Any] | None:
    """Normalize supported rule condition shapes for the Condition Engine."""

    if not isinstance(condition_data, Mapping):
        return None

    if "all_of" in condition_data:
        return {
            "operator": "all_of",
            "conditions": _normalize_condition_list(condition_data.get("all_of")),
        }

    if "any_of" in condition_data:
        return {
            "operator": "any_of",
            "conditions": _normalize_condition_list(condition_data.get("any_of")),
        }

    if "operator" in condition_data:
        return {str(key): _make_json_safe(value) for key, value in condition_data.items()}

    return None


def _normalize_condition_list(conditions: object) -> list[dict[str, Any]]:
    """Normalize nested rule conditions while preserving order."""

    if not isinstance(conditions, Sequence) or isinstance(conditions, (str, bytes)):
        return []

    normalized_conditions: list[dict[str, Any]] = []
    for condition in conditions:
        normalized_condition = _normalize_rule_conditions(condition)
        if normalized_condition is not None:
            normalized_conditions.append(normalized_condition)

    return normalized_conditions


def _create_invalid_rule_result(
    reason: str,
    *,
    rule_id: str = "",
    category: str = RULE_DEFAULT_CATEGORY,
    title: str = "",
) -> RuleEvaluationResult:
    """Create a safe placeholder result for a malformed rule."""

    result = create_prediction_result(
        prediction_id=rule_id,
        category=category,
        title=title,
        status="unknown",
        confidence=RULE_FAIL_CONFIDENCE,
        reasons=[reason],
        metadata={
            "calculation_status": "invalid",
            "formula_status": "rule_engine",
        },
    )
    return _with_rule_fields(
        result,
        rule_id=rule_id,
        matched=False,
        metadata={
            "priority": RULE_DEFAULT_PRIORITY,
            "invalid_rule": True,
            "invalid_reason": reason,
        },
    )


def _with_rule_fields(
    result: PredictionResult,
    *,
    rule_id: str,
    matched: bool,
    metadata: Mapping[str, Any],
) -> RuleEvaluationResult:
    """Attach rule-specific fields to a normalized Prediction Result."""

    rule_result: RuleEvaluationResult = {
        **result,
        "rule_id": rule_id,
        "matched": matched,
    }
    rule_result["metadata"].update(
        {str(key): _make_json_safe(value) for key, value in metadata.items()}
    )
    return rule_result


def _create_reasons(matched: bool, rule_id: str) -> list[str]:
    """Create deterministic structural reasons without interpretation text."""

    outcome = "matched" if matched else "not_matched"
    return [f"rule {rule_id} {outcome}"]


def _normalize_priority(priority: object) -> int:
    """Normalize priority into an integer sorting value."""

    if isinstance(priority, bool) or not isinstance(priority, Integral):
        return RULE_DEFAULT_PRIORITY

    return int(priority)


def _normalize_text(value: object) -> str:
    """Normalize identifiers into lowercase keys."""

    return str(value or "").strip().casefold()


def _normalize_title(value: object) -> str:
    """Normalize title while preserving display casing."""

    return str(value or "").strip()


def _make_json_safe(value: object) -> Any:
    """Return a JSON-safe copy of rule metadata values."""

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
