"""Deterministic Varna Koota foundation for matchmaking."""

from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.constants.rashi import RASHI_COUNT, RASHI_LIST
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MATCHMAKING_STATUSES
from backend.app.matchmaking.foundation import MatchmakingJsonValue

MATCHMAKING_RASHI_INDEX_BASE = 1
VARNA_KOOTA_ID = "varna"
VARNA_KOOTA_MAXIMUM_SCORE = 1.0
VARNA_CALCULATION_NAME = "varna_koota"

VARNA_BRAHMIN = "brahmin"
VARNA_KSHATRIYA = "kshatriya"
VARNA_VAISHYA = "vaishya"
VARNA_SHUDRA = "shudra"

VARNA_RANKS: dict[str, int] = {
    VARNA_SHUDRA: 1,
    VARNA_VAISHYA: 2,
    VARNA_KSHATRIYA: 3,
    VARNA_BRAHMIN: 4,
}

RASHI_ELEMENT_TO_VARNA: dict[str, str] = {
    "Water": VARNA_BRAHMIN,
    "Fire": VARNA_KSHATRIYA,
    "Earth": VARNA_VAISHYA,
    "Air": VARNA_SHUDRA,
}
RASHI_VARNA_BY_INDEX: dict[int, str] = {
    rashi.index: RASHI_ELEMENT_TO_VARNA[rashi.element] for rashi in RASHI_LIST
}

RASHI_MISSING = "rashi_missing"
RASHI_INVALID = "rashi_invalid"
RASHI_INDEX_OUT_OF_RANGE = "rashi_index_out_of_range"
VARNA_UNRESOLVED = "varna_unresolved"
DIRECTION_MISSING = "direction_missing"
ROLE_INVALID = "role_invalid"

MATCHMAKING_VARNA_ISSUE_CODES = (
    RASHI_MISSING,
    RASHI_INVALID,
    RASHI_INDEX_OUT_OF_RANGE,
    VARNA_UNRESOLVED,
    DIRECTION_MISSING,
    ROLE_INVALID,
)

_VALID_ROLES = ("person_a", "person_b")
_RASHI_BY_INDEX = {rashi.index: rashi for rashi in RASHI_LIST}

MatchmakingVarnaIssueSeverity = Literal["error", "warning"]


