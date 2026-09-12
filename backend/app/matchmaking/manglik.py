"""Deterministic Lagna-only Manglik classification and comparison."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Literal, TypedDict, cast

from backend.app.astronomy.planet_positions import PLANET_ORDER
from backend.app.kundali.placement import HousePlacement
from backend.app.kundali.placement import get_planet_house_placement
from backend.app.kundali.rashi import RashiResult
from backend.app.kundali.rashi import get_rashi, normalize_longitude
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MatchmakingJsonValue

MANGLIK_CALCULATION_NAME = "manglik_classification"
MANGLIK_COMPATIBILITY_CALCULATION_NAME = "manglik_compatibility"
MANGLIK_REFERENCE_POINT = "lagna"

MANGLIK_CLASSIFICATION = "manglik"
NON_MANGLIK_CLASSIFICATION = "non_manglik"
MANGLIK_CLASSIFICATIONS = (
    MANGLIK_CLASSIFICATION,
    NON_MANGLIK_CLASSIFICATION,
)

MANGLIK_HOUSES = (1, 4, 7, 8, 12)

BOTH_MANGLIK = "both_manglik"
BOTH_NON_MANGLIK = "both_non_manglik"
BRIDE_MANGLIK_GROOM_NON_MANGLIK = "bride_manglik_groom_non_manglik"
BRIDE_NON_MANGLIK_GROOM_MANGLIK = "bride_non_manglik_groom_manglik"
MANGLIK_PAIR_CLASSIFICATIONS = (
    BOTH_MANGLIK,
    BOTH_NON_MANGLIK,
    BRIDE_MANGLIK_GROOM_NON_MANGLIK,
    BRIDE_NON_MANGLIK_GROOM_MANGLIK,
)

SAME_MANGLIK_STATUS = "same_status"
MIXED_MANGLIK_STATUS = "mixed_status"
MANGLIK_COMPARISON_STATUSES = (
    SAME_MANGLIK_STATUS,
    MIXED_MANGLIK_STATUS,
)

MARS_IN_MANGLIK_HOUSE = "mars_in_manglik_house"
MARS_NOT_IN_MANGLIK_HOUSE = "mars_not_in_manglik_house"
SAME_MANGLIK_STATUS_REASON = "same_manglik_status"
MIXED_MANGLIK_STATUS_REASON = "mixed_manglik_status"

MANGLIK_INPUT_MISSING = "manglik_input_missing"
MANGLIK_INPUT_INVALID = "manglik_input_invalid"
MANGLIK_CHART_INVALID = "manglik_chart_invalid"
MANGLIK_CLASSIFICATION_INVALID = "manglik_classification_invalid"

MATCHMAKING_MANGLIK_ISSUE_CODES = (
    MANGLIK_INPUT_MISSING,
    MANGLIK_INPUT_INVALID,
    MANGLIK_CHART_INVALID,
    MANGLIK_CLASSIFICATION_INVALID,
)

_CLASSIFICATION_FIELDS = (
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

_CANONICAL_PLANETS = (*PLANET_ORDER, "ketu")
_RASHI_FIELDS = (
    "index",
    "english",
    "hindi",
    "sanskrit",
    "lord",
    "element",
    "modality",
    "start_degree",
    "end_degree",
    "degree_in_rashi",
)

ManglikIssueSeverity = Literal["error", "warning"]


class MatchmakingManglikIssue(TypedDict):
    """One localization-ready Manglik validation issue."""

    field: str
    code: str
    message_key: str
    severity: ManglikIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingManglikMetadata(TypedDict):
    """Stable metadata for one Manglik classification."""

    component: str
    schema_version: str
    deterministic: bool
    calculation: str
    house_system: str
    house_numbering: str
    reference_points: list[str]
    applicable_manglik_houses: list[int]
    classification_mode: str
    comparison_mode: str
    scoring_included: bool
    severity_included: bool
    cancellation_rules_included: bool
    divisional_charts_included: bool
    ashtakoota_recalculated: bool


class MatchmakingManglikCompatibilityMetadata(MatchmakingManglikMetadata):
    """Stable metadata for a bride/groom Manglik comparison."""

    role_order: list[str]
    same_mixed_comparison_symmetric: bool


class ManglikClassificationResult(TypedDict):
    """Canonical binary Manglik classification for one person."""

    calculation: str
    status: str
    classification: str
    reference_point: str
    lagna_sidereal_longitude: float | None
    mars_sidereal_longitude: float | None
    lagna_rashi_index: int | None
    mars_rashi_index: int | None
    mars_house: int | None
    applicable_manglik_houses: list[int]
    reason: str
    errors: list[MatchmakingManglikIssue]
    warnings: list[MatchmakingManglikIssue]
    references: list[str]
    metadata: MatchmakingManglikMetadata


class ManglikCompatibilityResult(TypedDict):
    """Structured bride/groom Manglik comparison without a score."""

    calculation: str
    status: str
    bride_manglik: ManglikClassificationResult
    groom_manglik: ManglikClassificationResult
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
    errors: list[MatchmakingManglikIssue]
    warnings: list[MatchmakingManglikIssue]
    references: list[str]
    metadata: MatchmakingManglikCompatibilityMetadata


def classify_manglik(
    *,
    lagna_sidereal_longitude: object = None,
    mars_sidereal_longitude: object = None,
) -> ManglikClassificationResult:
    """Classify Mars's canonical whole-sign house from the Lagna only."""

    lagna_longitude, lagna_issue = _normalize_input_longitude(
        lagna_sidereal_longitude,
        "lagna_sidereal_longitude",
    )
    mars_longitude, mars_issue = _normalize_input_longitude(
        mars_sidereal_longitude,
        "mars_sidereal_longitude",
    )
    errors = [issue for issue in (lagna_issue, mars_issue) if issue is not None]
    if errors:
        return _invalid_classification(
            errors,
            lagna_sidereal_longitude=lagna_longitude,
            mars_sidereal_longitude=mars_longitude,
        )

    if lagna_longitude is None or mars_longitude is None:
        raise RuntimeError("Validated Manglik longitudes must be available")

    lagna_rashi = get_rashi(lagna_longitude)
    placement = get_planet_house_placement(
        lagna_rashi["index"],
        mars_longitude,
    )
    mars_house = placement["house_number"]
    classification = (
        MANGLIK_CLASSIFICATION
        if mars_house in MANGLIK_HOUSES
        else NON_MANGLIK_CLASSIFICATION
    )
    reason = (
        MARS_IN_MANGLIK_HOUSE
        if classification == MANGLIK_CLASSIFICATION
        else MARS_NOT_IN_MANGLIK_HOUSE
    )

    return {
        "calculation": MANGLIK_CALCULATION_NAME,
        "status": "complete",
        "classification": classification,
        "reference_point": MANGLIK_REFERENCE_POINT,
        "lagna_sidereal_longitude": lagna_longitude,
        "mars_sidereal_longitude": mars_longitude,
        "lagna_rashi_index": lagna_rashi["index"],
        "mars_rashi_index": placement["rashi_index"],
        "mars_house": mars_house,
        "applicable_manglik_houses": list(MANGLIK_HOUSES),
        "reason": reason,
        "errors": [],
        "warnings": [],
        "references": [],
        "metadata": _classification_metadata(),
    }


