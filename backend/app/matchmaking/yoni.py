"""Deterministic Yoni Koota classification and symmetric scoring."""

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

YONI_KOOTA_ID = "yoni"
YONI_KOOTA_MAXIMUM_SCORE = 4.0
YONI_COMPATIBILITY_DOMAIN = "intimacy"
YONI_CALCULATION_NAME = "yoni_koota"

YONI_HORSE = "horse"
YONI_ELEPHANT = "elephant"
YONI_SHEEP = "sheep"
YONI_SERPENT = "serpent"
YONI_DOG = "dog"
YONI_CAT = "cat"
YONI_RAT = "rat"
YONI_COW = "cow"
YONI_BUFFALO = "buffalo"
YONI_TIGER = "tiger"
YONI_DEER = "deer"
YONI_MONKEY = "monkey"
YONI_MONGOOSE = "mongoose"
YONI_LION = "lion"

YONI_CATEGORIES = (
    YONI_HORSE,
    YONI_ELEPHANT,
    YONI_SHEEP,
    YONI_SERPENT,
    YONI_DOG,
    YONI_CAT,
    YONI_RAT,
    YONI_COW,
    YONI_BUFFALO,
    YONI_TIGER,
    YONI_DEER,
    YONI_MONKEY,
    YONI_MONGOOSE,
    YONI_LION,
)

YONI_MALE = "male"
YONI_FEMALE = "female"
YONI_SEXES = (YONI_MALE, YONI_FEMALE)

YONI_SAME = "same"
YONI_FRIENDLY = "friendly"
YONI_NEUTRAL = "neutral"
YONI_ENEMY = "enemy"
YONI_SWORN_ENEMY = "sworn_enemy"

YONI_RELATIONSHIP_BY_SCORE = {
    4.0: YONI_SAME,
    3.0: YONI_FRIENDLY,
    2.0: YONI_NEUTRAL,
    1.0: YONI_ENEMY,
    0.0: YONI_SWORN_ENEMY,
}


class YoniDefinition(TypedDict):
    """One canonical Nakshatra-to-Yoni definition."""

    yoni: str
    traditional_name: str
    yoni_sex: str


YONI_BY_NAKSHATRA_INDEX: dict[int, YoniDefinition] = {
    0: {"yoni": YONI_HORSE, "traditional_name": "Ashwa", "yoni_sex": YONI_MALE},
    1: {
        "yoni": YONI_ELEPHANT,
        "traditional_name": "Gaja",
        "yoni_sex": YONI_MALE,
    },
    2: {"yoni": YONI_SHEEP, "traditional_name": "Mesha", "yoni_sex": YONI_FEMALE},
    3: {"yoni": YONI_SERPENT, "traditional_name": "Sarpa", "yoni_sex": YONI_MALE},
    4: {
        "yoni": YONI_SERPENT,
        "traditional_name": "Sarpa",
        "yoni_sex": YONI_FEMALE,
    },
    5: {"yoni": YONI_DOG, "traditional_name": "Shwana", "yoni_sex": YONI_FEMALE},
    6: {
        "yoni": YONI_CAT,
        "traditional_name": "Marjara",
        "yoni_sex": YONI_FEMALE,
    },
    7: {"yoni": YONI_SHEEP, "traditional_name": "Mesha", "yoni_sex": YONI_MALE},
    8: {"yoni": YONI_CAT, "traditional_name": "Marjara", "yoni_sex": YONI_MALE},
    9: {"yoni": YONI_RAT, "traditional_name": "Mushika", "yoni_sex": YONI_MALE},
    10: {
        "yoni": YONI_RAT,
        "traditional_name": "Mushika",
        "yoni_sex": YONI_FEMALE,
    },
    11: {"yoni": YONI_COW, "traditional_name": "Gau", "yoni_sex": YONI_MALE},
    12: {
        "yoni": YONI_BUFFALO,
        "traditional_name": "Mahisha",
        "yoni_sex": YONI_FEMALE,
    },
    13: {
        "yoni": YONI_TIGER,
        "traditional_name": "Vyaghra",
        "yoni_sex": YONI_FEMALE,
    },
    14: {
        "yoni": YONI_BUFFALO,
        "traditional_name": "Mahisha",
        "yoni_sex": YONI_MALE,
    },
    15: {
        "yoni": YONI_TIGER,
        "traditional_name": "Vyaghra",
        "yoni_sex": YONI_MALE,
    },
    16: {"yoni": YONI_DEER, "traditional_name": "Mriga", "yoni_sex": YONI_FEMALE},
    17: {"yoni": YONI_DEER, "traditional_name": "Mriga", "yoni_sex": YONI_MALE},
    18: {"yoni": YONI_DOG, "traditional_name": "Shwana", "yoni_sex": YONI_MALE},
    19: {
        "yoni": YONI_MONKEY,
        "traditional_name": "Vanara",
        "yoni_sex": YONI_MALE,
    },
    20: {
        "yoni": YONI_MONGOOSE,
        "traditional_name": "Nakula",
        "yoni_sex": YONI_MALE,
    },
    21: {
        "yoni": YONI_MONKEY,
        "traditional_name": "Vanara",
        "yoni_sex": YONI_FEMALE,
    },
    22: {"yoni": YONI_LION, "traditional_name": "Simha", "yoni_sex": YONI_FEMALE},
    23: {"yoni": YONI_HORSE, "traditional_name": "Ashwa", "yoni_sex": YONI_FEMALE},
    24: {"yoni": YONI_LION, "traditional_name": "Simha", "yoni_sex": YONI_MALE},
    25: {"yoni": YONI_COW, "traditional_name": "Gau", "yoni_sex": YONI_FEMALE},
    26: {
        "yoni": YONI_ELEPHANT,
        "traditional_name": "Gaja",
        "yoni_sex": YONI_FEMALE,
    },
}