class MatchmakingVarnaIssue(TypedDict):
    """One localization-ready Varna Koota issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingVarnaIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingVarnaMetadata(TypedDict):
    """Stable metadata for Varna Koota objects."""

    component: str
    schema_version: str
    deterministic: bool
    calculation: str
    maximum_score: float
    directional: bool


class MatchmakingVarnaIdentity(TypedDict):
    """Resolved Varna identity for one supplied Rashi."""

    is_valid: bool
    rashi: str
    rashi_index: int | None
    varna: str
    varna_rank: int | None
    source_person_id: str
    errors: list[MatchmakingVarnaIssue]
    warnings: list[MatchmakingVarnaIssue]
    metadata: MatchmakingVarnaMetadata


class MatchmakingVarnaKootaResult(TypedDict):
    """Structured Varna Koota score without final compatibility judgement."""

    koota: str
    status: str
    score: float | None
    maximum_score: float
    person_a_varna: MatchmakingVarnaIdentity
    person_b_varna: MatchmakingVarnaIdentity
    direction: dict[str, str]
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingVarnaIssue]
    warnings: list[MatchmakingVarnaIssue]
    references: list[str]
    metadata: MatchmakingVarnaMetadata


def _normalize_name(value: str) -> str:
    return " ".join(value.strip().casefold().split())


_RASHI_NAME_TO_INDEX = {
    normalized_name: rashi.index
    for rashi in RASHI_LIST
    for normalized_name in {
        _normalize_name(rashi.english),
        _normalize_name(rashi.hindi),
        _normalize_name(rashi.sanskrit),
    }
}


def resolve_varna(
    value: object,
    *,
    source_person_id: object = "",
) -> MatchmakingVarnaIdentity:
    """Resolve supplied Rashi data into a canonical Varna identity."""

    raw_rashi: object
    raw_person_id: object

    if isinstance(value, Mapping):
        raw_rashi = _extract_rashi_value(value)
        raw_person_id = _first_present(
            value,
            ("person_id", "source_person_id"),
            default=source_person_id,
        )
    else:
        raw_rashi = value
        raw_person_id = source_person_id

    errors: list[MatchmakingVarnaIssue] = []
    rashi_index = _resolve_rashi_index(raw_rashi, errors)
    varna = RASHI_VARNA_BY_INDEX.get(rashi_index) if rashi_index is not None else None

    if rashi_index is not None and varna is None:
        errors.append(_issue("rashi", VARNA_UNRESOLVED, raw_rashi))

    rashi_name = _RASHI_BY_INDEX[rashi_index].sanskrit if rashi_index is not None else ""
    return {
        "is_valid": not errors,
        "rashi": rashi_name,
        "rashi_index": rashi_index,
        "varna": varna or "",
        "varna_rank": VARNA_RANKS.get(varna) if varna is not None else None,
        "source_person_id": _normalize_key(raw_person_id),
        "errors": errors,
        "warnings": [],
        "metadata": _metadata("matchmaking_varna_identity"),
    }


def calculate_varna_koota(
    pair: object,
    *,
    subject_role: object = None,
    comparison_role: object = None,
) -> MatchmakingVarnaKootaResult:
    """Calculate directional Varna Koota from supplied Rashi data only.

    The caller must provide the scoring direction explicitly. The score is
    ``1`` when the comparison role's Varna rank is greater than or equal to
    the subject role's Varna rank; otherwise the score is ``0``. The function
    does not infer gender, marital roles, or missing Rashi values.
    """

    person_a, person_b = _extract_pair_people(pair)
    person_a_varna = resolve_varna(person_a)
    person_b_varna = resolve_varna(person_b)

    errors = [
        *_prefix_issues("person_a", person_a_varna["errors"]),
        *_prefix_issues("person_b", person_b_varna["errors"]),
    ]

    subject = _normalize_role(subject_role)
    comparison = _normalize_role(comparison_role)
    if not subject or not comparison:
        errors.append(_issue("direction", DIRECTION_MISSING, None))
    elif subject not in _VALID_ROLES:
        errors.append(_issue("subject_role", ROLE_INVALID, subject_role))
    elif comparison not in _VALID_ROLES:
        errors.append(_issue("comparison_role", ROLE_INVALID, comparison_role))
    elif subject == comparison:
        errors.append(_issue("direction", ROLE_INVALID, {"subject_role": subject}))

    direction = {
        "subject_role": subject,
        "comparison_role": comparison,
    }

    score: float | None = None
    factors: list[MatchmakingJsonValue] = []
    if not errors and subject and comparison:
        identities = {
            "person_a": person_a_varna,
            "person_b": person_b_varna,
        }
        subject_identity = identities[subject]
        comparison_identity = identities[comparison]
        subject_rank = subject_identity["varna_rank"]
        comparison_rank = comparison_identity["varna_rank"]
        matched = (
            subject_rank is not None
            and comparison_rank is not None
            and comparison_rank >= subject_rank
        )
        score = VARNA_KOOTA_MAXIMUM_SCORE if matched else 0.0
        factors.append(
            {
                "factor": "varna_rank_condition",
                "subject_role": subject,
                "comparison_role": comparison,
                "subject_varna": subject_identity["varna"],
                "comparison_varna": comparison_identity["varna"],
                "subject_rank": subject_rank,
                "comparison_rank": comparison_rank,
                "matched": matched,
            }
        )

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": VARNA_KOOTA_ID,
        "status": status,
        "score": score,
        "maximum_score": VARNA_KOOTA_MAXIMUM_SCORE,
        "person_a_varna": person_a_varna,
        "person_b_varna": person_b_varna,
        "direction": direction,
        "factors": factors,
        "errors": errors,
        "warnings": [],
        "references": [],
        "metadata": _metadata("matchmaking_varna_koota"),
    }


def _extract_rashi_value(value: Mapping[object, object]) -> object:
    rashi = value.get("rashi")
    if isinstance(rashi, Mapping):
        return rashi
    if rashi not in (None, ""):
        return rashi
    return _first_present(value, ("rashi_index", "index", "sanskrit", "english", "hindi"))


def _extract_pair_people(value: object) -> tuple[object, object]:
    if not isinstance(value, Mapping):
        return {}, {}

    normalized_value = value.get("normalized_value")
    source = normalized_value if isinstance(normalized_value, Mapping) else value
    return source.get("person_a", {}), source.get("person_b", {})


def _resolve_rashi_index(
    value: object,
    errors: list[MatchmakingVarnaIssue],
) -> int | None:
    if value in (None, ""):
        errors.append(_issue("rashi", RASHI_MISSING, value))
        return None

    if isinstance(value, bool):
        errors.append(_issue("rashi", RASHI_INVALID, value))
        return None

    if isinstance(value, Integral):
        index = int(value)
        if 1 <= index <= RASHI_COUNT:
            return index
        errors.append(_issue("rashi", RASHI_INDEX_OUT_OF_RANGE, value))
        return None

    if isinstance(value, str):
        normalized_name = _normalize_name(value)
        if not normalized_name:
            errors.append(_issue("rashi", RASHI_MISSING, value))
            return None
        try:
            return _RASHI_NAME_TO_INDEX[normalized_name]
        except KeyError:
            errors.append(_issue("rashi", RASHI_INVALID, value))
            return None

    if isinstance(value, Mapping):
        nested = _extract_rashi_value(value)
        if nested is value:
            errors.append(_issue("rashi", RASHI_INVALID, value))
            return None
        return _resolve_rashi_index(nested, errors)

    errors.append(_issue("rashi", RASHI_INVALID, value))
    return None


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


def _normalize_role(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().casefold()


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingVarnaIssue],
) -> list[MatchmakingVarnaIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _issue(field: str, code: str, value: object) -> MatchmakingVarnaIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingVarnaMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": VARNA_CALCULATION_NAME,
        "maximum_score": VARNA_KOOTA_MAXIMUM_SCORE,
        "directional": True,
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
    return str(value)