def classify_manglik_from_chart(
    *,
    chart: object = None,
) -> ManglikClassificationResult:
    """Classify an existing Kundali-shaped mapping without recalculation."""

    chart_values = _validate_chart(chart)
    errors = chart_values["errors"]
    if errors:
        return _invalid_classification(errors)

    lagna_longitude = chart_values["lagna_sidereal_longitude"]
    mars_longitude = chart_values["mars_sidereal_longitude"]
    if lagna_longitude is None or mars_longitude is None:
        raise RuntimeError("Validated Kundali chart longitudes must be available")

    result = classify_manglik(
        lagna_sidereal_longitude=lagna_longitude,
        mars_sidereal_longitude=mars_longitude,
    )
    if result["status"] != "complete":
        raise RuntimeError("Validated Kundali chart produced an invalid result")

    consistency_errors = _validate_chart_consistency(
        chart_values["lagna"],
        chart_values["mars"],
        result,
    )
    if consistency_errors:
        return _invalid_classification(
            consistency_errors,
            lagna_sidereal_longitude=result["lagna_sidereal_longitude"],
            mars_sidereal_longitude=result["mars_sidereal_longitude"],
        )
    return result


def compare_manglik_classifications(
    *,
    bride: object,
    groom: object,
) -> ManglikCompatibilityResult:
    """Compare two strictly revalidated precomputed Manglik identities."""

    bride_identity, bride_errors = _revalidate_classification(bride, "bride")
    groom_identity, groom_errors = _revalidate_classification(groom, "groom")
    errors = [*bride_errors, *groom_errors]

    if errors:
        return _compatibility_result(
            bride_identity=bride_identity,
            groom_identity=groom_identity,
            errors=errors,
        )

    bride_classification = bride_identity["classification"]
    groom_classification = groom_identity["classification"]
    if bride_classification == groom_classification:
        comparison_status = SAME_MANGLIK_STATUS
        comparison_reason = SAME_MANGLIK_STATUS_REASON
        pair_classification = (
            BOTH_MANGLIK
            if bride_classification == MANGLIK_CLASSIFICATION
            else BOTH_NON_MANGLIK
        )
    else:
        comparison_status = MIXED_MANGLIK_STATUS
        comparison_reason = MIXED_MANGLIK_STATUS_REASON
        pair_classification = (
            BRIDE_MANGLIK_GROOM_NON_MANGLIK
            if bride_classification == MANGLIK_CLASSIFICATION
            else BRIDE_NON_MANGLIK_GROOM_MANGLIK
        )

    return _compatibility_result(
        bride_identity=bride_identity,
        groom_identity=groom_identity,
        pair_classification=pair_classification,
        comparison_status=comparison_status,
        reasons=[
            bride_identity["reason"],
            groom_identity["reason"],
            comparison_reason,
        ],
    )


