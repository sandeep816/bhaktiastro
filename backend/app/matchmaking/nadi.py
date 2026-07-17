"""Deterministic Nadi Koota classification and symmetric scoring."""

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

NADI_KOOTA_ID = "nadi"
NADI_KOOTA_MAXIMUM_SCORE = 8.0
NADI_COMPATIBILITY_DOMAIN = "physiological_compatibility"
NADI_CALCULATION_NAME = "nadi_koota"

NADI_ADI = "adi"
NADI_MADHYA = "madhya"
NADI_ANTYA = "antya"
NADI_CATEGORIES = (NADI_ADI, NADI_MADHYA, NADI_ANTYA)

NADI_SAME = "same_nadi"
NADI_DIFFERENT = "different_nadi"

NADI_BY_NAKSHATRA_INDEX: dict[int, str] = {
    0: NADI_ADI,
    1: NADI_MADHYA,
    2: NADI_ANTYA,
    3: NADI_ANTYA,
    4: NADI_MADHYA,
    5: NADI_ADI,
    6: NADI_ADI,
    7: NADI_MADHYA,
    8: NADI_ANTYA,
    9: NADI_ANTYA,
    10: NADI_MADHYA,
    11: NADI_ADI,
    12: NADI_ADI,
    13: NADI_MADHYA,
    14: NADI_ANTYA,
    15: NADI_ANTYA,
    16: NADI_MADHYA,
    17: NADI_ADI,
    18: NADI_ADI,
    19: NADI_MADHYA,
    20: NADI_ANTYA,
    21: NADI_ANTYA,
    22: NADI_MADHYA,
    23: NADI_ADI,
    24: NADI_ADI,
    25: NADI_MADHYA,
    26: NADI_ANTYA,
}

NADI_SCORING_MATRIX: dict[str, dict[str, float]] = {
    NADI_ADI: {NADI_ADI: 0.0, NADI_MADHYA: 8.0, NADI_ANTYA: 8.0},
    NADI_MADHYA: {NADI_ADI: 8.0, NADI_MADHYA: 0.0, NADI_ANTYA: 8.0},
    NADI_ANTYA: {NADI_ADI: 8.0, NADI_MADHYA: 8.0, NADI_ANTYA: 0.0},
}

NADI_REFERENCES = (
    "https://saravali.github.io/astrology/koota_nadi.html",
    "https://www.futuresamachar.com/en/nadi-dosha-and-married-life-1163",
    "https://www.futuresamachar.com/download/horoscope-matching-325.pdf",
    "https://www.astroyogi.com/blog/nadi-koota-in-kundli-matching.aspx",
)

DIRECTION_MISSING = "direction_missing"
ROLE_INVALID = "role_invalid"

MATCHMAKING_NADI_ISSUE_CODES = (
    *MATCHMAKING_NAKSHATRA_ISSUE_CODES,
    DIRECTION_MISSING,
    ROLE_INVALID,
)

_VALID_PAIR_ROLES = ("person_a", "person_b")

MatchmakingNadiIssueSeverity = Literal["error", "warning"]


class MatchmakingNadiIssue(TypedDict):
    """One localization-ready Nadi Koota issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingNadiIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingNadiMetadata(TypedDict):
    """Stable metadata for Nadi Koota objects."""

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


class MatchmakingNadiIdentity(TypedDict):
    """Canonical Nadi identity derived from a supplied Moon Nakshatra."""

    is_valid: bool
    nakshatra: str
    nakshatra_index: int | None
    nakshatra_pada: int | None
    source_person_id: str
    nadi: str
    errors: list[MatchmakingNadiIssue]
    warnings: list[MatchmakingNadiIssue]
    metadata: MatchmakingNadiMetadata


class MatchmakingNadiRelationship(TypedDict):
    """One strict symmetric lookup result for two canonical Nadis."""

    bride_nadi: str
    groom_nadi: str
    relationship: str
    same_nadi: bool
    nadi_dosha: bool
    score: float


class MatchmakingNadiKootaResult(TypedDict):
    """Structured symmetric Nadi score without cancellation or judgement."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    person_a_nakshatra: MatchmakingNakshatraIdentity
    person_b_nakshatra: MatchmakingNakshatraIdentity
    direction: dict[str, str]
    bride_nadi: MatchmakingNadiIdentity
    groom_nadi: MatchmakingNadiIdentity
    relationship: str
    same_nakshatra: bool | None
    same_pada: bool | None
    same_nadi: bool | None
    nadi_dosha: bool | None
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingNadiIssue]
    warnings: list[MatchmakingNadiIssue]
    references: list[str]
    metadata: MatchmakingNadiMetadata


