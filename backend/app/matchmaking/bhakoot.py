"""Deterministic Bhakoot Koota full-Rashi classification and scoring."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.constants.rashi import RASHI_COUNT, RASHI_LIST
from backend.app.kundali.rashi import get_rashi, normalize_longitude
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MATCHMAKING_STATUSES
from backend.app.matchmaking.foundation import MatchmakingJsonValue

BHAKOOT_KOOTA_ID = "bhakoot"
BHAKOOT_KOOTA_MAXIMUM_SCORE = 7.0
BHAKOOT_COMPATIBILITY_DOMAIN = "family_welfare"
BHAKOOT_CALCULATION_NAME = "bhakoot_koota"

BHAKOOT_COMPATIBLE = "compatible"
BHAKOOT_DOSHA = "dosha"

BHAKOOT_POSITION_PAIRS: dict[tuple[int, int], tuple[str, str, float]] = {
    (1, 1): ("1_1", BHAKOOT_COMPATIBLE, 7.0),
    (2, 12): ("2_12", BHAKOOT_DOSHA, 0.0),
    (3, 11): ("3_11", BHAKOOT_COMPATIBLE, 7.0),
    (4, 10): ("4_10", BHAKOOT_COMPATIBLE, 7.0),
    (5, 9): ("5_9", BHAKOOT_DOSHA, 0.0),
    (6, 8): ("6_8", BHAKOOT_DOSHA, 0.0),
    (7, 7): ("7_7", BHAKOOT_COMPATIBLE, 7.0),
}

BHAKOOT_DOSHA_POSITION_PAIRS = ((2, 12), (5, 9), (6, 8))

BHAKOOT_REFERENCES = (
    "https://saravali.github.io/astrology/koota_rasi.html",
    "https://www.futuresamachar.com/download/horoscope-matching-325.pdf",
    "https://www.astrosaxena.com/asmh2",
    "https://www.ghvisweswara.com/wp-content/uploads/2021/11/"
    "Comparison_of_Panchangas.pdf",
)

MOON_LONGITUDE_MISSING = "moon_longitude_missing"
MOON_LONGITUDE_INVALID = "moon_longitude_invalid"

MATCHMAKING_BHAKOOT_ISSUE_CODES = (
    MOON_LONGITUDE_MISSING,
    MOON_LONGITUDE_INVALID,
)

MatchmakingBhakootIssueSeverity = Literal["error", "warning"]


class MatchmakingBhakootIssue(TypedDict):
    """One localization-ready Bhakoot issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingBhakootIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingBhakootMetadata(TypedDict):
    """Stable metadata for Bhakoot objects."""

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


class MatchmakingBhakootIdentity(TypedDict):
    """Canonical full Moon-Rashi identity from one supplied longitude."""

    is_valid: bool
    sidereal_moon_longitude: float | None
    rashi: str
    rashi_english: str
    rashi_hindi: str
    rashi_sanskrit: str
    rashi_index: int | None
    degree_in_rashi: float | None
    errors: list[MatchmakingBhakootIssue]
    warnings: list[MatchmakingBhakootIssue]
    metadata: MatchmakingBhakootMetadata


class MatchmakingBhakootRelationship(TypedDict):
    """Inclusive directional distances and their symmetric Bhakoot score."""

    bride_rashi_index: int
    groom_rashi_index: int
    bride_to_groom_distance: int
    groom_to_bride_distance: int
    pair_identifier: str
    position_pair: str
    relationship: str
    same_rashi: bool
    bhakoot_dosha: bool
    score: float


