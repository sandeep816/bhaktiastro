"""Internal Prediction Framework assembly helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any, TypedDict

from backend.app.prediction.composer import PredictionComposition
from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.context import build_prediction_context


class PredictionFrameworkOutput(TypedDict):
    """JSON-safe internal Prediction Framework output."""

    context: dict[str, Any]
    rule_results: list[dict[str, Any]]
    predictions: PredictionComposition
    metadata: dict[str, Any]


def build_prediction_framework_output(
    chart_data: Mapping[str, Any],
    rules: Sequence[Mapping[str, Any]] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> PredictionFrameworkOutput:
    """Build internal Prediction Framework output without real prediction rules."""

    context = build_prediction_context(chart_data)
    rule_results = evaluate_prediction_rules(rules or [], context)
    predictions = compose_predictions(
        rule_results,
        metadata={
            "calculation_status": "foundation",
            "component": "prediction_composer",
            "rules_evaluated": len(rule_results),
        },
    )

    return {
        "context": context,
        "rule_results": rule_results,
        "predictions": predictions,
        "metadata": _create_metadata(chart_data, rules, metadata),
    }


def evaluate_prediction_rules(
    rules: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Evaluate prediction rules.

    Sprint 10A.8 intentionally keeps the rule list empty. The helper exists as
    the internal integration boundary for a future Rule Engine and returns a
    JSON-safe empty result set until real rules are introduced.
    """

    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)):
        return []

    if not isinstance(context, Mapping):
        return []

    return []


def _create_metadata(
    chart_data: object,
    rules: object,
    metadata: object,
) -> dict[str, Any]:
    """Create JSON-safe Prediction Framework metadata."""

    source_metadata = metadata if isinstance(metadata, Mapping) else {}
    normalized_metadata = {
        str(key): _make_json_safe(value) for key, value in source_metadata.items()
    }
    normalized_metadata.setdefault("calculation_status", "foundation")
    normalized_metadata.setdefault("component", "prediction_framework")
    normalized_metadata["chart_data_available"] = isinstance(chart_data, Mapping)
    normalized_metadata["rules_count"] = (
        len(rules)
        if isinstance(rules, Sequence) and not isinstance(rules, (str, bytes))
        else 0
    )
    normalized_metadata["real_prediction_rules_enabled"] = False
    return normalized_metadata


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
