"""Deterministic Vashya Koota classification and directional scoring."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.kundali.rashi import get_rashi, normalize_longitude
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MATCHMAKING_STATUSES
from backend.app.matchmaking.foundation import MatchmakingJsonValue

VASHYA_KOOTA_ID = "vashya"
VASHYA_KOOTA_MAXIMUM_SCORE = 2.0
VASHYA_COMPATIBILITY_DOMAIN = "attraction"
VASHYA_CALCULATION_NAME = "vashya_koota"

VASHYA_CHATUSHPADA = "chatushpada"
VASHYA_MANAVA = "manava"
VASHYA_JALACHARA = "jalachara"
VASHYA_VANACHARA = "vanachara"
VASHYA_KEETA = "keeta"

VASHYA_CATEGORIES = (
    VASHYA_CHATUSHPADA,
    VASHYA_MANAVA,
    VASHYA_JALACHARA,
    VASHYA_VANACHARA,
    VASHYA_KEETA,
)

VASHYA_BY_WHOLE_RASHI_INDEX: dict[int, str] = {
    1: VASHYA_CHATUSHPADA,
    2: VASHYA_CHATUSHPADA,
    3: VASHYA_MANAVA,
    4: VASHYA_JALACHARA,
    5: VASHYA_VANACHARA,
    6: VASHYA_MANAVA,
    7: VASHYA_MANAVA,
    8: VASHYA_KEETA,
    11: VASHYA_MANAVA,
    12: VASHYA_JALACHARA,
}

VASHYA_SCORING_MATRIX: dict[str, dict[str, float]] = {
    VASHYA_CHATUSHPADA: {
        VASHYA_CHATUSHPADA: 2.0,
        VASHYA_MANAVA: 1.0,
        VASHYA_JALACHARA: 1.0,
        VASHYA_VANACHARA: 1.5,
        VASHYA_KEETA: 1.0,
    },
    VASHYA_MANAVA: {
        VASHYA_CHATUSHPADA: 1.0,
        VASHYA_MANAVA: 2.0,
        VASHYA_JALACHARA: 1.5,
        VASHYA_VANACHARA: 0.0,
        VASHYA_KEETA: 1.0,
    },
    VASHYA_JALACHARA: {
        VASHYA_CHATUSHPADA: 1.0,
        VASHYA_MANAVA: 1.5,
        VASHYA_JALACHARA: 2.0,
        VASHYA_VANACHARA: 1.0,
        VASHYA_KEETA: 1.0,
    },
    VASHYA_VANACHARA: {
        VASHYA_CHATUSHPADA: 0.0,
        VASHYA_MANAVA: 0.0,
        VASHYA_JALACHARA: 0.0,
        VASHYA_VANACHARA: 2.0,
        VASHYA_KEETA: 0.0,
    },
    VASHYA_KEETA: {
        VASHYA_CHATUSHPADA: 1.0,
        VASHYA_MANAVA: 1.0,
        VASHYA_JALACHARA: 1.0,
        VASHYA_VANACHARA: 0.0,
        VASHYA_KEETA: 2.0,
    },
}

MOON_LONGITUDE_MISSING = "moon_longitude_missing"
MOON_LONGITUDE_INVALID = "moon_longitude_invalid"

MATCHMAKING_VASHYA_ISSUE_CODES = (
    MOON_LONGITUDE_MISSING,
    MOON_LONGITUDE_INVALID,
)

MatchmakingVashyaIssueSeverity = Literal["error", "warning"]


class MatchmakingVashyaIssue(TypedDict):
    """One localization-ready Vashya Koota issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingVashyaIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingVashyaMetadata(TypedDict):
    """Stable metadata for Vashya Koota objects."""

    component: str
    schema_version: str
    deterministic: bool
    calculation: str
    maximum_score: float
    compatibility_domain: str
    directional: bool


class MatchmakingVashyaIdentity(TypedDict):
    """Canonical Vashya identity derived from sidereal Moon longitude."""

    is_valid: bool
    sidereal_moon_longitude: float | None
    rashi: str
    rashi_index: int | None
    degree_in_rashi: float | None
    vashya: str
    errors: list[MatchmakingVashyaIssue]
    warnings: list[MatchmakingVashyaIssue]
    metadata: MatchmakingVashyaMetadata


