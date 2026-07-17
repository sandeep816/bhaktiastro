"""Deterministic Gana Koota classification and directional scoring."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.constants.nakshatra import NAKSHATRA_COUNT, NAKSHATRA_LIST
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MATCHMAKING_STATUSES
from backend.app.matchmaking.foundation import MatchmakingJsonValue
from backend.app.matchmaking.nakshatra import MATCHMAKING_NAKSHATRA_ISSUE_CODES
from backend.app.matchmaking.nakshatra import MatchmakingNakshatraIdentity
from backend.app.matchmaking.nakshatra import MatchmakingNakshatraIssue
from backend.app.matchmaking.nakshatra import build_nakshatra_pair_context
from backend.app.matchmaking.nakshatra import normalize_matchmaking_nakshatra

GANA_KOOTA_ID = "gana"
GANA_KOOTA_MAXIMUM_SCORE = 6.0
GANA_COMPATIBILITY_DOMAIN = "temperament"
GANA_CALCULATION_NAME = "gana_koota"

GANA_DEVA = "deva"
GANA_MANUSHYA = "manushya"
GANA_RAKSHASA = "rakshasa"
GANA_CATEGORIES = (GANA_DEVA, GANA_MANUSHYA, GANA_RAKSHASA)

GANA_SAME = "same_gana"
GANA_MIXED = "mixed_gana"

GANA_BY_NAKSHATRA_INDEX: dict[int, str] = {
    0: GANA_DEVA,
    1: GANA_MANUSHYA,
    2: GANA_RAKSHASA,
    3: GANA_MANUSHYA,
    4: GANA_DEVA,
    5: GANA_MANUSHYA,
    6: GANA_DEVA,
    7: GANA_DEVA,
    8: GANA_RAKSHASA,
    9: GANA_RAKSHASA,
    10: GANA_MANUSHYA,
    11: GANA_MANUSHYA,
    12: GANA_DEVA,
    13: GANA_RAKSHASA,
    14: GANA_DEVA,
    15: GANA_RAKSHASA,
    16: GANA_DEVA,
    17: GANA_RAKSHASA,
    18: GANA_RAKSHASA,
    19: GANA_MANUSHYA,
    20: GANA_MANUSHYA,
    21: GANA_DEVA,
    22: GANA_RAKSHASA,
    23: GANA_RAKSHASA,
    24: GANA_MANUSHYA,
    25: GANA_MANUSHYA,
    26: GANA_DEVA,
}

GANA_SCORING_MATRIX: dict[str, dict[str, float]] = {
    GANA_DEVA: {
        GANA_DEVA: 6.0,
        GANA_MANUSHYA: 6.0,
        GANA_RAKSHASA: 0.0,
    },
    GANA_MANUSHYA: {
        GANA_DEVA: 5.0,
        GANA_MANUSHYA: 6.0,
        GANA_RAKSHASA: 0.0,
    },
    GANA_RAKSHASA: {
        GANA_DEVA: 1.0,
        GANA_MANUSHYA: 0.0,
        GANA_RAKSHASA: 6.0,
    },
}

GANA_REFERENCES = (
    "https://saravali.github.io/astrology/koota_gana.html",
    "https://www.astroyogi.com/blog/gana-koota-in-kundli-matching.aspx",
    "https://www.futuresamachar.com/download/horoscope-matching-325.pdf",
    "https://www.ghvisweswara.com/wp-content/uploads/2021/11/"
    "Comparison_of_Panchangas.pdf",
)

DIRECTION_MISSING = "direction_missing"
ROLE_INVALID = "role_invalid"

MATCHMAKING_GANA_ISSUE_CODES = (
    *MATCHMAKING_NAKSHATRA_ISSUE_CODES,
    DIRECTION_MISSING,
    ROLE_INVALID,
)

_VALID_PAIR_ROLES = ("person_a", "person_b")

MatchmakingGanaIssueSeverity = Literal["error", "warning"]


class MatchmakingGanaIssue(TypedDict):
    """One localization-ready Gana Koota issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingGanaIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingGanaMetadata(TypedDict):
    """Stable metadata for Gana Koota objects."""

    component: str
    schema_version: str
    deterministic: bool
    calculation: str
    maximum_score: float
    compatibility_domain: str
    directional: bool
    symmetric: bool
    nakshatra_count: int
    index_base: int


