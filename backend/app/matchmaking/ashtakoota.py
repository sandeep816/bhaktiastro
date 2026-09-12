"""Deterministic aggregation over the eight completed Koota calculators."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import math
from numbers import Real
from typing import Literal, NamedTuple, TypedDict

from backend.app.astrology.nakshatra import get_nakshatra
from backend.app.kundali.rashi import get_rashi, normalize_longitude
from backend.app.matchmaking.bhakoot import (
    BHAKOOT_KOOTA_ID,
    BHAKOOT_KOOTA_MAXIMUM_SCORE,
    calculate_bhakoot_koota,
)
from backend.app.matchmaking.foundation import (
    MATCHMAKING_SCHEMA_VERSION,
    MatchmakingJsonValue,
)
from backend.app.matchmaking.gana import (
    GANA_KOOTA_ID,
    GANA_KOOTA_MAXIMUM_SCORE,
    calculate_gana_koota,
)
from backend.app.matchmaking.graha_maitri import (
    GRAHA_MAITRI_KOOTA_ID,
    GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
    calculate_graha_maitri_koota,
)
from backend.app.matchmaking.nadi import (
    NADI_KOOTA_ID,
    NADI_KOOTA_MAXIMUM_SCORE,
    calculate_nadi_koota,
)
from backend.app.matchmaking.tara import (
    TARA_KOOTA_ID,
    TARA_KOOTA_MAXIMUM_SCORE,
    calculate_tara_koota,
)
from backend.app.matchmaking.varna import (
    VARNA_KOOTA_ID,
    VARNA_KOOTA_MAXIMUM_SCORE,
    calculate_varna_koota,
)
from backend.app.matchmaking.vashya import (
    VASHYA_KOOTA_ID,
    VASHYA_KOOTA_MAXIMUM_SCORE,
    calculate_vashya_koota,
)
from backend.app.matchmaking.yoni import (
    YONI_KOOTA_ID,
    YONI_KOOTA_MAXIMUM_SCORE,
    calculate_yoni_koota,
)

ASHTAKOOTA_CALCULATION_NAME = "ashtakoota_aggregation"
ASHTAKOOTA_EXPECTED_KOOTA_COUNT = 8
ASHTAKOOTA_TOTAL_MAXIMUM_SCORE = 36.0

MOON_LONGITUDE_MISSING = "moon_longitude_missing"
MOON_LONGITUDE_INVALID = "moon_longitude_invalid"
KOOTA_RESULT_INVALID = "koota_result_invalid"

MATCHMAKING_ASHTAKOOTA_ISSUE_CODES = (
    MOON_LONGITUDE_MISSING,
    MOON_LONGITUDE_INVALID,
    KOOTA_RESULT_INVALID,
)

AshtakootaInputMode = Literal["varna_pair", "nakshatra_pair", "moon_longitudes"]
AshtakootaExecutionMode = Literal["raw_calculators", "precomputed_results"]
MatchmakingAshtakootaIssueSeverity = Literal["error", "warning"]


class AshtakootaKootaDefinition(NamedTuple):
    """One immutable Koota orchestration definition."""

    koota: str
    maximum_score: float
    calculator: Callable[..., object]
    input_mode: AshtakootaInputMode
    direction: tuple[tuple[str, str], ...]


ASHTAKOOTA_KOOTA_MANIFEST = (
    AshtakootaKootaDefinition(
        VARNA_KOOTA_ID,
        VARNA_KOOTA_MAXIMUM_SCORE,
        calculate_varna_koota,
        "varna_pair",
        (("subject_role", "person_a"), ("comparison_role", "person_b")),
    ),
    AshtakootaKootaDefinition(
        VASHYA_KOOTA_ID,
        VASHYA_KOOTA_MAXIMUM_SCORE,
        calculate_vashya_koota,
        "moon_longitudes",
        (("row_role", "bride"), ("column_role", "groom")),
    ),
    AshtakootaKootaDefinition(
        TARA_KOOTA_ID,
        TARA_KOOTA_MAXIMUM_SCORE,
        calculate_tara_koota,
        "nakshatra_pair",
        (("bride_role", "person_a"), ("groom_role", "person_b")),
    ),
    AshtakootaKootaDefinition(
        YONI_KOOTA_ID,
        YONI_KOOTA_MAXIMUM_SCORE,
        calculate_yoni_koota,
        "nakshatra_pair",
        (("bride_role", "person_a"), ("groom_role", "person_b")),
    ),
    AshtakootaKootaDefinition(
        GRAHA_MAITRI_KOOTA_ID,
        GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
        calculate_graha_maitri_koota,
        "moon_longitudes",
        (("row_role", "bride"), ("column_role", "groom")),
    ),
    AshtakootaKootaDefinition(
        GANA_KOOTA_ID,
        GANA_KOOTA_MAXIMUM_SCORE,
        calculate_gana_koota,
        "nakshatra_pair",
        (("bride_role", "person_a"), ("groom_role", "person_b")),
    ),
    AshtakootaKootaDefinition(
        BHAKOOT_KOOTA_ID,
        BHAKOOT_KOOTA_MAXIMUM_SCORE,
        calculate_bhakoot_koota,
        "moon_longitudes",
        (("row_role", "bride"), ("column_role", "groom")),
    ),
    AshtakootaKootaDefinition(
        NADI_KOOTA_ID,
        NADI_KOOTA_MAXIMUM_SCORE,
        calculate_nadi_koota,
        "nakshatra_pair",
        (("bride_role", "person_a"), ("groom_role", "person_b")),
    ),
)

ASHTAKOOTA_KOOTA_ORDER = tuple(
    definition.koota for definition in ASHTAKOOTA_KOOTA_MANIFEST
)


class MatchmakingAshtakootaIssue(TypedDict):
    """One localization-ready aggregation issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingAshtakootaIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingAshtakootaMetadata(TypedDict):
    """Stable metadata for one Ashtakoota aggregate result."""

    component: str
    schema_version: str
    deterministic: bool
    execution_mode: AshtakootaExecutionMode
    koota_order: list[str]
    expected_koota_count: int
    validated_koota_count: int
    total_maximum_score: float
    aggregation_method: str
    percentage_included: bool
    interpretation_included: bool
    cancellation_included: bool


