"""Reusable Prediction Result schema foundation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Literal, TypeAlias, TypedDict

PredictionStatus = Literal["present", "absent", "mixed", "unknown"]
PredictionJsonValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | list["PredictionJsonValue"]
    | dict[str, "PredictionJsonValue"]
)

PREDICTION_STATUSES: tuple[PredictionStatus, ...] = (
    "present",
    "absent",
    "mixed",
    "unknown",
)
PREDICTION_DEFAULT_STATUS: PredictionStatus = "unknown"
PREDICTION_CONFIDENCE_MIN = 0.0
PREDICTION_CONFIDENCE_MAX = 1.0
PREDICTION_CONFIDENCE_PRECISION = 4


class PredictionResultMetadata(TypedDict):
    """JSON-safe metadata for a prediction result foundation."""

    calculation_status: str
    formula_status: str
    invalid_status_provided: bool
    confidence_was_clamped: bool


class PredictionResult(TypedDict):
    """JSON-safe structured prediction result foundation."""

    prediction_id: str
    category: str
    title: str
    status: str
    confidence: float
    involved_planets: list[str]
    involved_houses: list[int]
    involved_rashis: list[str]
    supporting_factors: list[PredictionJsonValue]
    challenging_factors: list[PredictionJsonValue]
    reasons: list[str]
    metadata: PredictionResultMetadata


def create_empty_prediction_result(category: str) -> PredictionResult:
    """Create a JSON-safe placeholder prediction result for a category."""

    return create_prediction_result(
        prediction_id="",
        category=category,
        title="",
        status=PREDICTION_DEFAULT_STATUS,
        confidence=PREDICTION_CONFIDENCE_MIN,
        metadata={"calculation_status": "placeholder"},
    )


def create_prediction_result(
    *,
    prediction_id: str = "",
    category: str = "",
    title: str = "",
    status: str = PREDICTION_DEFAULT_STATUS,
    confidence: float = PREDICTION_CONFIDENCE_MIN,
    involved_planets: Sequence[object] | None = None,
    involved_houses: Sequence[object] | None = None,
    involved_rashis: Sequence[object] | None = None,
    supporting_factors: Sequence[object] | None = None,
    challenging_factors: Sequence[object] | None = None,
    reasons: Sequence[object] | None = None,
    metadata: Mapping[str, object] | None = None,
) -> PredictionResult:
    """Create a JSON-safe structured prediction result.

    This helper only normalizes a result envelope. It does not evaluate
    prediction rules, generate interpretation text, or recalculate astrology
    inputs.
    """

    normalized_status, invalid_status_provided = _normalize_status(status)
    normalized_confidence, confidence_was_clamped = _normalize_confidence(confidence)

    return {
        "prediction_id": _normalize_text(prediction_id),
        "category": _normalize_text(category),
        "title": _normalize_title(title),
        "status": normalized_status,
        "confidence": normalized_confidence,
        "involved_planets": _normalize_text_list(involved_planets),
        "involved_houses": _normalize_house_list(involved_houses),
        "involved_rashis": _normalize_text_list(involved_rashis),
        "supporting_factors": _normalize_factor_list(supporting_factors),
        "challenging_factors": _normalize_factor_list(challenging_factors),
        "reasons": _normalize_reason_list(reasons),
        "metadata": _create_metadata(
            metadata,
            invalid_status_provided=invalid_status_provided,
            confidence_was_clamped=confidence_was_clamped,
        ),
    }


def _normalize_status(status: object) -> tuple[PredictionStatus, bool]:
    """Normalize a status into the allowed prediction status set."""

    normalized_status = _normalize_text(status)
    if normalized_status in PREDICTION_STATUSES:
        return normalized_status, False  # type: ignore[return-value]

    return PREDICTION_DEFAULT_STATUS, True


def _normalize_confidence(confidence: object) -> tuple[float, bool]:
    """Normalize confidence into the JSON-safe inclusive `0..1` range."""

    if isinstance(confidence, bool) or not isinstance(confidence, Real):
        return PREDICTION_CONFIDENCE_MIN, True

    confidence_value = float(confidence)
    if not math.isfinite(confidence_value):
        return PREDICTION_CONFIDENCE_MIN, True

    clamped_value = max(
        PREDICTION_CONFIDENCE_MIN,
        min(PREDICTION_CONFIDENCE_MAX, confidence_value),
    )

    return (
        round(clamped_value, PREDICTION_CONFIDENCE_PRECISION),
        clamped_value != confidence_value,
    )


def _normalize_text_list(values: Sequence[object] | None) -> list[str]:
    """Normalize an optional sequence into non-empty text values."""

    if values is None or isinstance(values, (str, bytes)):
        return []

    normalized_values: list[str] = []
    for value in values:
        normalized_value = _normalize_text(value)
        if normalized_value:
            normalized_values.append(normalized_value)

    return normalized_values


def _normalize_house_list(values: Sequence[object] | None) -> list[int]:
    """Normalize an optional sequence into integer house values."""

    if values is None or isinstance(values, (str, bytes)):
        return []

    normalized_values: list[int] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, Integral):
            continue
        normalized_values.append(int(value))

    return normalized_values


def _normalize_factor_list(
    values: Sequence[object] | None,
) -> list[PredictionJsonValue]:
    """Normalize factor values into JSON-safe structures."""

    if values is None or isinstance(values, (str, bytes)):
        return []

    return [_make_json_safe(value) for value in values]


def _normalize_reason_list(values: Sequence[object] | None) -> list[str]:
    """Normalize reasons into non-empty JSON-safe text values."""

    return _normalize_text_list(values)


def _create_metadata(
    metadata: Mapping[str, object] | None,
    *,
    invalid_status_provided: bool,
    confidence_was_clamped: bool,
) -> PredictionResultMetadata:
    """Create JSON-safe metadata with normalization diagnostics."""

    source_metadata = metadata if isinstance(metadata, Mapping) else {}
    calculation_status = _normalize_text(
        source_metadata.get("calculation_status", "foundation")
    )
    formula_status = _normalize_text(source_metadata.get("formula_status", "schema"))

    return {
        "calculation_status": calculation_status or "foundation",
        "formula_status": formula_status or "schema",
        "invalid_status_provided": invalid_status_provided,
        "confidence_was_clamped": confidence_was_clamped,
    }


def _make_json_safe(value: object) -> PredictionJsonValue:
    """Return a JSON-safe copy of a factor value."""

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
        return {
            str(key): _make_json_safe(nested_value)
            for key, nested_value in value.items()
        }

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_make_json_safe(item) for item in value]

    return str(value)


def _normalize_text(value: object) -> str:
    """Normalize free-form identifiers into lowercase foundation keys."""

    return str(value or "").strip().casefold()


def _normalize_title(value: object) -> str:
    """Normalize a title while preserving display casing."""

    return str(value or "").strip()