def _score_row(*scores: int) -> dict[str, float]:
    if len(scores) != len(YONI_CATEGORIES):
        raise RuntimeError("Yoni score row must cover every canonical category")
    return {
        category: float(score)
        for category, score in zip(YONI_CATEGORIES, scores, strict=True)
    }


YONI_SCORING_MATRIX: dict[str, dict[str, float]] = {
    YONI_HORSE: _score_row(4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1),
    YONI_ELEPHANT: _score_row(2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),
    YONI_SHEEP: _score_row(2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1),
    YONI_SERPENT: _score_row(3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),
    YONI_DOG: _score_row(2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),
    YONI_CAT: _score_row(2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),
    YONI_RAT: _score_row(2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),
    YONI_COW: _score_row(1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),
    YONI_BUFFALO: _score_row(0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),
    YONI_TIGER: _score_row(1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),
    YONI_DEER: _score_row(3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1),
    YONI_MONKEY: _score_row(3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2),
    YONI_MONGOOSE: _score_row(2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2),
    YONI_LION: _score_row(1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4),
}

YONI_REFERENCES = (
    "https://saravali.github.io/astrology/koota_yoni.html",
    "https://www.futuresamachar.com/download/horoscope-matching-325.pdf",
    "https://www.ghvisweswara.com/wp-content/uploads/2021/11/"
    "Comparison_of_Panchangas.pdf",
)

DIRECTION_MISSING = "direction_missing"
ROLE_INVALID = "role_invalid"

MATCHMAKING_YONI_ISSUE_CODES = (
    *MATCHMAKING_NAKSHATRA_ISSUE_CODES,
    DIRECTION_MISSING,
    ROLE_INVALID,
)

_VALID_PAIR_ROLES = ("person_a", "person_b")

MatchmakingYoniIssueSeverity = Literal["error", "warning"]


class MatchmakingYoniIssue(TypedDict):
    """One localization-ready Yoni Koota issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingYoniIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingYoniMetadata(TypedDict):
    """Stable metadata for Yoni Koota objects."""

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


class MatchmakingYoniIdentity(TypedDict):
    """Canonical Yoni identity derived from a supplied Moon Nakshatra."""

    is_valid: bool
    nakshatra: str
    nakshatra_index: int | None
    nakshatra_pada: int | None
    source_person_id: str
    yoni: str
    traditional_name: str
    yoni_sex: str
    errors: list[MatchmakingYoniIssue]
    warnings: list[MatchmakingYoniIssue]
    metadata: MatchmakingYoniMetadata


class MatchmakingYoniRelationship(TypedDict):
    """One strict symmetric lookup result for two canonical Yonis."""

    bride_yoni: str
    groom_yoni: str
    relationship: str
    score: float


class MatchmakingYoniKootaResult(TypedDict):
    """Structured Yoni Koota score without compatibility judgement."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    person_a_nakshatra: MatchmakingNakshatraIdentity
    person_b_nakshatra: MatchmakingNakshatraIdentity
    direction: dict[str, str]
    bride_yoni: MatchmakingYoniIdentity
    groom_yoni: MatchmakingYoniIdentity
    relationship: str
    same_nakshatra: bool | None
    same_pada: bool | None
    same_yoni: bool | None
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingYoniIssue]
    warnings: list[MatchmakingYoniIssue]
    references: list[str]
    metadata: MatchmakingYoniMetadata


def classify_yoni(
    value: object,
    *,
    pada: object = None,
    source_person_id: object = "",
) -> MatchmakingYoniIdentity:
    """Classify one supported Nakshatra input using shared normalization."""

    identity = normalize_matchmaking_nakshatra(
        value,
        pada=pada,
        source_person_id=source_person_id,
    )
    return _classify_normalized_identity(identity)


def get_yoni_relationship(
    bride_yoni: str,
    groom_yoni: str,
) -> MatchmakingYoniRelationship:
    """Return the strict symmetric relationship and score for two Yonis.

    Raises:
        TypeError: If either category is not a string.
        ValueError: If either category is not a canonical identifier.
    """

    _validate_yoni_category(bride_yoni, "bride_yoni")
    _validate_yoni_category(groom_yoni, "groom_yoni")
    score = YONI_SCORING_MATRIX[bride_yoni][groom_yoni]
    return {
        "bride_yoni": bride_yoni,
        "groom_yoni": groom_yoni,
        "relationship": YONI_RELATIONSHIP_BY_SCORE[score],
        "score": score,
    }