class MatchmakingAshtakootaResult(TypedDict):
    """Structured aggregate without interpretation or partial totals."""

    calculation: str
    status: str
    bride_moon_longitude: float | None
    groom_moon_longitude: float | None
    koota_results: list[dict[str, MatchmakingJsonValue]]
    score_by_koota: dict[str, float | None]
    maximum_score_by_koota: dict[str, float]
    total_score: float | None
    total_maximum_score: float
    errors: list[MatchmakingAshtakootaIssue]
    warnings: list[MatchmakingAshtakootaIssue]
    references: list[str]
    metadata: MatchmakingAshtakootaMetadata


class _ValidatedComponent(NamedTuple):
    result: dict[str, MatchmakingJsonValue]
    score: float | None
    is_complete: bool
    warnings: list[MatchmakingAshtakootaIssue]


def calculate_ashtakoota(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingAshtakootaResult:
    """Run all eight public Koota calculators and aggregate their scores."""

    _validate_manifest()
    bride, bride_issue = _normalize_raw_longitude(
        bride_moon_longitude,
        role="bride",
    )
    groom, groom_issue = _normalize_raw_longitude(
        groom_moon_longitude,
        role="groom",
    )
    input_errors = [issue for issue in (bride_issue, groom_issue) if issue is not None]
    if input_errors:
        return _build_result(
            execution_mode="raw_calculators",
            bride_moon_longitude=bride,
            groom_moon_longitude=groom,
            components=[],
            score_by_koota={},
            total_score=None,
            errors=input_errors,
            warnings=[],
            validated_koota_count=0,
        )

    if bride is None or groom is None:
        raise RuntimeError("Valid raw inputs must have normalized longitudes")

    pair = _build_adapter_pair(bride, groom)
    components: list[dict[str, MatchmakingJsonValue]] = []
    score_by_koota: dict[str, float | None] = {}
    errors: list[MatchmakingAshtakootaIssue] = []
    warnings: list[MatchmakingAshtakootaIssue] = []
    validated_koota_count = 0

    for definition in ASHTAKOOTA_KOOTA_MANIFEST:
        raw_component = _execute_definition(
            definition,
            pair=pair,
            bride_moon_longitude=bride_moon_longitude,
            groom_moon_longitude=groom_moon_longitude,
        )
        component = _validate_component(
            raw_component,
            definition,
            require_complete=False,
        )
        components.append(component.result)
        score_by_koota[definition.koota] = component.score
        warnings.extend(component.warnings)
        if component.is_complete:
            validated_koota_count += 1
        else:
            errors.append(
                _issue(
                    f"koota_results.{definition.koota}",
                    KOOTA_RESULT_INVALID,
                    None,
                    metadata={"validation_aspect": "component_incomplete"},
                )
            )

    total_score = None
    if not errors:
        total_score = _sum_scores(score_by_koota)

    return _build_result(
        execution_mode="raw_calculators",
        bride_moon_longitude=bride,
        groom_moon_longitude=groom,
        components=components,
        score_by_koota=score_by_koota,
        total_score=total_score,
        errors=errors,
        warnings=warnings,
        validated_koota_count=validated_koota_count,
    )


def aggregate_ashtakoota_results(
    results: object,
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingAshtakootaResult:
    """Strictly validate and aggregate eight precomputed Koota mappings."""

    _validate_manifest()
    bride = normalize_longitude(bride_moon_longitude)  # type: ignore[arg-type]
    groom = normalize_longitude(groom_moon_longitude)  # type: ignore[arg-type]
    supplied_results = _validate_precomputed_identifiers(results)

    components: list[dict[str, MatchmakingJsonValue]] = []
    score_by_koota: dict[str, float | None] = {}
    warnings: list[MatchmakingAshtakootaIssue] = []
    for definition in ASHTAKOOTA_KOOTA_MANIFEST:
        component = _validate_component(
            supplied_results[definition.koota],
            definition,
            require_complete=True,
        )
        components.append(component.result)
        score_by_koota[definition.koota] = component.score
        warnings.extend(component.warnings)

    total_score = _sum_scores(score_by_koota)
    return _build_result(
        execution_mode="precomputed_results",
        bride_moon_longitude=bride,
        groom_moon_longitude=groom,
        components=components,
        score_by_koota=score_by_koota,
        total_score=total_score,
        errors=[],
        warnings=warnings,
        validated_koota_count=ASHTAKOOTA_EXPECTED_KOOTA_COUNT,
    )


def _build_adapter_pair(
    bride_moon_longitude: float,
    groom_moon_longitude: float,
) -> dict[str, object]:
    bride_rashi = get_rashi(bride_moon_longitude)
    groom_rashi = get_rashi(groom_moon_longitude)
    bride_nakshatra = get_nakshatra(bride_moon_longitude)
    groom_nakshatra = get_nakshatra(groom_moon_longitude)
    return {
        "person_a": {
            "person_id": "bride",
            "rashi": bride_rashi["index"],
            "nakshatra": bride_nakshatra["index"],
            "nakshatra_pada": bride_nakshatra["pada"],
        },
        "person_b": {
            "person_id": "groom",
            "rashi": groom_rashi["index"],
            "nakshatra": groom_nakshatra["index"],
            "nakshatra_pada": groom_nakshatra["pada"],
        },
    }


def _execute_definition(
    definition: AshtakootaKootaDefinition,
    *,
    pair: Mapping[str, object],
    bride_moon_longitude: object,
    groom_moon_longitude: object,
) -> object:
    if definition.input_mode == "varna_pair":
        return definition.calculator(
            pair,
            subject_role="person_a",
            comparison_role="person_b",
        )
    if definition.input_mode == "nakshatra_pair":
        return definition.calculator(
            pair,
            bride_role="person_a",
            groom_role="person_b",
        )
    if definition.input_mode == "moon_longitudes":
        return definition.calculator(
            bride_moon_longitude=bride_moon_longitude,
            groom_moon_longitude=groom_moon_longitude,
        )
    raise RuntimeError(f"Unsupported Ashtakoota input mode: {definition.input_mode}")


def _validate_precomputed_identifiers(
    results: object,
) -> dict[str, Mapping[object, object]]:
    if isinstance(results, (str, bytes, bytearray, Mapping)) or not isinstance(
        results, Sequence
    ):
        raise TypeError("results must be a non-string sequence")

    by_koota: dict[str, Mapping[object, object]] = {}
    counts: dict[str, int] = {}
    for index, result in enumerate(results):
        if not isinstance(result, Mapping):
            raise TypeError(f"results[{index}] must be a mapping")
        koota = result.get("koota")
        if not isinstance(koota, str):
            raise TypeError(f"results[{index}].koota must be a string")
        counts[koota] = counts.get(koota, 0) + 1
        by_koota.setdefault(koota, result)

    missing = [koota for koota in ASHTAKOOTA_KOOTA_ORDER if koota not in counts]
    duplicates = [koota for koota in ASHTAKOOTA_KOOTA_ORDER if counts.get(koota, 0) > 1]
    duplicates.extend(
        sorted(
            koota
            for koota, count in counts.items()
            if koota not in ASHTAKOOTA_KOOTA_ORDER and count > 1
        )
    )
    unexpected = sorted(
        koota for koota in counts if koota not in ASHTAKOOTA_KOOTA_ORDER
    )
    if (
        len(results) != ASHTAKOOTA_EXPECTED_KOOTA_COUNT
        or missing
        or duplicates
        or unexpected
    ):
        raise ValueError(
            "invalid precomputed Koota identifiers: "
            f"missing={missing}, duplicates={duplicates}, unexpected={unexpected}"
        )
    return by_koota


def _validate_component(
    result: object,
    definition: AshtakootaKootaDefinition,
    *,
    require_complete: bool,
) -> _ValidatedComponent:
    if not isinstance(result, Mapping):
        raise TypeError(f"{definition.koota} result must be a mapping")
    copied = _copy_json_mapping(result, field=f"koota_results.{definition.koota}")

    koota = copied.get("koota")
    if not isinstance(koota, str):
        raise TypeError(f"{definition.koota}.koota must be a string")
    if koota != definition.koota:
        raise ValueError(f"expected Koota {definition.koota!r}, received {koota!r}")

    maximum_score = _validate_number(
        copied.get("maximum_score"),
        field=f"{definition.koota}.maximum_score",
    )
    if maximum_score != definition.maximum_score:
        raise ValueError(
            f"{definition.koota}.maximum_score must equal "
            f"{definition.maximum_score}"
        )

    direction = copied.get("direction")
    if not isinstance(direction, dict):
        raise TypeError(f"{definition.koota}.direction must be a mapping")
    expected_direction = dict(definition.direction)
    if direction != expected_direction:
        raise ValueError(
            f"{definition.koota}.direction must equal {expected_direction}"
        )

    errors = _validate_issue_list(copied.get("errors"), definition.koota, "errors")
    component_warnings = _validate_issue_list(
        copied.get("warnings"),
        definition.koota,
        "warnings",
    )
    warnings = [
        _prefix_component_issue(definition.koota, warning)
        for warning in component_warnings
    ]

    status = copied.get("status")
    if not isinstance(status, str):
        raise TypeError(f"{definition.koota}.status must be a string")
    if require_complete and status != "complete":
        raise ValueError(f"{definition.koota}.status must equal 'complete'")

    raw_score = copied.get("score")
    if status != "complete":
        if raw_score is not None:
            raise ValueError(f"incomplete {definition.koota} score must be None")
        if require_complete:
            raise ValueError(f"{definition.koota} result must be complete")
        return _ValidatedComponent(copied, None, False, warnings)

    score: float | None = None
    if raw_score is not None:
        score = _validate_number(raw_score, field=f"{definition.koota}.score")
        if not 0.0 <= score <= definition.maximum_score:
            raise ValueError(
                f"{definition.koota}.score must be between 0.0 and "
                f"{definition.maximum_score}"
            )

    is_complete = score is not None and not errors
    if require_complete and not is_complete:
        if errors:
            raise ValueError(f"complete {definition.koota} result must have no errors")
        raise ValueError(f"complete {definition.koota} result must have a score")
    return _ValidatedComponent(
        copied,
        score if is_complete else None,
        is_complete,
        warnings,
    )


def _validate_issue_list(
    value: MatchmakingJsonValue | None,
    koota: str,
    field: str,
) -> list[dict[str, MatchmakingJsonValue]]:
    if not isinstance(value, list):
        raise TypeError(f"{koota}.{field} must be a list")
    issues: list[dict[str, MatchmakingJsonValue]] = []
    for index, issue in enumerate(value):
        if not isinstance(issue, dict):
            raise TypeError(f"{koota}.{field}[{index}] must be a mapping")
        issue_field = issue.get("field")
        if not isinstance(issue_field, str):
            raise TypeError(f"{koota}.{field}[{index}].field must be a string")
        issues.append(issue)
    return issues


def _copy_json_mapping(
    value: Mapping[object, object],
    *,
    field: str,
) -> dict[str, MatchmakingJsonValue]:
    copied = _copy_json_value(value, field=field)
    if not isinstance(copied, dict):
        raise TypeError(f"{field} must be a mapping")
    return copied


def _copy_json_value(value: object, *, field: str) -> MatchmakingJsonValue:
    if value is None or type(value) in (str, bool, int):
        return value  # type: ignore[return-value]
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"{field} must not contain NaN or infinity")
        return value
    if isinstance(value, Mapping):
        copied: dict[str, MatchmakingJsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{field} keys must be strings")
            copied[key] = _copy_json_value(item, field=f"{field}.{key}")
        return copied
    if isinstance(value, list):
        return [
            _copy_json_value(item, field=f"{field}[{index}]")
            for index, item in enumerate(value)
        ]
    raise TypeError(f"{field} contains a non-JSON-safe value")


def _validate_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{field} must be a real number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    return numeric


def _sum_scores(score_by_koota: Mapping[str, float | None]) -> float:
    scores: list[float] = []
    for koota in ASHTAKOOTA_KOOTA_ORDER:
        score = score_by_koota.get(koota)
        if score is None:
            raise RuntimeError("Cannot aggregate an incomplete Koota score set")
        scores.append(score)
    total = math.fsum(scores)
    if not 0.0 <= total <= ASHTAKOOTA_TOTAL_MAXIMUM_SCORE:
        raise RuntimeError("Ashtakoota total is outside the canonical range")
    return total


def _normalize_raw_longitude(
    value: object,
    *,
    role: str,
) -> tuple[float | None, MatchmakingAshtakootaIssue | None]:
    try:
        return normalize_longitude(value), None  # type: ignore[arg-type]
    except (TypeError, ValueError):
        code = MOON_LONGITUDE_MISSING if value in (None, "") else MOON_LONGITUDE_INVALID
        return None, _issue(
            f"{role}.sidereal_moon_longitude",
            code,
            value,
        )


def _prefix_component_issue(
    koota: str,
    issue: Mapping[str, MatchmakingJsonValue],
) -> MatchmakingAshtakootaIssue:
    field = issue.get("field")
    if not isinstance(field, str):
        raise TypeError("component issue field must be a string")
    copied = _copy_json_mapping(issue, field=f"{koota}.warning")
    copied["field"] = f"{koota}.{field}" if field else koota
    metadata = copied.get("metadata", {})
    if not isinstance(metadata, dict):
        raise TypeError("component issue metadata must be a mapping")
    copied["metadata"] = dict(metadata)
    return copied  # type: ignore[return-value]


def _issue(
    field: str,
    code: str,
    value: object,
    *,
    metadata: Mapping[str, MatchmakingJsonValue] | None = None,
) -> MatchmakingAshtakootaIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": dict(metadata or {}),
    }


def _safe_value(value: object) -> MatchmakingJsonValue:
    if value is None or type(value) in (str, bool, int):
        return value  # type: ignore[return-value]
    if isinstance(value, Real):
        numeric = float(value)
        return numeric if math.isfinite(numeric) else None
    return str(value)


def _build_result(
    *,
    execution_mode: AshtakootaExecutionMode,
    bride_moon_longitude: float | None,
    groom_moon_longitude: float | None,
    components: list[dict[str, MatchmakingJsonValue]],
    score_by_koota: Mapping[str, float | None],
    total_score: float | None,
    errors: list[MatchmakingAshtakootaIssue],
    warnings: list[MatchmakingAshtakootaIssue],
    validated_koota_count: int,
) -> MatchmakingAshtakootaResult:
    return {
        "calculation": ASHTAKOOTA_CALCULATION_NAME,
        "status": "invalid" if errors else "complete",
        "bride_moon_longitude": bride_moon_longitude,
        "groom_moon_longitude": groom_moon_longitude,
        "koota_results": [dict(component) for component in components],
        "score_by_koota": dict(score_by_koota),
        "maximum_score_by_koota": {
            definition.koota: definition.maximum_score
            for definition in ASHTAKOOTA_KOOTA_MANIFEST
        },
        "total_score": total_score,
        "total_maximum_score": ASHTAKOOTA_TOTAL_MAXIMUM_SCORE,
        "errors": [_copy_aggregate_issue(issue, field="errors") for issue in errors],
        "warnings": [
            _copy_aggregate_issue(issue, field="warnings") for issue in warnings
        ],
        "references": [],
        "metadata": _metadata(execution_mode, validated_koota_count),
    }


def _copy_aggregate_issue(
    issue: MatchmakingAshtakootaIssue,
    *,
    field: str,
) -> MatchmakingAshtakootaIssue:
    copied = _copy_json_mapping(issue, field=field)
    return copied  # type: ignore[return-value]


def _metadata(
    execution_mode: AshtakootaExecutionMode,
    validated_koota_count: int,
) -> MatchmakingAshtakootaMetadata:
    return {
        "component": "matchmaking_ashtakoota_aggregation",
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "execution_mode": execution_mode,
        "koota_order": list(ASHTAKOOTA_KOOTA_ORDER),
        "expected_koota_count": ASHTAKOOTA_EXPECTED_KOOTA_COUNT,
        "validated_koota_count": validated_koota_count,
        "total_maximum_score": ASHTAKOOTA_TOTAL_MAXIMUM_SCORE,
        "aggregation_method": "math_fsum",
        "percentage_included": False,
        "interpretation_included": False,
        "cancellation_included": False,
    }


def _validate_manifest() -> None:
    expected_order = (
        VARNA_KOOTA_ID,
        VASHYA_KOOTA_ID,
        TARA_KOOTA_ID,
        YONI_KOOTA_ID,
        GRAHA_MAITRI_KOOTA_ID,
        GANA_KOOTA_ID,
        BHAKOOT_KOOTA_ID,
        NADI_KOOTA_ID,
    )
    order = tuple(definition.koota for definition in ASHTAKOOTA_KOOTA_MANIFEST)
    if order != expected_order or order != ASHTAKOOTA_KOOTA_ORDER:
        raise RuntimeError("Ashtakoota manifest order is not canonical")
    if len(set(order)) != ASHTAKOOTA_EXPECTED_KOOTA_COUNT:
        raise RuntimeError("Ashtakoota manifest identifiers must be unique")
    if not all(
        callable(definition.calculator) for definition in ASHTAKOOTA_KOOTA_MANIFEST
    ):
        raise RuntimeError("Ashtakoota manifest calculators must be callable")
    maximum = math.fsum(
        definition.maximum_score for definition in ASHTAKOOTA_KOOTA_MANIFEST
    )
    if maximum != ASHTAKOOTA_TOTAL_MAXIMUM_SCORE:
        raise RuntimeError("Ashtakoota manifest maximum must equal 36.0")


_validate_manifest()