class _ChartValues(TypedDict):
    lagna_sidereal_longitude: object | None
    mars_sidereal_longitude: object | None
    lagna: Mapping[str, object]
    mars: Mapping[str, object]
    errors: list[MatchmakingManglikIssue]


def _validate_chart(chart: object) -> _ChartValues:
    empty: dict[str, object] = {}
    if chart is None:
        return {
            "lagna_sidereal_longitude": None,
            "mars_sidereal_longitude": None,
            "lagna": empty,
            "mars": {},
            "errors": [_issue("chart", MANGLIK_INPUT_MISSING, None)],
        }
    if not isinstance(chart, Mapping):
        return {
            "lagna_sidereal_longitude": None,
            "mars_sidereal_longitude": None,
            "lagna": empty,
            "mars": {},
            "errors": [_issue("chart", MANGLIK_CHART_INVALID, chart)],
        }

    errors: list[MatchmakingManglikIssue] = []
    lagna_value = chart.get("lagna")
    lagna_is_mapping = isinstance(lagna_value, Mapping)
    if lagna_value is None:
        errors.append(_issue("chart.lagna", MANGLIK_INPUT_MISSING, None))
        lagna: Mapping[str, object] = {}
    elif not isinstance(lagna_value, Mapping):
        errors.append(_issue("chart.lagna", MANGLIK_CHART_INVALID, lagna_value))
        lagna = {}
    else:
        lagna = cast(Mapping[str, object], lagna_value)

    lagna_longitude = lagna.get("sidereal_longitude")
    if lagna_is_mapping and "sidereal_longitude" not in lagna:
        errors.append(
            _issue(
                "chart.lagna.sidereal_longitude",
                MANGLIK_INPUT_MISSING,
                None,
            )
        )
    elif lagna_is_mapping:
        _, issue = _normalize_input_longitude(
            lagna_longitude,
            "chart.lagna.sidereal_longitude",
        )
        if issue is not None:
            errors.append(issue)
    if lagna_is_mapping and "rashi_index" not in lagna:
        errors.append(_issue("chart.lagna.rashi_index", MANGLIK_INPUT_MISSING, None))
    elif lagna_is_mapping and not _is_house_or_rashi_index(lagna.get("rashi_index")):
        errors.append(
            _issue(
                "chart.lagna.rashi_index",
                MANGLIK_INPUT_INVALID,
                lagna.get("rashi_index"),
            )
        )

    planets_value = chart.get("planets")
    mars: Mapping[str, object] = {}
    if planets_value is None:
        errors.append(_issue("chart.planets", MANGLIK_INPUT_MISSING, None))
        planets: Sequence[object] = []
    elif not isinstance(planets_value, Sequence) or isinstance(
        planets_value, (str, bytes)
    ):
        errors.append(_issue("chart.planets", MANGLIK_CHART_INVALID, planets_value))
        planets = []
    else:
        planets = planets_value

    mars_candidates: list[Mapping[str, object]] = []
    for index, planet_value in enumerate(planets):
        field = f"chart.planets.{index}"
        if not isinstance(planet_value, Mapping):
            errors.append(_issue(field, MANGLIK_CHART_INVALID, planet_value))
            continue
        planet = planet_value.get("planet")
        if not isinstance(planet, str) or planet not in _CANONICAL_PLANETS:
            errors.append(_issue(f"{field}.planet", MANGLIK_CHART_INVALID, planet))
            continue
        if planet == "mars":
            mars_candidates.append(cast(Mapping[str, object], planet_value))

    if not mars_candidates:
        errors.append(_issue("chart.planets.mars", MANGLIK_INPUT_MISSING, None))
    elif len(mars_candidates) > 1:
        errors.append(
            _issue(
                "chart.planets.mars",
                MANGLIK_CHART_INVALID,
                len(mars_candidates),
            )
        )
    else:
        mars = mars_candidates[0]

    mars_longitude = mars.get("sidereal_longitude")
    if mars and "sidereal_longitude" not in mars:
        errors.append(
            _issue(
                "chart.planets.mars.sidereal_longitude",
                MANGLIK_INPUT_MISSING,
                None,
            )
        )
    elif mars:
        _, issue = _normalize_input_longitude(
            mars_longitude,
            "chart.planets.mars.sidereal_longitude",
        )
        if issue is not None:
            errors.append(issue)

    return {
        "lagna_sidereal_longitude": lagna_longitude,
        "mars_sidereal_longitude": mars_longitude,
        "lagna": lagna,
        "mars": mars,
        "errors": errors,
    }


