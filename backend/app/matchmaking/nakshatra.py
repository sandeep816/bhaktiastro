"""Nakshatra identity and pair-context helpers for matchmaking foundations."""

from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.constants.nakshatra import NAKSHATRA_COUNT, NAKSHATRA_LIST
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MatchmakingJsonValue

MATCHMAKING_NAKSHATRA_INDEX_BASE = 0
MATCHMAKING_NAKSHATRA_CALCULATION_SCOPE = "nakshatra_pair_context_preparation"

NAKSHATRA_MISSING = "nakshatra_missing"
NAKSHATRA_INVALID = "nakshatra_invalid"
NAKSHATRA_INDEX_OUT_OF_RANGE = "nakshatra_index_out_of_range"
NAKSHATRA_PADA_OUT_OF_RANGE = "nakshatra_pada_out_of_range"

MATCHMAKING_NAKSHATRA_ISSUE_CODES = (
    NAKSHATRA_MISSING,
    NAKSHATRA_INVALID,
    NAKSHATRA_INDEX_OUT_OF_RANGE,
    NAKSHATRA_PADA_OUT_OF_RANGE,
)

MatchmakingNakshatraIssueSeverity = Literal["error", "warning"]


class MatchmakingNakshatraIssue(TypedDict):
    """One localization-ready Nakshatra context issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingNakshatraIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingNakshatraMetadata(TypedDict):
    """Stable metadata for Nakshatra matchmaking context objects."""

    component: str
    schema_version: str
    deterministic: bool
    nakshatra_count: int
    index_base: int
    calculation_scope: str


class MatchmakingNakshatraIdentity(TypedDict):
    """Normalized Nakshatra identity using zero-based canonical indexes."""

    is_valid: bool
    name: str
    index: int | None
    pada: int | None
    source_person_id: str
    errors: list[MatchmakingNakshatraIssue]
    warnings: list[MatchmakingNakshatraIssue]
    metadata: MatchmakingNakshatraMetadata


class MatchmakingNakshatraPairContext(TypedDict):
    """Ordered Nakshatra pair context without compatibility scoring."""

    is_valid: bool
    person_a: MatchmakingNakshatraIdentity
    person_b: MatchmakingNakshatraIdentity
    forward_distance: int | None
    reverse_distance: int | None
    same_nakshatra: bool | None
    same_pada: bool | None
    errors: list[MatchmakingNakshatraIssue]
    warnings: list[MatchmakingNakshatraIssue]
    metadata: MatchmakingNakshatraMetadata


def _normalize_name(value: str) -> str:
    return " ".join(value.strip().casefold().split())


_NAKSHATRA_BY_INDEX = {nakshatra.index: nakshatra for nakshatra in NAKSHATRA_LIST}
_NAKSHATRA_NAME_TO_INDEX = {
    normalized_name: nakshatra.index
    for nakshatra in NAKSHATRA_LIST
    for normalized_name in {
        _normalize_name(nakshatra.name_en),
        _normalize_name(nakshatra.name_hi),
        _normalize_name(nakshatra.name_sa),
    }
}


def normalize_matchmaking_nakshatra(
    value: object,
    *,
    pada: object = None,
    source_person_id: object = "",
) -> MatchmakingNakshatraIdentity:
    """Normalize supplied Nakshatra data into one canonical identity.

    The canonical index convention is zero-based and follows
    ``backend.app.constants.nakshatra.NAKSHATRA_LIST``: Ashwini is index ``0``
    and Revati is index ``26``. Missing or invalid values are reported as
    deterministic issues rather than derived from chart calculations.
    """

    raw_nakshatra: object
    raw_pada: object
    raw_person_id: object

    if isinstance(value, Mapping):
        raw_nakshatra = _first_present(
            value,
            ("nakshatra", "nakshatra_name", "name", "nakshatra_index", "index"),
        )
        raw_pada = _first_present(value, ("nakshatra_pada", "pada"), default=pada)
        raw_person_id = _first_present(
            value,
            ("person_id", "source_person_id"),
            default=source_person_id,
        )
    else:
        raw_nakshatra = value
        raw_pada = pada
        raw_person_id = source_person_id

    errors: list[MatchmakingNakshatraIssue] = []
    index = _resolve_nakshatra_index(raw_nakshatra, errors)
    normalized_pada = _resolve_pada(raw_pada, errors)

    name = _NAKSHATRA_BY_INDEX[index].name_en if index is not None else ""
    return {
        "is_valid": not errors,
        "name": name,
        "index": index,
        "pada": normalized_pada,
        "source_person_id": _normalize_key(raw_person_id),
        "errors": errors,
        "warnings": [],
        "metadata": _metadata("matchmaking_nakshatra_identity"),
    }


def calculate_nakshatra_distance(index_from: object, index_to: object) -> int | None:
    """Return zero-based circular distance between two Nakshatra indexes."""

    if not _is_valid_index(index_from) or not _is_valid_index(index_to):
        return None
    return (int(index_to) - int(index_from)) % NAKSHATRA_COUNT


def build_nakshatra_pair_context(
    pair_or_person_a: object,
    person_b: object | None = None,
) -> MatchmakingNakshatraPairContext:
    """Build ordered Nakshatra pair context from supplied person structures."""

    if person_b is None:
        person_a_source, person_b_source = _extract_pair_people(pair_or_person_a)
    else:
        person_a_source, person_b_source = pair_or_person_a, person_b

    person_a_identity = normalize_matchmaking_nakshatra(person_a_source)
    person_b_identity = normalize_matchmaking_nakshatra(person_b_source)

    errors = [
        *_prefix_issues("person_a", person_a_identity["errors"]),
        *_prefix_issues("person_b", person_b_identity["errors"]),
    ]

    forward_distance: int | None = None
    reverse_distance: int | None = None
    same_nakshatra: bool | None = None
    same_pada: bool | None = None

    if person_a_identity["index"] is not None and person_b_identity["index"] is not None:
        forward_distance = calculate_nakshatra_distance(
            person_a_identity["index"],
            person_b_identity["index"],
        )
        reverse_distance = calculate_nakshatra_distance(
            person_b_identity["index"],
            person_a_identity["index"],
        )
        same_nakshatra = person_a_identity["index"] == person_b_identity["index"]
        same_pada = (
            person_a_identity["pada"] is not None
            and person_a_identity["pada"] == person_b_identity["pada"]
        )

    return {
        "is_valid": not errors,
        "person_a": person_a_identity,
        "person_b": person_b_identity,
        "forward_distance": forward_distance,
        "reverse_distance": reverse_distance,
        "same_nakshatra": same_nakshatra,
        "same_pada": same_pada,
        "errors": errors,
        "warnings": [],
        "metadata": _metadata("matchmaking_nakshatra_pair_context"),
    }


def _extract_pair_people(value: object) -> tuple[object, object]:
    if not isinstance(value, Mapping):
        return {}, {}

    normalized_value = value.get("normalized_value")
    source = normalized_value if isinstance(normalized_value, Mapping) else value
    return source.get("person_a", {}), source.get("person_b", {})


def _resolve_nakshatra_index(
    value: object,
    errors: list[MatchmakingNakshatraIssue],
) -> int | None:
    if value in (None, ""):
        errors.append(_issue("nakshatra", NAKSHATRA_MISSING, value))
        return None

    if isinstance(value, bool):
        errors.append(_issue("nakshatra", NAKSHATRA_INVALID, value))
        return None

    if isinstance(value, Integral):
        index = int(value)
        if _is_valid_index(index):
            return index
        errors.append(_issue("nakshatra", NAKSHATRA_INDEX_OUT_OF_RANGE, value))
        return None

    if isinstance(value, str):
        normalized_name = _normalize_name(value)
        if not normalized_name:
            errors.append(_issue("nakshatra", NAKSHATRA_MISSING, value))
            return None
        try:
            return _NAKSHATRA_NAME_TO_INDEX[normalized_name]
        except KeyError:
            errors.append(_issue("nakshatra", NAKSHATRA_INVALID, value))
            return None

    errors.append(_issue("nakshatra", NAKSHATRA_INVALID, value))
    return None


def _resolve_pada(
    value: object,
    errors: list[MatchmakingNakshatraIssue],
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Integral):
        errors.append(_issue("pada", NAKSHATRA_PADA_OUT_OF_RANGE, value))
        return None

    normalized = int(value)
    if not 1 <= normalized <= 4:
        errors.append(_issue("pada", NAKSHATRA_PADA_OUT_OF_RANGE, value))
        return None
    return normalized


def _is_valid_index(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Integral)
        and 0 <= int(value) < NAKSHATRA_COUNT
    )


def _first_present(
    source: Mapping[object, object],
    keys: tuple[str, ...],
    *,
    default: object = None,
) -> object:
    for key in keys:
        if key in source:
            return source[key]
    return default


def _normalize_key(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().casefold()


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingNakshatraIssue],
) -> list[MatchmakingNakshatraIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _issue(field: str, code: str, value: object) -> MatchmakingNakshatraIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingNakshatraMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "nakshatra_count": NAKSHATRA_COUNT,
        "index_base": MATCHMAKING_NAKSHATRA_INDEX_BASE,
        "calculation_scope": MATCHMAKING_NAKSHATRA_CALCULATION_SCOPE,
    }


def _safe_value(value: object) -> MatchmakingJsonValue:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Real):
        numeric = float(value)
        if not math.isfinite(numeric):
            return None
        return int(value) if isinstance(value, Integral) else numeric
    return str(value)
