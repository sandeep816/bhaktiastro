"""Deterministic Graha Maitri Koota classification and symmetric scoring."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.constants.rashi import RASHI_COUNT, RASHI_LIST
from backend.app.kundali.graha_lordship import get_rashi_lord_by_index
from backend.app.kundali.graha_relationship import CLASSICAL_PLANETS
from backend.app.kundali.graha_relationship import get_natural_relationship
from backend.app.kundali.rashi import get_rashi, normalize_longitude
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MATCHMAKING_STATUSES
from backend.app.matchmaking.foundation import MatchmakingJsonValue

GRAHA_MAITRI_KOOTA_ID = "graha_maitri"
GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE = 5.0
GRAHA_MAITRI_COMPATIBILITY_DOMAIN = "mental_compatibility"
GRAHA_MAITRI_CALCULATION_NAME = "graha_maitri_koota"

GRAHA_MAITRI_LORDS = CLASSICAL_PLANETS

GRAHA_MAITRI_SAME_LORD = "same_lord"
GRAHA_MAITRI_MUTUAL_FRIEND = "mutual_friend"
GRAHA_MAITRI_FRIEND_NEUTRAL = "friend_neutral"
GRAHA_MAITRI_MUTUAL_NEUTRAL = "mutual_neutral"
GRAHA_MAITRI_FRIEND_ENEMY = "friend_enemy"
GRAHA_MAITRI_NEUTRAL_ENEMY = "neutral_enemy"
GRAHA_MAITRI_MUTUAL_ENEMY = "mutual_enemy"

GRAHA_MAITRI_COMBINED_SCORES: dict[tuple[str, str], tuple[str, float]] = {
    ("friend", "friend"): (GRAHA_MAITRI_MUTUAL_FRIEND, 5.0),
    ("friend", "neutral"): (GRAHA_MAITRI_FRIEND_NEUTRAL, 4.0),
    ("neutral", "neutral"): (GRAHA_MAITRI_MUTUAL_NEUTRAL, 3.0),
    ("enemy", "friend"): (GRAHA_MAITRI_FRIEND_ENEMY, 1.0),
    ("enemy", "neutral"): (GRAHA_MAITRI_NEUTRAL_ENEMY, 0.5),
    ("enemy", "enemy"): (GRAHA_MAITRI_MUTUAL_ENEMY, 0.0),
}

GRAHA_MAITRI_REFERENCES = (
    "https://www.futuresamachar.com/download/horoscope-matching-325.pdf",
    "https://www.rashisetu.com/blog/ashtakoota-gun-milan-explained",
    "https://www.ghvisweswara.com/wp-content/uploads/2021/11/"
    "Comparison_of_Panchangas.pdf",
)

MOON_LONGITUDE_MISSING = "moon_longitude_missing"
MOON_LONGITUDE_INVALID = "moon_longitude_invalid"

MATCHMAKING_GRAHA_MAITRI_ISSUE_CODES = (
    MOON_LONGITUDE_MISSING,
    MOON_LONGITUDE_INVALID,
)

MatchmakingGrahaMaitriIssueSeverity = Literal["error", "warning"]


class MatchmakingGrahaMaitriIssue(TypedDict):
    """One localization-ready Graha Maitri issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingGrahaMaitriIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingGrahaMaitriMetadata(TypedDict):
    """Stable metadata for Graha Maitri objects."""

    component: str
    schema_version: str
    deterministic: bool
    calculation: str
    maximum_score: float
    compatibility_domain: str
    directional: bool
    symmetric: bool
    relationship_type: str
    rashi_count: int
    index_base: int


class MatchmakingGrahaMaitriIdentity(TypedDict):
    """Canonical Moon-Rashi lord identity from one supplied longitude."""

    is_valid: bool
    sidereal_moon_longitude: float | None
    rashi: str
    rashi_english: str
    rashi_hindi: str
    rashi_sanskrit: str
    rashi_index: int | None
    degree_in_rashi: float | None
    lord: str
    errors: list[MatchmakingGrahaMaitriIssue]
    warnings: list[MatchmakingGrahaMaitriIssue]
    metadata: MatchmakingGrahaMaitriMetadata