class MatchmakingVashyaKootaResult(TypedDict):
    """Structured directional Vashya score without compatibility prose."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    bride_vashya: MatchmakingVashyaIdentity
    groom_vashya: MatchmakingVashyaIdentity
    direction: dict[str, str]
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingVashyaIssue]
    warnings: list[MatchmakingVashyaIssue]
    references: list[str]
    metadata: MatchmakingVashyaMetadata


def classify_vashya(sidereal_moon_longitude: float) -> MatchmakingVashyaIdentity:
    """Classify a finite sidereal Moon longitude into one Vashya category.

    Raises:
        TypeError: If the longitude is a boolean or is not a real number.
        ValueError: If the longitude is NaN or infinite.
    """

    normalized_longitude = normalize_longitude(sidereal_moon_longitude)
    rashi = get_rashi(normalized_longitude)
    rashi_index = rashi["index"]
    degree_in_rashi = rashi["degree_in_rashi"]

    if rashi_index == 9:
        vashya = (
            VASHYA_MANAVA if degree_in_rashi < 15.0 else VASHYA_CHATUSHPADA
        )
    elif rashi_index == 10:
        vashya = (
            VASHYA_CHATUSHPADA if degree_in_rashi < 15.0 else VASHYA_JALACHARA
        )
    else:
        vashya = VASHYA_BY_WHOLE_RASHI_INDEX[rashi_index]

    return {
        "is_valid": True,
        "sidereal_moon_longitude": normalized_longitude,
        "rashi": rashi["sanskrit"],
        "rashi_index": rashi_index,
        "degree_in_rashi": degree_in_rashi,
        "vashya": vashya,
        "errors": [],
        "warnings": [],
        "metadata": _metadata("matchmaking_vashya_identity"),
    }


def get_vashya_score(bride_vashya: str, groom_vashya: str) -> float:
    """Return the strict bride-row/groom-column score for two categories.

    Raises:
        TypeError: If either category is not a string.
        ValueError: If either category is not a canonical identifier.
    """

    _validate_vashya_category(bride_vashya, "bride_vashya")
    _validate_vashya_category(groom_vashya, "groom_vashya")
    return VASHYA_SCORING_MATRIX[bride_vashya][groom_vashya]


def calculate_vashya_koota(
    *,
    bride_moon_longitude: object = None,
    groom_moon_longitude: object = None,
) -> MatchmakingVashyaKootaResult:
    """Calculate directional Vashya Koota from explicitly assigned roles."""

    bride_identity = _classify_for_result(bride_moon_longitude)
    groom_identity = _classify_for_result(groom_moon_longitude)
    errors = [
        *_prefix_issues("bride", bride_identity["errors"]),
        *_prefix_issues("groom", groom_identity["errors"]),
    ]

    score: float | None = None
    factors: list[MatchmakingJsonValue] = []
    if not errors:
        bride_category = bride_identity["vashya"]
        groom_category = groom_identity["vashya"]
        score = get_vashya_score(bride_category, groom_category)
        factors.append(
            {
                "factor": "vashya_directional_matrix",
                "row_role": "bride",
                "column_role": "groom",
                "bride_vashya": bride_category,
                "groom_vashya": groom_category,
                "awarded_score": score,
            }
        )

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": VASHYA_KOOTA_ID,
        "compatibility_domain": VASHYA_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": VASHYA_KOOTA_MAXIMUM_SCORE,
        "bride_vashya": bride_identity,
        "groom_vashya": groom_identity,
        "direction": {"row_role": "bride", "column_role": "groom"},
        "factors": factors,
        "errors": errors,
        "warnings": [],
        "references": [],
        "metadata": _metadata("matchmaking_vashya_koota"),
    }


def _classify_for_result(value: object) -> MatchmakingVashyaIdentity:
    try:
        return classify_vashya(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        code = MOON_LONGITUDE_MISSING if value in (None, "") else MOON_LONGITUDE_INVALID
        issue = _issue("sidereal_moon_longitude", code, value)
        return {
            "is_valid": False,
            "sidereal_moon_longitude": None,
            "rashi": "",
            "rashi_index": None,
            "degree_in_rashi": None,
            "vashya": "",
            "errors": [issue],
            "warnings": [],
            "metadata": _metadata("matchmaking_vashya_identity"),
        }


def _validate_vashya_category(value: object, field: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    if value not in VASHYA_CATEGORIES:
        raise ValueError(f"{field} must be a canonical Vashya category")


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingVashyaIssue],
) -> list[MatchmakingVashyaIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _issue(field: str, code: str, value: object) -> MatchmakingVashyaIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingVashyaMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": VASHYA_CALCULATION_NAME,
        "maximum_score": VASHYA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": VASHYA_COMPATIBILITY_DOMAIN,
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
    return str(value)