def classify_nadi(
    value: object,
    *,
    pada: object = None,
    source_person_id: object = "",
) -> MatchmakingNadiIdentity:
    """Classify one supported Nakshatra input using shared normalization."""

    identity = normalize_matchmaking_nakshatra(
        value,
        pada=pada,
        source_person_id=source_person_id,
    )
    return _classify_normalized_identity(identity)


def get_nadi_relationship(
    bride_nadi: str,
    groom_nadi: str,
) -> MatchmakingNadiRelationship:
    """Return the strict symmetric Nadi relationship and score.

    Raises:
        TypeError: If either category is not a string.
        ValueError: If either category is not a canonical identifier.
    """

    _validate_nadi_category(bride_nadi, "bride_nadi")
    _validate_nadi_category(groom_nadi, "groom_nadi")
    same_nadi = bride_nadi == groom_nadi
    return {
        "bride_nadi": bride_nadi,
        "groom_nadi": groom_nadi,
        "relationship": NADI_SAME if same_nadi else NADI_DIFFERENT,
        "same_nadi": same_nadi,
        "nadi_dosha": same_nadi,
        "score": NADI_SCORING_MATRIX[bride_nadi][groom_nadi],
    }


def calculate_nadi_koota(
    pair: object,
    *,
    bride_role: object = None,
    groom_role: object = None,
) -> MatchmakingNadiKootaResult:
    """Calculate symmetric Nadi Koota for explicitly assigned pair roles."""

    context = build_nakshatra_pair_context(pair)
    bride = _normalize_role(bride_role)
    groom = _normalize_role(groom_role)
    role_errors = _validate_pair_roles(bride, groom, bride_role, groom_role)

    identities = {
        "person_a": context["person_a"],
        "person_b": context["person_b"],
    }
    bride_nadi = _empty_identity()
    groom_nadi = _empty_identity()

    if not role_errors and bride and groom:
        bride_nadi = _classify_normalized_identity(identities[bride])
        groom_nadi = _classify_normalized_identity(identities[groom])
        errors = [
            *_prefix_issues("bride", bride_nadi["errors"]),
            *_prefix_issues("groom", groom_nadi["errors"]),
        ]
        if errors:
            bride_nadi = _empty_identity()
            groom_nadi = _empty_identity()
    else:
        errors = [_copy_issue(issue) for issue in context["errors"]]
    errors.extend(role_errors)

    score: float | None = None
    relationship = ""
    same_nadi: bool | None = None
    nadi_dosha: bool | None = None
    factors: list[MatchmakingJsonValue] = []

    if not errors:
        lookup = get_nadi_relationship(bride_nadi["nadi"], groom_nadi["nadi"])
        score = lookup["score"]
        relationship = lookup["relationship"]
        same_nadi = lookup["same_nadi"]
        nadi_dosha = lookup["nadi_dosha"]
        factors = [
            {
                "factor": "nadi_symmetric_matrix",
                "bride_nadi": bride_nadi["nadi"],
                "groom_nadi": groom_nadi["nadi"],
                "relationship": relationship,
                "same_nadi": same_nadi,
                "nadi_dosha": nadi_dosha,
                "awarded_score": score,
            }
        ]

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": NADI_KOOTA_ID,
        "compatibility_domain": NADI_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": NADI_KOOTA_MAXIMUM_SCORE,
        "person_a_nakshatra": context["person_a"],
        "person_b_nakshatra": context["person_b"],
        "direction": {"bride_role": bride, "groom_role": groom},
        "bride_nadi": bride_nadi,
        "groom_nadi": groom_nadi,
        "relationship": relationship,
        "same_nakshatra": context["same_nakshatra"],
        "same_pada": context["same_pada"],
        "same_nadi": same_nadi,
        "nadi_dosha": nadi_dosha,
        "factors": factors,
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in context["warnings"]],
        "references": list(NADI_REFERENCES),
        "metadata": _metadata("matchmaking_nadi_koota"),
    }


