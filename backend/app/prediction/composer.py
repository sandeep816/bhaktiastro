"""Prediction Composer foundation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any, TypedDict

from backend.app.prediction.result import PredictionJsonValue
from backend.app.prediction.result import PredictionResult
from backend.app.prediction.result import create_prediction_result

COMPOSER_DEFAULT_CATEGORY = "uncategorized"
COMPOSER_STATUSES = ("matched", "mixed", "absent", "unknown")
PREDICTION_STATUS_TO_SECTION = {
    "present": "matched",
    "mixed": "mixed",
    "absent": "absent",
    "unknown": "unknown",
}
COMPOSER_CONFIDENCE_PRECISION = 4


class PredictionCategorySummary(TypedDict):
    """JSON-safe grouped prediction category output."""

    category: str
    matched: list[PredictionResult]
    mixed: list[PredictionResult]
    absent: list[PredictionResult]
    unknown: list[PredictionResult]
    confidence_average: float
    reasons: list[str]
    involved_planets: list[str]
    involved_houses: list[int]
    involved_rashis: list[str]
    supporting_factors: list[PredictionJsonValue]
    challenging_factors: list[PredictionJsonValue]
    metadata: dict[str, int | str]


class PredictionComposerSummary(TypedDict):
    """JSON-safe top-level composer counts."""

    total_rules: int
    matched_count: int
    mixed_count: int
    absent_count: int
    unknown_count: int
    categories_count: int


class PredictionComposition(TypedDict):
    """JSON-safe Prediction Composer foundation result."""

    categories: dict[str, PredictionCategorySummary]
    summary: PredictionComposerSummary
    metadata: dict[str, Any]


def compose_predictions(
    rule_results: list[dict],
    category: str | None = None,
    metadata: dict | None = None,
) -> PredictionComposition:
    """Group rule results into deterministic, JSON-safe prediction sections."""

    normalized_results = _normalize_rule_results(rule_results, category)
    categories: dict[str, PredictionCategorySummary] = {}
    summary = _create_empty_summary()

    for result in normalized_results:
        category_key = _normalize_category(result.get("category") or category)
        category_summary = categories.setdefault(
            category_key,
            _create_empty_category(category_key),
        )
        section = PREDICTION_STATUS_TO_SECTION.get(result["status"], "unknown")
        category_summary[section].append(result)  # type: ignore[literal-required]
        _add_category_rollups(category_summary, result)
        summary["total_rules"] += 1
        _increment_summary_count(summary, section)

    for category_summary in categories.values():
        category_summary["confidence_average"] = _average_confidence(
            [
                result["confidence"]
                for section in COMPOSER_STATUSES
                for result in category_summary[section]  # type: ignore[literal-required]
            ]
        )
        category_summary["metadata"].update(
            {
                "results_count": sum(
                    len(category_summary[section])  # type: ignore[literal-required]
                    for section in COMPOSER_STATUSES
                ),
                "matched_count": len(category_summary["matched"]),
                "mixed_count": len(category_summary["mixed"]),
                "absent_count": len(category_summary["absent"]),
                "unknown_count": len(category_summary["unknown"]),
            }
        )

    summary["categories_count"] = len(categories)

    return {
        "categories": categories,
        "summary": summary,
        "metadata": _create_metadata(metadata),
    }


def _normalize_rule_results(
    rule_results: object,
    default_category: str | None,
) -> list[PredictionResult]:
    """Normalize incoming rule result dictionaries without mutating inputs."""

    if not isinstance(rule_results, Sequence) or isinstance(rule_results, (str, bytes)):
        return []

    normalized_results: list[PredictionResult] = []
    for result in rule_results:
        if not isinstance(result, Mapping):
            continue

        normalized_results.append(
            create_prediction_result(
                prediction_id=_get_text(result, "prediction_id", "id"),
                category=_get_text(result, "category") or default_category or "",
                title=_get_text(result, "title"),
                status=_get_text(result, "status"),
                confidence=result.get("confidence", 0.0),  # type: ignore[arg-type]
                involved_planets=_get_sequence(result, "involved_planets"),
                involved_houses=_get_sequence(result, "involved_houses"),
                involved_rashis=_get_sequence(result, "involved_rashis"),
                supporting_factors=_get_sequence(result, "supporting_factors"),
                challenging_factors=_get_sequence(result, "challenging_factors"),
                reasons=_get_sequence(result, "reasons"),
                metadata=_get_mapping(result, "metadata"),
            )
        )

    return normalized_results


def _create_empty_category(category: str) -> PredictionCategorySummary:
    """Create an empty grouped category section."""

    return {
        "category": category,
        "matched": [],
        "mixed": [],
        "absent": [],
        "unknown": [],
        "confidence_average": 0.0,
        "reasons": [],
        "involved_planets": [],
        "involved_houses": [],
        "involved_rashis": [],
        "supporting_factors": [],
        "challenging_factors": [],
        "metadata": {
            "calculation_status": "foundation",
            "results_count": 0,
            "matched_count": 0,
            "mixed_count": 0,
            "absent_count": 0,
            "unknown_count": 0,
        },
    }


def _create_empty_summary() -> PredictionComposerSummary:
    """Create an empty composer count summary."""

    return {
        "total_rules": 0,
        "matched_count": 0,
        "mixed_count": 0,
        "absent_count": 0,
        "unknown_count": 0,
        "categories_count": 0,
    }


def _add_category_rollups(
    category_summary: PredictionCategorySummary,
    result: PredictionResult,
) -> None:
    """Preserve category-level reasons, factors, and involved entities."""

    _extend_unique_text(category_summary["reasons"], result["reasons"])
    _extend_unique_text(category_summary["involved_planets"], result["involved_planets"])
    _extend_unique_int(category_summary["involved_houses"], result["involved_houses"])
    _extend_unique_text(category_summary["involved_rashis"], result["involved_rashis"])
    category_summary["supporting_factors"].extend(result["supporting_factors"])
    category_summary["challenging_factors"].extend(result["challenging_factors"])


def _increment_summary_count(
    summary: PredictionComposerSummary,
    section: str,
) -> None:
    """Increment top-level summary counters for a section."""

    if section == "matched":
        summary["matched_count"] += 1
        return

    if section == "mixed":
        summary["mixed_count"] += 1
        return

    if section == "absent":
        summary["absent_count"] += 1
        return

    summary["unknown_count"] += 1


def _average_confidence(confidences: list[float]) -> float:
    """Return rounded average confidence for a category."""

    if not confidences:
        return 0.0

    return round(sum(confidences) / len(confidences), COMPOSER_CONFIDENCE_PRECISION)


def _create_metadata(metadata: object) -> dict[str, Any]:
    """Create JSON-safe composer metadata."""

    source_metadata = metadata if isinstance(metadata, Mapping) else {}
    normalized_metadata = {
        str(key): _make_json_safe(value) for key, value in source_metadata.items()
    }
    normalized_metadata.setdefault("calculation_status", "foundation")
    normalized_metadata.setdefault("component", "prediction_composer")
    return normalized_metadata


def _normalize_category(category: object) -> str:
    """Normalize a category key for grouping."""

    normalized_category = str(category or "").strip().casefold()
    return normalized_category or COMPOSER_DEFAULT_CATEGORY


def _extend_unique_text(target: list[str], values: list[str]) -> None:
    """Append text values while preserving first-seen order."""

    for value in values:
        if value not in target:
            target.append(value)


def _extend_unique_int(target: list[int], values: list[int]) -> None:
    """Append integer values while preserving first-seen order."""

    for value in values:
        if value not in target:
            target.append(value)


def _get_text(source: Mapping[str, object], *keys: str) -> str:
    """Read the first non-empty string-like value from a mapping."""

    for key in keys:
        value = source.get(key)
        if value is None:
            continue
        return str(value)

    return ""


def _get_sequence(source: Mapping[str, object], key: str) -> Sequence[object] | None:
    """Read a sequence value from a mapping."""

    value = source.get(key)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value

    return None


def _get_mapping(source: Mapping[str, object], key: str) -> Mapping[str, object] | None:
    """Read a mapping value from a mapping."""

    value = source.get(key)
    if isinstance(value, Mapping):
        return value

    return None


def _make_json_safe(value: object) -> Any:
    """Return a JSON-safe copy of metadata values."""

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