def calculate_yoni_koota(
    pair: object,
    *,
    bride_role: object = None,
    groom_role: object = None,
) -> MatchmakingYoniKootaResult:
    """Calculate symmetric Yoni Koota for explicitly assigned roles."""

    context = build_nakshatra_pair_context(pair)
    bride = _normalize_role(bride_role)
    groom = _normalize_role(groom_role)
    role_errors = _validate_pair_roles(bride, groom, bride_role, groom_role)

    identities = {
        "person_a": context["person_a"],
        "person_b": context["person_b"],
    }
    bride_yoni = _empty_identity()
    groom_yoni = _empty_identity()

    if not role_errors and bride and groom:
        bride_yoni = _classify_normalized_identity(identities[bride])
        groom_yoni = _classify_normalized_identity(identities[groom])
        errors = [
            *_prefix_issues("bride", bride_yoni["errors"]),
            *_prefix_issues("groom", groom_yoni["errors"]),
        ]
    else:
        errors = [_copy_issue(issue) for issue in context["errors"]]
    errors.extend(role_errors)

    score: float | None = None
    relationship = ""
    same_yoni: bool | None = None
    factors: list[MatchmakingJsonValue] = []

    if not errors:
        bride_category = bride_yoni["yoni"]
        groom_category = groom_yoni["yoni"]
        lookup = get_yoni_relationship(bride_category, groom_category)
        score = lookup["score"]
        relationship = lookup["relationship"]
        same_yoni = bride_category == groom_category
        factors = [
            {
                "factor": "yoni_symmetric_matrix",
                "row_role": "bride",
                "column_role": "groom",
                "bride_yoni": bride_category,
                "groom_yoni": groom_category,
                "relationship": relationship,
                "awarded_score": score,
            }
        ]

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": YONI_KOOTA_ID,
        "compatibility_domain": YONI_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": YONI_KOOTA_MAXIMUM_SCORE,
        "person_a_nakshatra": context["person_a"],
        "person_b_nakshatra": context["person_b"],
        "direction": {"bride_role": bride, "groom_role": groom},
        "bride_yoni": bride_yoni,
        "groom_yoni": groom_yoni,
        "relationship": relationship,
        "same_nakshatra": context["same_nakshatra"],
        "same_pada": context["same_pada"],
        "same_yoni": same_yoni,
        "factors": factors,
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in context["warnings"]],
        "references": list(YONI_REFERENCES),
        "metadata": _metadata("matchmaking_yoni_koota"),
    }


def _classify_normalized_identity(
    identity: MatchmakingNakshatraIdentity,
) -> MatchmakingYoniIdentity:
    index = identity["index"]
    definition = YONI_BY_NAKSHATRA_INDEX.get(index) if index is not None else None
    errors = [_copy_issue(issue) for issue in identity["errors"]]

    return {
        "is_valid": not errors and definition is not None,
        "nakshatra": identity["name"],
        "nakshatra_index": index,
        "nakshatra_pada": identity["pada"],
        "source_person_id": identity["source_person_id"],
        "yoni": definition["yoni"] if definition is not None else "",
        "traditional_name": (
            definition["traditional_name"] if definition is not None else ""
        ),
        "yoni_sex": definition["yoni_sex"] if definition is not None else "",
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in identity["warnings"]],
        "metadata": _metadata("matchmaking_yoni_identity"),
    }


def _empty_identity() -> MatchmakingYoniIdentity:
    return {
        "is_valid": False,
        "nakshatra": "",
        "nakshatra_index": None,
        "nakshatra_pada": None,
        "source_person_id": "",
        "yoni": "",
        "traditional_name": "",
        "yoni_sex": "",
        "errors": [],
        "warnings": [],
        "metadata": _metadata("matchmaking_yoni_identity"),
    }


def _validate_yoni_category(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if value not in YONI_CATEGORIES:
        raise ValueError(f"{field} must be a canonical Yoni category")


def _validate_pair_roles(
    bride: str,
    groom: str,
    raw_bride: object,
    raw_groom: object,
) -> list[MatchmakingYoniIssue]:
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
    issues: list[MatchmakingYoniIssue],
) -> list[MatchmakingYoniIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _copy_issue(issue: MatchmakingNakshatraIssue) -> MatchmakingYoniIssue:
    return {**issue, "metadata": dict(issue["metadata"])}


def _issue(field: str, code: str, value: object) -> MatchmakingYoniIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingYoniMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": YONI_CALCULATION_NAME,
        "maximum_score": YONI_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": YONI_COMPATIBILITY_DOMAIN,
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


if tuple(YONI_BY_NAKSHATRA_INDEX) != tuple(range(NAKSHATRA_COUNT)):
    raise RuntimeError("Yoni mapping must cover all canonical Nakshatra indexes")

if len(NAKSHATRA_LIST) != len(YONI_BY_NAKSHATRA_INDEX):
    raise RuntimeError("Yoni mapping must match the canonical Nakshatra list")
