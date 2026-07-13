"""Reusable structured Prediction Explanation layer."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any, TypedDict

from backend.app.prediction.result import PredictionJsonValue

EXPLANATION_SECTIONS = ("matched", "mixed", "absent", "unknown")


class PredictionExplanation(TypedDict):
    """JSON-safe structured explanation generated from a prediction result."""

    title: str
    summary: dict[str, Any]
    reasoning: dict[str, list[PredictionJsonValue]]
    confidence: float
    references: list[str]
    notes: list[PredictionJsonValue]
    metadata: dict[str, Any]


class PredictionExplanationCollection(TypedDict):
    """JSON-safe grouped explanation output for composed predictions."""

    categories: dict[str, dict[str, list[PredictionExplanation]]]
    summary: dict[str, Any]
    metadata: dict[str, Any]


def create_prediction_explanation(
    prediction_result: Mapping[str, Any],
) -> PredictionExplanation:
    """Create a deterministic explanation object from one prediction result.

    This function only restructures existing result data. It does not evaluate
    conditions, alter prediction outcomes, or generate interpretive prose.
    """

    source_result = prediction_result if isinstance(prediction_result, Mapping) else {}
    prediction_id = _normalize_text(
        source_result.get("prediction_id") or source_result.get("id")
    )
    category = _normalize_text(source_result.get("category"))
    title = _normalize_title(source_result.get("title")) or prediction_id or category
    status = _normalize_text(source_result.get("status")) or "unknown"
    confidence = _normalize_confidence(source_result.get("confidence", 0.0))
    metadata = source_result.get("metadata")
    source_metadata = metadata if isinstance(metadata, Mapping) else {}

    summary: dict[str, Any] = {
        "prediction_id": prediction_id,
        "category": category,
        "status": status,
    }
    rule_id = _normalize_text(source_result.get("rule_id"))
    if rule_id:
        summary["rule_id"] = rule_id
    if isinstance(source_result.get("matched"), bool):
        summary["matched"] = source_result["matched"]

    explanation: PredictionExplanation = {
        "title": title,
        "summary": _make_json_safe(summary),
        "reasoning": {
            "supporting_factors": _normalize_factor_list(
                source_result.get("supporting_factors")
            ),
            "challenging_factors": _normalize_factor_list(
                source_result.get("challenging_factors")
            ),
            "reasons": _normalize_factor_list(source_result.get("reasons")),
        },
        "confidence": confidence,
        "references": _extract_references(source_result, source_metadata),
        "notes": _extract_notes(source_result, source_metadata),
        "metadata": {
            "calculation_status": "foundation",
            "component": "prediction_explanation",
            "source_prediction_id": prediction_id,
            "source_status": status,
        },
    }
    return _make_json_safe(explanation)


def create_prediction_explanations(
    prediction_results: Sequence[Mapping[str, Any]],
) -> list[PredictionExplanation]:
    """Create deterministic explanations for a sequence of prediction results."""

    if not isinstance(prediction_results, Sequence) or isinstance(
        prediction_results,
        (str, bytes),
    ):
        return []

    explanations: list[PredictionExplanation] = []
    for result in prediction_results:
        if isinstance(result, Mapping):
            explanations.append(create_prediction_explanation(result))
    return explanations


def explain_composed_predictions(
    composed_predictions: Mapping[str, Any],
) -> PredictionExplanationCollection:
    """Create grouped explanations from Prediction Composer output."""

    source_composition = (
        composed_predictions if isinstance(composed_predictions, Mapping) else {}
    )
    categories = source_composition.get("categories")
    explanation_categories: dict[str, dict[str, list[PredictionExplanation]]] = {}

    if isinstance(categories, Mapping):
        for category, category_output in categories.items():
            if not isinstance(category_output, Mapping):
                continue
            category_key = _normalize_text(category)
            section_output: dict[str, list[PredictionExplanation]] = {}
            for section in EXPLANATION_SECTIONS:
                section_output[section] = create_prediction_explanations(
                    category_output.get(section, [])
                )
            explanation_categories[category_key] = section_output

    source_summary = source_composition.get("summary")
    source_metadata = source_composition.get("metadata")
    return _make_json_safe(
        {
            "categories": explanation_categories,
            "summary": source_summary if isinstance(source_summary, Mapping) else {},
            "metadata": {
                "calculation_status": "foundation",
                "component": "prediction_explanation_collection",
                "source_component": (
                    source_metadata.get("component")
                    if isinstance(source_metadata, Mapping)
                    else None
                ),
            },
        }
    )


def _extract_references(
    result: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> list[str]:
    """Extract reference strings from result or metadata."""

    references: list[str] = []
    for value in (result.get("references"), metadata.get("references")):
        _extend_text_values(references, value)
    source_text = metadata.get("source_text")
    if source_text is not None:
        _extend_text_values(references, [source_text])
    return references


def _extract_notes(
    result: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> list[PredictionJsonValue]:
    """Extract deterministic notes from result or metadata."""

    notes: list[PredictionJsonValue] = []
    notes.extend(_normalize_factor_list(result.get("notes")))
    notes.extend(_normalize_factor_list(metadata.get("notes")))
    return notes


def _extend_text_values(target: list[str], value: object) -> None:
    """Append normalized text values without duplicates."""

    for item in _normalize_text_list(value):
        if item not in target:
            target.append(item)


def _normalize_text_list(value: object) -> list[str]:
    """Normalize a scalar or sequence into a list of non-empty strings."""

    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        normalized = _normalize_title(value)
        return [normalized] if normalized else []
    if not isinstance(value, Sequence):
        normalized = _normalize_title(value)
        return [normalized] if normalized else []

    normalized_items: list[str] = []
    for item in value:
        normalized = _normalize_title(item)
        if normalized:
            normalized_items.append(normalized)
    return normalized_items


def _normalize_factor_list(value: object) -> list[PredictionJsonValue]:
    """Normalize a scalar or sequence into JSON-safe factor entries."""

    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [_make_json_safe(value)]
    if isinstance(value, Sequence):
        return [_make_json_safe(item) for item in value]
    return [_make_json_safe(value)]


def _normalize_confidence(value: object) -> float:
    """Normalize confidence into the inclusive `0..1` range."""

    if isinstance(value, bool) or not isinstance(value, Real):
        return 0.0
    confidence = float(value)
    if not math.isfinite(confidence):
        return 0.0
    return round(max(0.0, min(1.0, confidence)), 4)


def _normalize_text(value: object) -> str:
    """Normalize identifiers into lowercase keys."""

    return str(value or "").strip().casefold()


def _normalize_title(value: object) -> str:
    """Normalize display text while preserving casing."""

    return str(value or "").strip()


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