def _classify_normalized_identity(
    identity: MatchmakingNakshatraIdentity,
) -> MatchmakingNadiIdentity:
    index = identity["index"]
    nadi = NADI_BY_NAKSHATRA_INDEX.get(index) if index is not None else None
    errors = [_copy_issue(issue) for issue in identity["errors"]]
    return {
        "is_valid": not errors and nadi is not None,
        "nakshatra": identity["name"],
        "nakshatra_index": index,
        "nakshatra_pada": identity["pada"],
        "source_person_id": identity["source_person_id"],
        "nadi": nadi if nadi is not None else "",
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in identity["warnings"]],
        "metadata": _metadata("matchmaking_nadi_identity"),
    }


def _empty_identity() -> MatchmakingNadiIdentity:
    return {
        "is_valid": False,
        "nakshatra": "",
        "nakshatra_index": None,
        "nakshatra_pada": None,
        "source_person_id": "",
        "nadi": "",
        "errors": [],
        "warnings": [],
        "metadata": _metadata("matchmaking_nadi_identity"),
    }


def _validate_nadi_category(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if value not in NADI_CATEGORIES:
        raise ValueError(f"{field} must be a canonical Nadi category")


def _validate_pair_roles(
    bride: str,
    groom: str,
    raw_bride: object,
    raw_groom: object,
) -> list[MatchmakingNadiIssue]:
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
    issues: list[MatchmakingNadiIssue],
) -> list[MatchmakingNadiIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _copy_issue(issue: MatchmakingNakshatraIssue) -> MatchmakingNadiIssue:
    return {**issue, "metadata": dict(issue["metadata"])}


def _issue(field: str, code: str, value: object) -> MatchmakingNadiIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingNadiMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": NADI_CALCULATION_NAME,
        "maximum_score": NADI_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": NADI_COMPATIBILITY_DOMAIN,
        "directional": False,
        "symmetric": True,
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


if tuple(NADI_BY_NAKSHATRA_INDEX) != tuple(range(NAKSHATRA_COUNT)):
    raise RuntimeError("Nadi mapping must cover all canonical Nakshatra indexes")

if len(NAKSHATRA_LIST) != len(NADI_BY_NAKSHATRA_INDEX):
    raise RuntimeError("Nadi mapping must match the canonical Nakshatra list")

if any(
    tuple(NADI_BY_NAKSHATRA_INDEX.values()).count(nadi) != 9 for nadi in NADI_CATEGORIES
):
    raise RuntimeError("Nadi mapping must contain nine Nakshatras per category")

if tuple(NADI_SCORING_MATRIX) != NADI_CATEGORIES or any(
    tuple(row) != NADI_CATEGORIES for row in NADI_SCORING_MATRIX.values()
):
    raise RuntimeError("Nadi matrix rows must cover all canonical categories")

if any(
    NADI_SCORING_MATRIX[first][second] != NADI_SCORING_MATRIX[second][first]
    for first in NADI_CATEGORIES
    for second in NADI_CATEGORIES
):
    raise RuntimeError("Nadi matrix must be symmetric")