def _validate_chart_consistency(
    lagna: Mapping[str, object],
    mars: Mapping[str, object],
    result: ManglikClassificationResult,
) -> list[MatchmakingManglikIssue]:
    errors: list[MatchmakingManglikIssue] = []
    lagna_longitude = result["lagna_sidereal_longitude"]
    mars_longitude = result["mars_sidereal_longitude"]
    if lagna_longitude is None or mars_longitude is None:
        raise RuntimeError("Complete Manglik result must contain longitudes")

    lagna_rashi = get_rashi(lagna_longitude)
    lagna_index = result["lagna_rashi_index"]
    if lagna.get("rashi_index") != lagna_index:
        errors.append(
            _issue(
                "chart.lagna.rashi_index",
                MANGLIK_CHART_INVALID,
                lagna.get("rashi_index"),
            )
        )
    if "rashi" in lagna:
        errors.extend(
            _validate_rashi_mapping(
                lagna.get("rashi"),
                lagna_rashi,
                "chart.lagna.rashi",
            )
        )
    if "rashi_degree" in lagna and not _numeric_matches(
        lagna.get("rashi_degree"), lagna_rashi["degree_in_rashi"]
    ):
        errors.append(
            _issue(
                "chart.lagna.rashi_degree",
                MANGLIK_CHART_INVALID,
                lagna.get("rashi_degree"),
            )
        )

    placement = get_planet_house_placement(cast(int, lagna_index), mars_longitude)
    errors.extend(_validate_optional_mars_placement(mars, placement))
    return errors


def _validate_optional_mars_placement(
    mars: Mapping[str, object],
    placement: HousePlacement,
) -> list[MatchmakingManglikIssue]:
    errors: list[MatchmakingManglikIssue] = []
    expected_fields: tuple[tuple[str, object], ...] = (
        ("rashi_index", placement["rashi_index"]),
        ("rashi_degree", placement["rashi_degree"]),
        ("house_index", placement["house_index"]),
        ("house_number", placement["house_number"]),
    )
    for field, expected in expected_fields:
        if field not in mars:
            continue
        value = mars.get(field)
        matches = (
            _numeric_matches(value, expected)
            if field == "rashi_degree"
            else _is_integral_match(value, expected)
        )
        if not matches:
            errors.append(
                _issue(
                    f"chart.planets.mars.{field}",
                    MANGLIK_CHART_INVALID,
                    value,
                )
            )
    if "rashi" in mars:
        errors.extend(
            _validate_rashi_mapping(
                mars.get("rashi"),
                placement["rashi"],
                "chart.planets.mars.rashi",
            )
        )
    return errors


def _validate_rashi_mapping(
    value: object,
    expected: RashiResult,
    field: str,
) -> list[MatchmakingManglikIssue]:
    if not isinstance(value, Mapping):
        return [_issue(field, MANGLIK_CHART_INVALID, value)]
    for key in _RASHI_FIELDS:
        if key not in value or value.get(key) != expected[key]:
            return [_issue(f"{field}.{key}", MANGLIK_CHART_INVALID, value.get(key))]
    return []


