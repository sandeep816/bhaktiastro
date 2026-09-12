"""Deterministic composition of Ashtakoota and Manglik compatibility results."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Literal, TypedDict, cast

from backend.app.matchmaking.ashtakoota import (
    ASHTAKOOTA_CALCULATION_NAME,
    ASHTAKOOTA_EXPECTED_KOOTA_COUNT,
    ASHTAKOOTA_KOOTA_ORDER,
    ASHTAKOOTA_TOTAL_MAXIMUM_SCORE,
    MatchmakingAshtakootaResult,
    aggregate_ashtakoota_results,
    calculate_ashtakoota,
)
from backend.app.matchmaking.foundation import (
    MATCHMAKING_SCHEMA_VERSION,
    MatchmakingJsonValue,
)
from backend.app.matchmaking.manglik import (
    MANGLIK_COMPATIBILITY_CALCULATION_NAME,
    MANGLIK_HOUSES,
    ManglikClassificationResult,
    ManglikCompatibilityResult,
    classify_manglik,
    compare_manglik_classifications,
)

COMPATIBILITY_REPORT_SCHEMA_VERSION = MATCHMAKING_SCHEMA_VERSION
COMPATIBILITY_REPORT_TYPE = "matchmaking_compatibility_report"
COMPATIBILITY_REPORT_COMPONENT_ORDER = ("ashtakoota", "manglik")
COMPATIBILITY_REPORT_SECTIONS = (
    "report_metadata",
    "input_summary",
    "ashtakoota_summary",
    "koota_breakdown",
    "manglik_summary",
    "validation_status",
    "errors",
    "warnings",
    "notes",
)
COMPATIBILITY_REPORT_NOTES = (
    "structured_report_only",
    "no_overall_compatibility_label",
    "no_combined_ashtakoota_manglik_score",
    "no_manglik_cancellation",
    "no_prediction_advice_or_remedies",
)

_ASHTAKOOTA_FIELDS = (
    "calculation",
    "status",
    "bride_moon_longitude",
    "groom_moon_longitude",
    "koota_results",
    "score_by_koota",
    "maximum_score_by_koota",
    "total_score",
    "total_maximum_score",
    "errors",
    "warnings",
    "references",
    "metadata",
)
_MANGLIK_COMPATIBILITY_FIELDS = (
    "calculation",
    "status",
    "bride_manglik",
    "groom_manglik",
    "bride_classification",
    "groom_classification",
    "bride_reference_point",
    "groom_reference_point",
    "bride_mars_house",
    "groom_mars_house",
    "applicable_manglik_houses",
    "pair_classification",
    "comparison_status",
    "reasons",
    "errors",
    "warnings",
    "references",
    "metadata",
)
_MANGLIK_CLASSIFICATION_FIELDS = (
    "calculation",
    "status",
    "classification",
    "reference_point",
    "lagna_sidereal_longitude",
    "mars_sidereal_longitude",
    "lagna_rashi_index",
    "mars_rashi_index",
    "mars_house",
    "applicable_manglik_houses",
    "reason",
    "errors",
    "warnings",
    "references",
    "metadata",
)
_REPORT_FIELDS = (
    "schema_version",
    "report_type",
    "status",
    "bride",
    "groom",
    "ashtakoota",
    "koota_results",
    "manglik",
    "validation",
    "errors",
    "warnings",
    "notes",
    "sections",
    "metadata",
)

CompatibilityReportStatus = Literal["complete", "invalid"]
CompatibilityReportIssueSeverity = Literal["error", "warning"]


class MatchmakingCompatibilityReportIssue(TypedDict):
    """One localization-ready copied component issue."""

    field: str
    code: str
    message_key: str
    severity: CompatibilityReportIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingCompatibilityPersonSummary(TypedDict):
    """Normalized factual input audit for one report role."""

    role: str
    moon_sidereal_longitude: float | None
    lagna_sidereal_longitude: float | None
    mars_sidereal_longitude: float | None
    manglik_reference_point: str


class MatchmakingCompatibilityAshtakootaSummary(TypedDict):
    """Report-level view of the authoritative Ashtakoota aggregate."""

    calculation: str
    status: str
    bride_moon_longitude: float | None
    groom_moon_longitude: float | None
    total_score: float | None
    total_maximum_score: float
    score_by_koota: dict[str, float | None]
    maximum_score_by_koota: dict[str, float]
    component_status_by_koota: dict[str, str]
    koota_order: list[str]
    execution_mode: str
    percentage_included: bool


class MatchmakingCompatibilityManglikSummary(TypedDict):
    """Report-level view of the authoritative Manglik comparison."""

    calculation: str
    status: str
    bride_classification: str
    groom_classification: str
    bride_reference_point: str
    groom_reference_point: str
    bride_mars_house: int | None
    groom_mars_house: int | None
    applicable_manglik_houses: list[int]
    pair_classification: str
    comparison_status: str
    reasons: list[str]
    validation_status: str


class MatchmakingCompatibilityValidation(TypedDict):
    """Technical validation state without compatibility interpretation."""

    status: CompatibilityReportStatus
    is_valid: bool
    component_statuses: dict[str, str]
    validated_components: list[str]
    expected_component_count: int
    validated_component_count: int
    error_count: int
    warning_count: int


class MatchmakingCompatibilityReportMetadata(TypedDict):
    """Stable report schema and exclusion metadata."""

    component: str
    schema_version: str
    deterministic: bool
    report_type: str
    section_order: list[str]
    expected_section_count: int
    component_order: list[str]
    expected_component_count: int
    validated_component_count: int
    source_calculations: list[str]
    structured_only: bool
    overall_compatibility_label_included: bool
    combined_score_included: bool
    percentage_included: bool
    interpretation_included: bool
    recommendations_included: bool
    remedies_included: bool
    rendering_included: bool


class MatchmakingCompatibilityReport(TypedDict):
    """Canonical structured compatibility report."""

    schema_version: str
    report_type: str
    status: CompatibilityReportStatus
    bride: MatchmakingCompatibilityPersonSummary
    groom: MatchmakingCompatibilityPersonSummary
    ashtakoota: MatchmakingCompatibilityAshtakootaSummary
    koota_results: list[dict[str, MatchmakingJsonValue]]
    manglik: MatchmakingCompatibilityManglikSummary
    validation: MatchmakingCompatibilityValidation
    errors: list[MatchmakingCompatibilityReportIssue]
    warnings: list[MatchmakingCompatibilityReportIssue]
    notes: list[str]
    sections: list[str]
    metadata: MatchmakingCompatibilityReportMetadata


def compose_compatibility_report(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
    bride_lagna_longitude: object = None,
    groom_lagna_longitude: object = None,
    bride_mars_longitude: object = None,
    groom_mars_longitude: object = None,
) -> MatchmakingCompatibilityReport:
    """Compose a safe report by running the public calculators in order."""

    ashtakoota = calculate_ashtakoota(
        bride_moon_longitude=bride_moon_longitude,
        groom_moon_longitude=groom_moon_longitude,
    )
    bride = classify_manglik(
        lagna_sidereal_longitude=bride_lagna_longitude,
        mars_sidereal_longitude=bride_mars_longitude,
    )
    groom = classify_manglik(
        lagna_sidereal_longitude=groom_lagna_longitude,
        mars_sidereal_longitude=groom_mars_longitude,
    )
    manglik = compare_manglik_classifications(bride=bride, groom=groom)

    _validate_raw_ashtakoota(ashtakoota)
    _validate_raw_classification(bride, "bride")
    _validate_raw_classification(groom, "groom")
    _validate_raw_manglik(manglik)
    return _build_report(
        ashtakoota=ashtakoota,
        manglik=manglik,
        bride_identity=bride,
        groom_identity=groom,
    )


def compose_compatibility_report_from_results(
    *,
    ashtakoota: object,
    manglik: object,
) -> MatchmakingCompatibilityReport:
    """Strictly revalidate completed components and compose a report."""

    ashtakoota_mapping = _require_mapping(ashtakoota, "ashtakoota")
    _reject_mutable_aliases(ashtakoota_mapping, "ashtakoota")
    validated_ashtakoota = _strict_ashtakoota(ashtakoota_mapping)

    manglik_mapping = _require_mapping(manglik, "manglik")
    _reject_mutable_aliases(manglik_mapping, "manglik")
    _reject_cross_component_aliases(ashtakoota_mapping, manglik_mapping)
    validated_manglik = _strict_manglik(manglik_mapping)
    return _build_report(
        ashtakoota=validated_ashtakoota,
        manglik=validated_manglik,
        bride_identity=validated_manglik["bride_manglik"],
        groom_identity=validated_manglik["groom_manglik"],
    )


def serialize_compatibility_report(
    *,
    report: object,
) -> dict[str, MatchmakingJsonValue]:
    """Strictly validate and independently copy one complete report."""

    source = _require_mapping(report, "report")
    _reject_mutable_aliases(source, "report")
    _require_exact_fields(source, _REPORT_FIELDS, "report")
    copied = _copy_json_mapping(source, "report")
    if copied.get("status") != "complete":
        raise ValueError("report.status must equal 'complete'")
    if copied.get("schema_version") != COMPATIBILITY_REPORT_SCHEMA_VERSION:
        raise ValueError("report.schema_version is invalid")
    if copied.get("report_type") != COMPATIBILITY_REPORT_TYPE:
        raise ValueError("report.report_type is invalid")

    ashtakoota_summary = _require_dict(copied.get("ashtakoota"), "report.ashtakoota")
    koota_results = copied.get("koota_results")
    if not isinstance(koota_results, list):
        raise TypeError("report.koota_results must be a list")
    regenerated_ashtakoota = aggregate_ashtakoota_results(
        koota_results,
        bride_moon_longitude=ashtakoota_summary.get("bride_moon_longitude"),
        groom_moon_longitude=ashtakoota_summary.get("groom_moon_longitude"),
    )
    execution_mode = ashtakoota_summary.get("execution_mode")
    if execution_mode not in ("raw_calculators", "precomputed_results"):
        raise ValueError("report.ashtakoota.execution_mode is invalid")
    regenerated_ashtakoota["metadata"]["execution_mode"] = cast(str, execution_mode)

    bride_summary = _require_dict(copied.get("bride"), "report.bride")
    groom_summary = _require_dict(copied.get("groom"), "report.groom")
    bride = classify_manglik(
        lagna_sidereal_longitude=bride_summary.get("lagna_sidereal_longitude"),
        mars_sidereal_longitude=bride_summary.get("mars_sidereal_longitude"),
    )
    groom = classify_manglik(
        lagna_sidereal_longitude=groom_summary.get("lagna_sidereal_longitude"),
        mars_sidereal_longitude=groom_summary.get("mars_sidereal_longitude"),
    )
    regenerated_manglik = compare_manglik_classifications(bride=bride, groom=groom)
    expected = _build_report(
        ashtakoota=regenerated_ashtakoota,
        manglik=regenerated_manglik,
        bride_identity=bride,
        groom_identity=groom,
    )
    if copied != expected:
        raise ValueError("report does not match authoritative component results")
    return _copy_json_mapping(expected, "report")


def _strict_ashtakoota(
    source: Mapping[object, object],
) -> MatchmakingAshtakootaResult:
    _require_exact_fields(source, _ASHTAKOOTA_FIELDS, "ashtakoota")
    copied = _copy_json_mapping(source, "ashtakoota")
    if copied.get("calculation") != ASHTAKOOTA_CALCULATION_NAME:
        raise ValueError("ashtakoota.calculation is invalid")
    if copied.get("status") != "complete":
        raise ValueError("ashtakoota.status must equal 'complete'")
    if copied.get("errors") != []:
        raise ValueError("ashtakoota.errors must be empty")
    metadata = _require_dict(copied.get("metadata"), "ashtakoota.metadata")
    if metadata.get("schema_version") != MATCHMAKING_SCHEMA_VERSION:
        raise ValueError("ashtakoota.metadata.schema_version is invalid")
    execution_mode = metadata.get("execution_mode")
    if execution_mode not in ("raw_calculators", "precomputed_results"):
        raise ValueError("ashtakoota.metadata.execution_mode is invalid")
    results = copied.get("koota_results")
    if not isinstance(results, list):
        raise TypeError("ashtakoota.koota_results must be a list")
    if [
        item.get("koota") if isinstance(item, dict) else None for item in results
    ] != list(ASHTAKOOTA_KOOTA_ORDER):
        raise ValueError("ashtakoota.koota_results order is invalid")
    regenerated = aggregate_ashtakoota_results(
        results,
        bride_moon_longitude=copied.get("bride_moon_longitude"),
        groom_moon_longitude=copied.get("groom_moon_longitude"),
    )
    regenerated["metadata"]["execution_mode"] = cast(str, execution_mode)
    if copied != regenerated:
        raise ValueError("ashtakoota does not match authoritative aggregation")
    return regenerated


def _strict_manglik(source: Mapping[object, object]) -> ManglikCompatibilityResult:
    _require_exact_fields(source, _MANGLIK_COMPATIBILITY_FIELDS, "manglik")
    copied = _copy_json_mapping(source, "manglik")
    if copied.get("calculation") != MANGLIK_COMPATIBILITY_CALCULATION_NAME:
        raise ValueError("manglik.calculation is invalid")
    if copied.get("status") != "complete":
        raise ValueError("manglik.status must equal 'complete'")
    if copied.get("errors") != []:
        raise ValueError("manglik.errors must be empty")
    metadata = _require_dict(copied.get("metadata"), "manglik.metadata")
    if metadata.get("schema_version") != MATCHMAKING_SCHEMA_VERSION:
        raise ValueError("manglik.metadata.schema_version is invalid")
    bride = copied.get("bride_manglik")
    groom = copied.get("groom_manglik")
    regenerated = compare_manglik_classifications(bride=bride, groom=groom)
    if regenerated["status"] != "complete" or copied != regenerated:
        raise ValueError("manglik does not match authoritative comparison")
    return regenerated


def _validate_raw_ashtakoota(value: object) -> None:
    source = _require_mapping(value, "ashtakoota")
    _require_exact_fields(source, _ASHTAKOOTA_FIELDS, "ashtakoota")
    copied = _copy_json_mapping(source, "ashtakoota")
    if copied.get("calculation") != ASHTAKOOTA_CALCULATION_NAME:
        raise ValueError("ashtakoota.calculation is invalid")
    if copied.get("status") not in ("complete", "invalid"):
        raise ValueError("ashtakoota.status is invalid")
    metadata = _require_dict(copied.get("metadata"), "ashtakoota.metadata")
    if metadata.get("schema_version") != MATCHMAKING_SCHEMA_VERSION:
        raise ValueError("ashtakoota.metadata.schema_version is invalid")


def _validate_raw_classification(value: object, role: str) -> None:
    source = _require_mapping(value, f"manglik.{role}")
    _require_exact_fields(source, _MANGLIK_CLASSIFICATION_FIELDS, f"manglik.{role}")
    copied = _copy_json_mapping(source, f"manglik.{role}")
    if copied.get("status") not in ("complete", "invalid"):
        raise ValueError(f"manglik.{role}.status is invalid")
    metadata = _require_dict(copied.get("metadata"), f"manglik.{role}.metadata")
    if metadata.get("schema_version") != MATCHMAKING_SCHEMA_VERSION:
        raise ValueError(f"manglik.{role}.metadata.schema_version is invalid")


def _validate_raw_manglik(value: object) -> None:
    source = _require_mapping(value, "manglik")
    _require_exact_fields(source, _MANGLIK_COMPATIBILITY_FIELDS, "manglik")
    copied = _copy_json_mapping(source, "manglik")
    if copied.get("calculation") != MANGLIK_COMPATIBILITY_CALCULATION_NAME:
        raise ValueError("manglik.calculation is invalid")
    if copied.get("status") not in ("complete", "invalid"):
        raise ValueError("manglik.status is invalid")
    metadata = _require_dict(copied.get("metadata"), "manglik.metadata")
    if metadata.get("schema_version") != MATCHMAKING_SCHEMA_VERSION:
        raise ValueError("manglik.metadata.schema_version is invalid")


def _build_report(
    *,
    ashtakoota: Mapping[str, object],
    manglik: Mapping[str, object],
    bride_identity: Mapping[str, object],
    groom_identity: Mapping[str, object],
) -> MatchmakingCompatibilityReport:
    ashtakoota_status = cast(str, ashtakoota["status"])
    manglik_status = cast(str, manglik["status"])
    validated_components = [
        component
        for component, status in (
            ("ashtakoota", ashtakoota_status),
            ("manglik", manglik_status),
        )
        if status == "complete"
    ]
    errors = [
        *_prefixed_issues(ashtakoota.get("errors"), "ashtakoota"),
        *_prefixed_issues(bride_identity.get("errors"), "manglik.bride"),
        *_prefixed_issues(groom_identity.get("errors"), "manglik.groom"),
        *_prefixed_issues(manglik.get("errors"), "manglik.comparison"),
    ]
    warnings = [
        *_prefixed_issues(ashtakoota.get("warnings"), "ashtakoota"),
        *_prefixed_issues(bride_identity.get("warnings"), "manglik.bride"),
        *_prefixed_issues(groom_identity.get("warnings"), "manglik.groom"),
        *_prefixed_issues(manglik.get("warnings"), "manglik.comparison"),
    ]
    complete = (
        ashtakoota_status == "complete" and manglik_status == "complete" and not errors
    )
    status: CompatibilityReportStatus = "complete" if complete else "invalid"
    koota_results = ashtakoota.get("koota_results")
    if not isinstance(koota_results, list):
        raise TypeError("ashtakoota.koota_results must be a list")
    score_by = _require_dict(
        ashtakoota.get("score_by_koota"), "ashtakoota.score_by_koota"
    )
    maximum_by = _require_dict(
        ashtakoota.get("maximum_score_by_koota"),
        "ashtakoota.maximum_score_by_koota",
    )
    metadata = _require_dict(ashtakoota.get("metadata"), "ashtakoota.metadata")

    report: MatchmakingCompatibilityReport = {
        "schema_version": COMPATIBILITY_REPORT_SCHEMA_VERSION,
        "report_type": COMPATIBILITY_REPORT_TYPE,
        "status": status,
        "bride": _person_summary(
            "bride", ashtakoota.get("bride_moon_longitude"), bride_identity
        ),
        "groom": _person_summary(
            "groom", ashtakoota.get("groom_moon_longitude"), groom_identity
        ),
        "ashtakoota": {
            "calculation": cast(str, ashtakoota["calculation"]),
            "status": ashtakoota_status,
            "bride_moon_longitude": cast(
                float | None, ashtakoota.get("bride_moon_longitude")
            ),
            "groom_moon_longitude": cast(
                float | None, ashtakoota.get("groom_moon_longitude")
            ),
            "total_score": cast(float | None, ashtakoota.get("total_score")),
            "total_maximum_score": cast(float, ashtakoota["total_maximum_score"]),
            "score_by_koota": cast(
                dict[str, float | None], _copy_json_mapping(score_by, "score_by_koota")
            ),
            "maximum_score_by_koota": cast(
                dict[str, float],
                _copy_json_mapping(maximum_by, "maximum_score_by_koota"),
            ),
            "component_status_by_koota": {
                cast(str, component["koota"]): cast(str, component["status"])
                for component in koota_results
                if isinstance(component, dict)
            },
            "koota_order": list(cast(list[str], metadata.get("koota_order", []))),
            "execution_mode": cast(str, metadata.get("execution_mode", "")),
            "percentage_included": cast(
                bool, metadata.get("percentage_included", False)
            ),
        },
        "koota_results": cast(
            list[dict[str, MatchmakingJsonValue]],
            _copy_json_value(koota_results, "koota_results"),
        ),
        "manglik": _manglik_summary(manglik),
        "validation": {
            "status": status,
            "is_valid": complete,
            "component_statuses": {
                "ashtakoota": ashtakoota_status,
                "manglik": manglik_status,
            },
            "validated_components": list(validated_components),
            "expected_component_count": 2,
            "validated_component_count": len(validated_components),
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
        "notes": list(COMPATIBILITY_REPORT_NOTES),
        "sections": list(COMPATIBILITY_REPORT_SECTIONS),
        "metadata": _report_metadata(len(validated_components)),
    }
    return report


def _person_summary(
    role: str,
    moon_longitude: object,
    identity: Mapping[str, object],
) -> MatchmakingCompatibilityPersonSummary:
    return {
        "role": role,
        "moon_sidereal_longitude": cast(float | None, moon_longitude),
        "lagna_sidereal_longitude": cast(
            float | None, identity.get("lagna_sidereal_longitude")
        ),
        "mars_sidereal_longitude": cast(
            float | None, identity.get("mars_sidereal_longitude")
        ),
        "manglik_reference_point": cast(str, identity.get("reference_point", "")),
    }


def _manglik_summary(
    value: Mapping[str, object],
) -> MatchmakingCompatibilityManglikSummary:
    houses = value.get("applicable_manglik_houses")
    reasons = value.get("reasons")
    if not isinstance(houses, list) or not isinstance(reasons, list):
        raise TypeError("manglik houses and reasons must be lists")
    return {
        "calculation": cast(str, value["calculation"]),
        "status": cast(str, value["status"]),
        "bride_classification": cast(str, value.get("bride_classification", "")),
        "groom_classification": cast(str, value.get("groom_classification", "")),
        "bride_reference_point": cast(str, value.get("bride_reference_point", "")),
        "groom_reference_point": cast(str, value.get("groom_reference_point", "")),
        "bride_mars_house": cast(int | None, value.get("bride_mars_house")),
        "groom_mars_house": cast(int | None, value.get("groom_mars_house")),
        "applicable_manglik_houses": list(cast(list[int], houses)),
        "pair_classification": cast(str, value.get("pair_classification", "")),
        "comparison_status": cast(str, value.get("comparison_status", "")),
        "reasons": list(cast(list[str], reasons)),
        "validation_status": cast(str, value["status"]),
    }


def _report_metadata(validated_count: int) -> MatchmakingCompatibilityReportMetadata:
    return {
        "component": "matchmaking_compatibility_report",
        "schema_version": COMPATIBILITY_REPORT_SCHEMA_VERSION,
        "deterministic": True,
        "report_type": COMPATIBILITY_REPORT_TYPE,
        "section_order": list(COMPATIBILITY_REPORT_SECTIONS),
        "expected_section_count": len(COMPATIBILITY_REPORT_SECTIONS),
        "component_order": list(COMPATIBILITY_REPORT_COMPONENT_ORDER),
        "expected_component_count": len(COMPATIBILITY_REPORT_COMPONENT_ORDER),
        "validated_component_count": validated_count,
        "source_calculations": [
            ASHTAKOOTA_CALCULATION_NAME,
            MANGLIK_COMPATIBILITY_CALCULATION_NAME,
        ],
        "structured_only": True,
        "overall_compatibility_label_included": False,
        "combined_score_included": False,
        "percentage_included": False,
        "interpretation_included": False,
        "recommendations_included": False,
        "remedies_included": False,
        "rendering_included": False,
    }


def _prefixed_issues(
    value: object, prefix: str
) -> list[MatchmakingCompatibilityReportIssue]:
    if not isinstance(value, list):
        raise TypeError(f"{prefix} issues must be a list")
    copied: list[MatchmakingCompatibilityReportIssue] = []
    for index, issue in enumerate(value):
        if not isinstance(issue, Mapping):
            raise TypeError(f"{prefix} issue {index} must be a mapping")
        issue_copy = _copy_json_mapping(issue, f"{prefix}[{index}]")
        field = issue_copy.get("field")
        if not isinstance(field, str):
            raise TypeError(f"{prefix} issue field must be a string")
        issue_copy["field"] = f"{prefix}.{field}" if field else prefix
        copied.append(cast(MatchmakingCompatibilityReportIssue, issue_copy))
    return copied


def _require_mapping(value: object, field: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a mapping")
    return value


def _require_dict(value: object, field: str) -> dict[str, MatchmakingJsonValue]:
    if not isinstance(value, dict):
        raise TypeError(f"{field} must be a mapping")
    return value


def _require_exact_fields(
    value: Mapping[object, object], expected: tuple[str, ...], field: str
) -> None:
    if tuple(value.keys()) != expected:
        raise ValueError(f"{field} fields or field order are invalid")


def _copy_json_mapping(
    value: Mapping[object, object], field: str
) -> dict[str, MatchmakingJsonValue]:
    copied = _copy_json_value(value, field)
    if not isinstance(copied, dict):
        raise TypeError(f"{field} must be a mapping")
    return copied


def _copy_json_value(value: object, field: str) -> MatchmakingJsonValue:
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
                raise ValueError(f"{field} contains a non-string key")
            copied[key] = _copy_json_value(item, f"{field}.{key}")
        return copied
    if isinstance(value, list):
        return [
            _copy_json_value(item, f"{field}[{index}]")
            for index, item in enumerate(value)
        ]
    raise ValueError(f"{field} contains a non-JSON-safe value")


def _reject_mutable_aliases(value: Mapping[object, object], field: str) -> None:
    seen: dict[int, str] = {}

    def visit(item: object, path: str) -> None:
        if isinstance(item, (Mapping, list)):
            identity = id(item)
            if identity in seen:
                raise ValueError(
                    f"{field} contains mutable aliasing at {seen[identity]} and {path}"
                )
            seen[identity] = path
            if isinstance(item, Mapping):
                for key, child in item.items():
                    visit(child, f"{path}.{key}")
            else:
                for index, child in enumerate(item):
                    visit(child, f"{path}[{index}]")

    visit(value, field)


def _reject_cross_component_aliases(
    ashtakoota: Mapping[object, object], manglik: Mapping[object, object]
) -> None:
    left: set[int] = set()

    def collect(item: object, identities: set[int]) -> None:
        if isinstance(item, (Mapping, list)):
            identities.add(id(item))
            children = item.values() if isinstance(item, Mapping) else item
            for child in children:
                collect(child, identities)

    collect(ashtakoota, left)
    right: set[int] = set()
    collect(manglik, right)
    if left & right:
        raise ValueError("component inputs contain cross-component mutable aliasing")


assert ASHTAKOOTA_EXPECTED_KOOTA_COUNT == len(ASHTAKOOTA_KOOTA_ORDER)
assert ASHTAKOOTA_TOTAL_MAXIMUM_SCORE == 36.0
assert tuple(MANGLIK_HOUSES) == (1, 4, 7, 8, 12)