class MatchmakingGanaIdentity(TypedDict):
    """Canonical Gana identity derived from a supplied Moon Nakshatra."""

    is_valid: bool
    nakshatra: str
    nakshatra_index: int | None
    nakshatra_pada: int | None
    source_person_id: str
    gana: str
    errors: list[MatchmakingGanaIssue]
    warnings: list[MatchmakingGanaIssue]
    metadata: MatchmakingGanaMetadata


class MatchmakingGanaRelationship(TypedDict):
    """One strict directional lookup result for two canonical Ganas."""

    bride_gana: str
    groom_gana: str
    relationship: str
    score: float


class MatchmakingGanaKootaResult(TypedDict):
    """Structured directional Gana score without compatibility judgement."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    person_a_nakshatra: MatchmakingNakshatraIdentity
    person_b_nakshatra: MatchmakingNakshatraIdentity
    direction: dict[str, str]
    bride_gana: MatchmakingGanaIdentity
    groom_gana: MatchmakingGanaIdentity
    relationship: str
    same_nakshatra: bool | None
    same_pada: bool | None
    same_gana: bool | None
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingGanaIssue]
    warnings: list[MatchmakingGanaIssue]
    references: list[str]
    metadata: MatchmakingGanaMetadata


def classify_gana(
    value: object,
    *,
    pada: object = None,
    source_person_id: object = "",
) -> MatchmakingGanaIdentity:
    """Classify one supported Nakshatra input using shared normalization."""

    identity = normalize_matchmaking_nakshatra(
        value,
        pada=pada,
        source_person_id=source_person_id,
    )
    return _classify_normalized_identity(identity)


def get_gana_relationship(
    bride_gana: str,
    groom_gana: str,
) -> MatchmakingGanaRelationship:
    """Return the strict bride-row/groom-column relationship and score.

    Raises:
        TypeError: If either category is not a string.
        ValueError: If either category is not a canonical identifier.
    """

    _validate_gana_category(bride_gana, "bride_gana")
    _validate_gana_category(groom_gana, "groom_gana")
    score = GANA_SCORING_MATRIX[bride_gana][groom_gana]
    return {
        "bride_gana": bride_gana,
        "groom_gana": groom_gana,
        "relationship": GANA_SAME if bride_gana == groom_gana else GANA_MIXED,
        "score": score,
    }


def calculate_gana_koota(
    pair: object,
    *,
    bride_role: object = None,
    groom_role: object = None,
) -> MatchmakingGanaKootaResult:
    """Calculate directional Gana Koota for explicitly assigned roles."""

    context = build_nakshatra_pair_context(pair)
    bride = _normalize_role(bride_role)
    groom = _normalize_role(groom_role)
    role_errors = _validate_pair_roles(bride, groom, bride_role, groom_role)

    identities = {
        "person_a": context["person_a"],
        "person_b": context["person_b"],
    }
    bride_gana = _empty_identity()
    groom_gana = _empty_identity()

    if not role_errors and bride and groom:
        bride_gana = _classify_normalized_identity(identities[bride])
        groom_gana = _classify_normalized_identity(identities[groom])
        errors = [
            *_prefix_issues("bride", bride_gana["errors"]),
            *_prefix_issues("groom", groom_gana["errors"]),
        ]
    else:
        errors = [_copy_issue(issue) for issue in context["errors"]]
    errors.extend(role_errors)

    score: float | None = None
    relationship = ""
    same_gana: bool | None = None
    factors: list[MatchmakingJsonValue] = []

    if not errors:
        bride_category = bride_gana["gana"]
        groom_category = groom_gana["gana"]
        lookup = get_gana_relationship(bride_category, groom_category)
        score = lookup["score"]
        relationship = lookup["relationship"]
        same_gana = bride_category == groom_category
        factors = [
            {
                "factor": "gana_directional_matrix",
                "row_role": "bride",
                "column_role": "groom",
                "bride_gana": bride_category,
                "groom_gana": groom_category,
                "relationship": relationship,
                "awarded_score": score,
            }
        ]

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": GANA_KOOTA_ID,
        "compatibility_domain": GANA_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": GANA_KOOTA_MAXIMUM_SCORE,
        "person_a_nakshatra": context["person_a"],
        "person_b_nakshatra": context["person_b"],
        "direction": {"bride_role": bride, "groom_role": groom},
        "bride_gana": bride_gana,
        "groom_gana": groom_gana,
        "relationship": relationship,
        "same_nakshatra": context["same_nakshatra"],
        "same_pada": context["same_pada"],
        "same_gana": same_gana,
        "factors": factors,
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in context["warnings"]],
        "references": list(GANA_REFERENCES),
        "metadata": _metadata("matchmaking_gana_koota"),
    }


def _classify_normalized_identity(
    identity: MatchmakingNakshatraIdentity,
) -> MatchmakingGanaIdentity:
    index = identity["index"]
    gana = GANA_BY_NAKSHATRA_INDEX.get(index) if index is not None else None
    errors = [_copy_issue(issue) for issue in identity["errors"]]

    return {
        "is_valid": not errors and gana is not None,
        "nakshatra": identity["name"],
        "nakshatra_index": index,
        "nakshatra_pada": identity["pada"],
        "source_person_id": identity["source_person_id"],
        "gana": gana if gana is not None else "",
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in identity["warnings"]],
        "metadata": _metadata("matchmaking_gana_identity"),
    }


def _empty_identity() -> MatchmakingGanaIdentity:
    return {
        "is_valid": False,
        "nakshatra": "",
        "nakshatra_index": None,
        "nakshatra_pada": None,
        "source_person_id": "",
        "gana": "",
        "errors": [],
        "warnings": [],
        "metadata": _metadata("matchmaking_gana_identity"),
    }


def _validate_gana_category(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if value not in GANA_CATEGORIES:
        raise ValueError(f"{field} must be a canonical Gana category")


def _validate_pair_roles(
    bride: str,
    groom: str,
    raw_bride: object,
    raw_groom: object,
) -> list[MatchmakingGanaIssue]:
    if not bride or not groom:
        return [_issue("direction", DIRECTION_MISSING, None)]
    if bride not in _VALID_PAIR_ROLES:
        return [_issue("bride_role", ROLE_INVALID, raw_bride)]
    if groom not in _VALID_PAIR_ROLES:
        return [_issue("groom_role", ROLE_INVALID, raw_groom)]
    if bride == groom:
        return [_issue("direction", ROLE_INVALID, {"bride_role": bride})]
    return []


def _normalize_role(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().casefold()


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingGanaIssue],
) -> list[MatchmakingGanaIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _copy_issue(issue: MatchmakingNakshatraIssue) -> MatchmakingGanaIssue:
    return {**issue, "metadata": dict(issue["metadata"])}


def _issue(field: str, code: str, value: object) -> MatchmakingGanaIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingGanaMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": GANA_CALCULATION_NAME,
        "maximum_score": GANA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": GANA_COMPATIBILITY_DOMAIN,
        "directional": True,
        "symmetric": False,
        "nakshatra_count": NAKSHATRA_COUNT,
        "index_base": 0,
    }


def _safe_value(value: object) -> MatchmakingJsonValue:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Real):
        numeric = float(value)
        if not math.isfinite(numeric):
            return None
        return int(value) if isinstance(value, Integral) else numeric
    if isinstance(value, dict):
        return {str(key): _safe_value(item) for key, item in value.items()}
    return str(value)


if tuple(GANA_BY_NAKSHATRA_INDEX) != tuple(range(NAKSHATRA_COUNT)):
    raise RuntimeError("Gana mapping must cover all canonical Nakshatra indexes")

if len(NAKSHATRA_LIST) != len(GANA_BY_NAKSHATRA_INDEX):
    raise RuntimeError("Gana mapping must match the canonical Nakshatra list")

if tuple(GANA_SCORING_MATRIX) != GANA_CATEGORIES or any(
    tuple(row) != GANA_CATEGORIES for row in GANA_SCORING_MATRIX.values()
):
    raise RuntimeError("Gana matrix rows must cover all canonical categories")