def _revalidate_classification(
    value: object,
    role: str,
) -> tuple[ManglikClassificationResult, list[MatchmakingManglikIssue]]:
    field = f"{role}.manglik"
    issue = _classification_contract_issue(value, field)
    if issue is not None:
        return _invalid_classification([issue]), [issue]

    source = cast(Mapping[str, object], value)
    lagna_longitude = source["lagna_sidereal_longitude"]
    mars_longitude = source["mars_sidereal_longitude"]
    expected = classify_manglik(
        lagna_sidereal_longitude=lagna_longitude,
        mars_sidereal_longitude=mars_longitude,
    )
    if expected["status"] != "complete" or not _classification_matches(
        source, expected
    ):
        issue = _issue(field, MANGLIK_CLASSIFICATION_INVALID, value)
        return _invalid_classification([issue]), [issue]
    return _copy_classification(expected), []


def _classification_contract_issue(
    value: object,
    field: str,
) -> MatchmakingManglikIssue | None:
    if not isinstance(value, Mapping):
        return _issue(field, MANGLIK_CLASSIFICATION_INVALID, value)
    if tuple(value.keys()) != _CLASSIFICATION_FIELDS:
        return _issue(field, MANGLIK_CLASSIFICATION_INVALID, value)
    if not _is_json_safe(value):
        return _issue(field, MANGLIK_CLASSIFICATION_INVALID, None)
    if value.get("status") != "complete":
        return _issue(field, MANGLIK_CLASSIFICATION_INVALID, value)
    return None


def _classification_matches(
    source: Mapping[str, object],
    expected: ManglikClassificationResult,
) -> bool:
    for field in _CLASSIFICATION_FIELDS:
        if field == "metadata":
            metadata = source.get(field)
            if not isinstance(metadata, Mapping):
                return False
            if any(metadata.get(key) != item for key, item in expected[field].items()):
                return False
            continue
        if source.get(field) != expected[field]:
            return False
    return True


def _compatibility_result(
    *,
    bride_identity: ManglikClassificationResult,
    groom_identity: ManglikClassificationResult,
    pair_classification: str = "",
    comparison_status: str = "",
    reasons: list[str] | None = None,
    errors: list[MatchmakingManglikIssue] | None = None,
) -> ManglikCompatibilityResult:
    result_errors = [_copy_issue(issue) for issue in (errors or [])]
    complete = not result_errors
    return {
        "calculation": MANGLIK_COMPATIBILITY_CALCULATION_NAME,
        "status": "complete" if complete else "invalid",
        "bride_manglik": _copy_classification(bride_identity),
        "groom_manglik": _copy_classification(groom_identity),
        "bride_classification": bride_identity["classification"] if complete else "",
        "groom_classification": groom_identity["classification"] if complete else "",
        "bride_reference_point": bride_identity["reference_point"] if complete else "",
        "groom_reference_point": groom_identity["reference_point"] if complete else "",
        "bride_mars_house": bride_identity["mars_house"] if complete else None,
        "groom_mars_house": groom_identity["mars_house"] if complete else None,
        "applicable_manglik_houses": list(MANGLIK_HOUSES),
        "pair_classification": pair_classification if complete else "",
        "comparison_status": comparison_status if complete else "",
        "reasons": list(reasons or []) if complete else [],
        "errors": result_errors,
        "warnings": [],
        "references": [],
        "metadata": _compatibility_metadata(),
    }


def _invalid_classification(
    errors: Sequence[MatchmakingManglikIssue],
    *,
    lagna_sidereal_longitude: float | None = None,
    mars_sidereal_longitude: float | None = None,
) -> ManglikClassificationResult:
    return {
        "calculation": MANGLIK_CALCULATION_NAME,
        "status": "invalid",
        "classification": "",
        "reference_point": (
            MANGLIK_REFERENCE_POINT if lagna_sidereal_longitude is not None else ""
        ),
        "lagna_sidereal_longitude": lagna_sidereal_longitude,
        "mars_sidereal_longitude": mars_sidereal_longitude,
        "lagna_rashi_index": None,
        "mars_rashi_index": None,
        "mars_house": None,
        "applicable_manglik_houses": list(MANGLIK_HOUSES),
        "reason": "",
        "errors": [_copy_issue(issue) for issue in errors],
        "warnings": [],
        "references": [],
        "metadata": _classification_metadata(),
    }