class MatchmakingBhakootKootaResult(TypedDict):
    """Structured Bhakoot score without cancellation or compatibility prose."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    bride_moon_rashi: MatchmakingBhakootIdentity
    groom_moon_rashi: MatchmakingBhakootIdentity
    direction: dict[str, str]
    bride_to_groom_distance: int | None
    groom_to_bride_distance: int | None
    pair_identifier: str
    position_pair: str
    relationship: str
    same_rashi: bool | None
    bhakoot_dosha: bool | None
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingBhakootIssue]
    warnings: list[MatchmakingBhakootIssue]
    references: list[str]
    metadata: MatchmakingBhakootMetadata


def classify_bhakoot_rashi(
    sidereal_moon_longitude: float,
) -> MatchmakingBhakootIdentity:
    """Derive one canonical full Moon-Rashi identity.

    Raises:
        TypeError: If the longitude is a boolean or is not a real number.
        ValueError: If the longitude is NaN or infinite.
    """

    normalized_longitude = normalize_longitude(sidereal_moon_longitude)
    rashi = get_rashi(normalized_longitude)

    return {
        "is_valid": True,
        "sidereal_moon_longitude": normalized_longitude,
        "rashi": rashi["sanskrit"],
        "rashi_english": rashi["english"],
        "rashi_hindi": rashi["hindi"],
        "rashi_sanskrit": rashi["sanskrit"],
        "rashi_index": rashi["index"],
        "degree_in_rashi": rashi["degree_in_rashi"],
        "errors": [],
        "warnings": [],
        "metadata": _metadata("matchmaking_bhakoot_identity"),
    }


def calculate_bhakoot_inclusive_distance(
    from_rashi_index: int,
    to_rashi_index: int,
) -> int:
    """Return inclusive circular distance between exact one-based indexes.

    Raises:
        TypeError: If either index is not an integer or is a boolean.
        ValueError: If either index is outside the inclusive range 1..12.
    """

    _validate_rashi_index(from_rashi_index, "from_rashi_index")
    _validate_rashi_index(to_rashi_index, "to_rashi_index")
    return ((to_rashi_index - from_rashi_index) % RASHI_COUNT) + 1


def get_bhakoot_relationship(
    bride_rashi_index: int,
    groom_rashi_index: int,
) -> MatchmakingBhakootRelationship:
    """Return directional distances and symmetric score for two Rashis.

    Raises:
        TypeError: If either index is not an integer or is a boolean.
        ValueError: If either index is outside the inclusive range 1..12.
    """

    bride_to_groom = calculate_bhakoot_inclusive_distance(
        bride_rashi_index, groom_rashi_index
    )
    groom_to_bride = calculate_bhakoot_inclusive_distance(
        groom_rashi_index, bride_rashi_index
    )
    canonical_pair = tuple(sorted((bride_to_groom, groom_to_bride)))
    try:
        pair_identifier, relationship, score = BHAKOOT_POSITION_PAIRS[canonical_pair]
    except KeyError as exc:
        raise RuntimeError("Unsupported Bhakoot position pair") from exc

    same_rashi = bride_rashi_index == groom_rashi_index
    return {
        "bride_rashi_index": bride_rashi_index,
        "groom_rashi_index": groom_rashi_index,
        "bride_to_groom_distance": bride_to_groom,
        "groom_to_bride_distance": groom_to_bride,
        "pair_identifier": pair_identifier,
        "position_pair": f"{canonical_pair[0]}/{canonical_pair[1]}",
        "relationship": relationship,
        "same_rashi": same_rashi,
        "bhakoot_dosha": relationship == BHAKOOT_DOSHA,
        "score": score,
    }


def _build_scoring_matrix() -> dict[int, dict[int, float]]:
    return {
        bride_index: {
            groom_index: get_bhakoot_relationship(bride_index, groom_index)["score"]
            for groom_index in range(1, RASHI_COUNT + 1)
        }
        for bride_index in range(1, RASHI_COUNT + 1)
    }


def calculate_bhakoot_koota(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingBhakootKootaResult:
    """Calculate symmetric Bhakoot Koota from explicitly assigned roles."""

    bride_identity = _classify_for_result(bride_moon_longitude)
    groom_identity = _classify_for_result(groom_moon_longitude)
    errors = [
        *_prefix_issues("bride", bride_identity["errors"]),
        *_prefix_issues("groom", groom_identity["errors"]),
    ]

    score: float | None = None
    bride_to_groom: int | None = None
    groom_to_bride: int | None = None
    pair_identifier = ""
    position_pair = ""
    relationship_name = ""
    same_rashi: bool | None = None
    bhakoot_dosha: bool | None = None
    factors: list[MatchmakingJsonValue] = []

    if not errors:
        bride_index = bride_identity["rashi_index"]
        groom_index = groom_identity["rashi_index"]
        if bride_index is None or groom_index is None:
            raise RuntimeError("Valid Bhakoot identities must contain Rashi indexes")

        relationship = get_bhakoot_relationship(bride_index, groom_index)
        score = relationship["score"]
        bride_to_groom = relationship["bride_to_groom_distance"]
        groom_to_bride = relationship["groom_to_bride_distance"]
        pair_identifier = relationship["pair_identifier"]
        position_pair = relationship["position_pair"]
        relationship_name = relationship["relationship"]
        same_rashi = relationship["same_rashi"]
        bhakoot_dosha = relationship["bhakoot_dosha"]
        factors = [
            {
                "factor": "inclusive_circular_rashi_distance",
                "row_role": "bride",
                "column_role": "groom",
                "bride_rashi_index": bride_index,
                "groom_rashi_index": groom_index,
                "bride_to_groom_distance": bride_to_groom,
                "groom_to_bride_distance": groom_to_bride,
                "pair_identifier": pair_identifier,
                "position_pair": position_pair,
                "relationship": relationship_name,
                "same_rashi": same_rashi,
                "bhakoot_dosha": bhakoot_dosha,
                "awarded_score": score,
            }
        ]

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": BHAKOOT_KOOTA_ID,
        "compatibility_domain": BHAKOOT_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": BHAKOOT_KOOTA_MAXIMUM_SCORE,
        "bride_moon_rashi": bride_identity,
        "groom_moon_rashi": groom_identity,
        "direction": {"row_role": "bride", "column_role": "groom"},
        "bride_to_groom_distance": bride_to_groom,
        "groom_to_bride_distance": groom_to_bride,
        "pair_identifier": pair_identifier,
        "position_pair": position_pair,
        "relationship": relationship_name,
        "same_rashi": same_rashi,
        "bhakoot_dosha": bhakoot_dosha,
        "factors": factors,
        "errors": errors,
        "warnings": [],
        "references": list(BHAKOOT_REFERENCES),
        "metadata": _metadata("matchmaking_bhakoot_koota"),
    }


def _classify_for_result(value: object) -> MatchmakingBhakootIdentity:
    try:
        return classify_bhakoot_rashi(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        missing = value is None or (isinstance(value, str) and value == "")
        code = MOON_LONGITUDE_MISSING if missing else MOON_LONGITUDE_INVALID
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
            "errors": [issue],
            "warnings": [],
            "metadata": _metadata("matchmaking_bhakoot_identity"),
        }


def _validate_rashi_index(value: object, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{field} must be an integer")
    if not 1 <= int(value) <= RASHI_COUNT:
        raise ValueError(f"{field} must be between 1 and {RASHI_COUNT}")


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingBhakootIssue],
) -> list[MatchmakingBhakootIssue]:
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
) -> MatchmakingBhakootIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingBhakootMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": BHAKOOT_CALCULATION_NAME,
        "maximum_score": BHAKOOT_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": BHAKOOT_COMPATIBILITY_DOMAIN,
        "directional": False,
        "symmetric": True,
        "relationship_type": "inclusive_circular_rashi_distance",
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


BHAKOOT_SCORING_MATRIX = _build_scoring_matrix()

if len(RASHI_LIST) != RASHI_COUNT:
    raise RuntimeError("Canonical Rashi constants must cover all twelve Rashis")

if tuple(BHAKOOT_SCORING_MATRIX) != tuple(range(1, RASHI_COUNT + 1)):
    raise RuntimeError("Bhakoot matrix must cover all canonical Rashi indexes")

if any(
    BHAKOOT_SCORING_MATRIX[bride][groom] != BHAKOOT_SCORING_MATRIX[groom][bride]
    for bride in BHAKOOT_SCORING_MATRIX
    for groom in BHAKOOT_SCORING_MATRIX[bride]
):
    raise RuntimeError("Bhakoot scoring matrix must be symmetric")