class MatchmakingGrahaMaitriRelationship(TypedDict):
    """Directional permanent relationships and their symmetric score."""

    bride_lord: str
    groom_lord: str
    bride_to_groom: str
    groom_to_bride: str
    combined_relationship: str
    same_lord: bool
    score: float


class MatchmakingGrahaMaitriKootaResult(TypedDict):
    """Structured Graha Maitri score without compatibility prose."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    bride_moon_rashi: MatchmakingGrahaMaitriIdentity
    groom_moon_rashi: MatchmakingGrahaMaitriIdentity
    direction: dict[str, str]
    bride_to_groom_relationship: str
    groom_to_bride_relationship: str
    combined_relationship: str
    same_lord: bool | None
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingGrahaMaitriIssue]
    warnings: list[MatchmakingGrahaMaitriIssue]
    references: list[str]
    metadata: MatchmakingGrahaMaitriMetadata


def classify_graha_maitri_lord(
    sidereal_moon_longitude: float,
) -> MatchmakingGrahaMaitriIdentity:
    """Derive one canonical Moon-Rashi lord identity.

    Raises:
        TypeError: If the longitude is a boolean or is not a real number.
        ValueError: If the longitude is NaN or infinite.
    """

    normalized_longitude = normalize_longitude(sidereal_moon_longitude)
    rashi = get_rashi(normalized_longitude)
    lord = get_rashi_lord_by_index(rashi["index"]).casefold()

    return {
        "is_valid": True,
        "sidereal_moon_longitude": normalized_longitude,
        "rashi": rashi["sanskrit"],
        "rashi_english": rashi["english"],
        "rashi_hindi": rashi["hindi"],
        "rashi_sanskrit": rashi["sanskrit"],
        "rashi_index": rashi["index"],
        "degree_in_rashi": rashi["degree_in_rashi"],
        "lord": lord,
        "errors": [],
        "warnings": [],
        "metadata": _metadata("matchmaking_graha_maitri_identity"),
    }


def get_graha_maitri_relationship(
    bride_lord: str,
    groom_lord: str,
) -> MatchmakingGrahaMaitriRelationship:
    """Return strict directional statuses and symmetric score for two lords.

    Raises:
        TypeError: If either lord is not a string.
        ValueError: If either lord is not a canonical lowercase identifier.
    """

    _validate_lord(bride_lord, "bride_lord")
    _validate_lord(groom_lord, "groom_lord")

    if bride_lord == groom_lord:
        return {
            "bride_lord": bride_lord,
            "groom_lord": groom_lord,
            "bride_to_groom": "same",
            "groom_to_bride": "same",
            "combined_relationship": GRAHA_MAITRI_SAME_LORD,
            "same_lord": True,
            "score": GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
        }

    bride_to_groom = get_natural_relationship(bride_lord, groom_lord)
    groom_to_bride = get_natural_relationship(groom_lord, bride_lord)
    pair = tuple(sorted((bride_to_groom, groom_to_bride)))
    try:
        combined_relationship, score = GRAHA_MAITRI_COMBINED_SCORES[pair]
    except KeyError as exc:
        raise RuntimeError("Unsupported natural relationship combination") from exc

    return {
        "bride_lord": bride_lord,
        "groom_lord": groom_lord,
        "bride_to_groom": bride_to_groom,
        "groom_to_bride": groom_to_bride,
        "combined_relationship": combined_relationship,
        "same_lord": False,
        "score": score,
    }


def _build_scoring_matrix() -> dict[str, dict[str, float]]:
    return {
        bride_lord: {
            groom_lord: get_graha_maitri_relationship(bride_lord, groom_lord)["score"]
            for groom_lord in GRAHA_MAITRI_LORDS
        }
        for bride_lord in GRAHA_MAITRI_LORDS
    }


def calculate_graha_maitri_koota(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingGrahaMaitriKootaResult:
    """Calculate symmetric Graha Maitri Koota from explicitly assigned roles."""

    bride_identity = _classify_for_result(bride_moon_longitude)
    groom_identity = _classify_for_result(groom_moon_longitude)
    errors = [
        *_prefix_issues("bride", bride_identity["errors"]),
        *_prefix_issues("groom", groom_identity["errors"]),
    ]

    score: float | None = None
    bride_to_groom = ""
    groom_to_bride = ""
    combined_relationship = ""
    same_lord: bool | None = None
    factors: list[MatchmakingJsonValue] = []

    if not errors:
        relationship = get_graha_maitri_relationship(
            bride_identity["lord"], groom_identity["lord"]
        )
        score = relationship["score"]
        bride_to_groom = relationship["bride_to_groom"]
        groom_to_bride = relationship["groom_to_bride"]
        combined_relationship = relationship["combined_relationship"]
        same_lord = relationship["same_lord"]
        factors = [
            {
                "factor": "permanent_planetary_relationship",
                "relationship_type": "natural_permanent",
                "row_role": "bride",
                "column_role": "groom",
                "bride_lord": relationship["bride_lord"],
                "groom_lord": relationship["groom_lord"],
                "bride_to_groom": bride_to_groom,
                "groom_to_bride": groom_to_bride,
                "combined_relationship": combined_relationship,
                "same_lord": same_lord,
                "awarded_score": score,
            }
        ]

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": GRAHA_MAITRI_KOOTA_ID,
        "compatibility_domain": GRAHA_MAITRI_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
        "bride_moon_rashi": bride_identity,
        "groom_moon_rashi": groom_identity,
        "direction": {"row_role": "bride", "column_role": "groom"},
        "bride_to_groom_relationship": bride_to_groom,
        "groom_to_bride_relationship": groom_to_bride,
        "combined_relationship": combined_relationship,
        "same_lord": same_lord,
        "factors": factors,
        "errors": errors,
        "warnings": [],
        "references": list(GRAHA_MAITRI_REFERENCES),
        "metadata": _metadata("matchmaking_graha_maitri_koota"),
    }


def _classify_for_result(value: object) -> MatchmakingGrahaMaitriIdentity:
    try:
        return classify_graha_maitri_lord(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        code = MOON_LONGITUDE_MISSING if value in (None, "") else MOON_LONGITUDE_INVALID
        issue = _issue("sidereal_moon_longitude", code, value)
        return {
            "is_valid": False,
            "sidereal_moon_longitude": None,
            "rashi": "",
            "rashi_english": "",
            "rashi_hindi": "",
            "rashi_sanskrit": "",
            "rashi_index": None,
            "degree_in_rashi": None,
            "lord": "",
            "errors": [issue],
            "warnings": [],
            "metadata": _metadata("matchmaking_graha_maitri_identity"),
        }


def _validate_lord(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if value not in GRAHA_MAITRI_LORDS:
        raise ValueError(f"{field} must be a canonical Graha Maitri lord")


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingGrahaMaitriIssue],
) -> list[MatchmakingGrahaMaitriIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _issue(
    field: str,
    code: str,
    value: object,
) -> MatchmakingGrahaMaitriIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingGrahaMaitriMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": GRAHA_MAITRI_CALCULATION_NAME,
        "maximum_score": GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": GRAHA_MAITRI_COMPATIBILITY_DOMAIN,
        "directional": False,
        "symmetric": True,
        "relationship_type": "natural_permanent",
        "rashi_count": RASHI_COUNT,
        "index_base": 1,
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


GRAHA_MAITRI_SCORING_MATRIX = _build_scoring_matrix()

if len(RASHI_LIST) != RASHI_COUNT:
    raise RuntimeError("Canonical Rashi constants must cover all twelve Rashis")

if tuple(GRAHA_MAITRI_SCORING_MATRIX) != GRAHA_MAITRI_LORDS:
    raise RuntimeError("Graha Maitri matrix must cover all canonical lords")