def _copy_classification(
    value: ManglikClassificationResult,
) -> ManglikClassificationResult:
    return {
        "calculation": value["calculation"],
        "status": value["status"],
        "classification": value["classification"],
        "reference_point": value["reference_point"],
        "lagna_sidereal_longitude": value["lagna_sidereal_longitude"],
        "mars_sidereal_longitude": value["mars_sidereal_longitude"],
        "lagna_rashi_index": value["lagna_rashi_index"],
        "mars_rashi_index": value["mars_rashi_index"],
        "mars_house": value["mars_house"],
        "applicable_manglik_houses": list(value["applicable_manglik_houses"]),
        "reason": value["reason"],
        "errors": [_copy_issue(issue) for issue in value["errors"]],
        "warnings": [_copy_issue(issue) for issue in value["warnings"]],
        "references": list(value["references"]),
        "metadata": _copy_classification_metadata(value["metadata"]),
    }


def _normalize_input_longitude(
    value: object,
    field: str,
) -> tuple[float | None, MatchmakingManglikIssue | None]:
    if value is None or value == "":
        return None, _issue(field, MANGLIK_INPUT_MISSING, value)
    try:
        return normalize_longitude(value), None  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None, _issue(field, MANGLIK_INPUT_INVALID, value)


def _is_house_or_rashi_index(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Integral)
        and 1 <= int(value) <= 12
    )


def _is_integral_match(value: object, expected: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Integral)
        and int(value) == expected
    )


def _numeric_matches(value: object, expected: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Real)
        and math.isfinite(float(value))
        and float(value) == expected
    )


def _issue(field: str, code: str, value: object) -> MatchmakingManglikIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _copy_issue(issue: MatchmakingManglikIssue) -> MatchmakingManglikIssue:
    return {
        "field": issue["field"],
        "code": issue["code"],
        "message_key": issue["message_key"],
        "severity": issue["severity"],
        "value": _safe_value(issue["value"]),
        "metadata": {
            str(key): _safe_value(value) for key, value in issue["metadata"].items()
        },
    }


def _classification_metadata() -> MatchmakingManglikMetadata:
    return {
        "component": "matchmaking_manglik_classification",
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": MANGLIK_CALCULATION_NAME,
        "house_system": "whole_sign",
        "house_numbering": "one_based",
        "reference_points": [MANGLIK_REFERENCE_POINT],
        "applicable_manglik_houses": list(MANGLIK_HOUSES),
        "classification_mode": "binary",
        "comparison_mode": "structured_only",
        "scoring_included": False,
        "severity_included": False,
        "cancellation_rules_included": False,
        "divisional_charts_included": False,
        "ashtakoota_recalculated": False,
    }


def _compatibility_metadata() -> MatchmakingManglikCompatibilityMetadata:
    metadata: MatchmakingManglikCompatibilityMetadata = {
        **_classification_metadata(),
        "component": "matchmaking_manglik_compatibility",
        "calculation": MANGLIK_COMPATIBILITY_CALCULATION_NAME,
        "role_order": ["bride", "groom"],
        "same_mixed_comparison_symmetric": True,
    }
    return metadata


def _copy_classification_metadata(
    value: MatchmakingManglikMetadata,
) -> MatchmakingManglikMetadata:
    return {
        "component": value["component"],
        "schema_version": value["schema_version"],
        "deterministic": value["deterministic"],
        "calculation": value["calculation"],
        "house_system": value["house_system"],
        "house_numbering": value["house_numbering"],
        "reference_points": list(value["reference_points"]),
        "applicable_manglik_houses": list(value["applicable_manglik_houses"]),
        "classification_mode": value["classification_mode"],
        "comparison_mode": value["comparison_mode"],
        "scoring_included": value["scoring_included"],
        "severity_included": value["severity_included"],
        "cancellation_rules_included": value["cancellation_rules_included"],
        "divisional_charts_included": value["divisional_charts_included"],
        "ashtakoota_recalculated": value["ashtakoota_recalculated"],
    }


def _safe_value(value: object) -> MatchmakingJsonValue:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Real):
        numeric = float(value)
        if not math.isfinite(numeric):
            return None
        return int(value) if isinstance(value, Integral) else numeric
    if isinstance(value, Mapping):
        return {str(key): _safe_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_safe_value(item) for item in value]
    return type(value).__name__


def _is_json_safe(value: object) -> bool:
    if value is None or isinstance(value, (str, bool)):
        return True
    if isinstance(value, Real):
        return math.isfinite(float(value))
    if isinstance(value, list):
        return all(_is_json_safe(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _is_json_safe(item) for key, item in value.items()
        )
    return False
