"""Deterministic Tara Koota classification and bidirectional scoring."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Literal, TypedDict

from backend.app.constants.nakshatra import NAKSHATRA_COUNT
from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MATCHMAKING_STATUSES
from backend.app.matchmaking.foundation import MatchmakingJsonValue
from backend.app.matchmaking.nakshatra import MATCHMAKING_NAKSHATRA_ISSUE_CODES
from backend.app.matchmaking.nakshatra import MatchmakingNakshatraIdentity
from backend.app.matchmaking.nakshatra import MatchmakingNakshatraIssue
from backend.app.matchmaking.nakshatra import build_nakshatra_pair_context
from backend.app.matchmaking.nakshatra import calculate_nakshatra_distance

TARA_KOOTA_ID = "tara"
TARA_KOOTA_MAXIMUM_SCORE = 3.0
TARA_DIRECTIONAL_MAXIMUM_SCORE = 1.5
TARA_COMPATIBILITY_DOMAIN = "destiny"
TARA_CALCULATION_NAME = "tara_koota"

TARA_JANMA = "janma"
TARA_SAMPAT = "sampat"
TARA_VIPAT = "vipat"
TARA_KSHEMA = "kshema"
TARA_PRATYARI = "pratyari"
TARA_SADHAKA = "sadhaka"
TARA_VADHA = "vadha"
TARA_MITRA = "mitra"
TARA_ATI_MITRA = "ati_mitra"

TARA_FAVORABLE_NUMBERS = (2, 4, 6, 8, 9)
TARA_UNFAVORABLE_NUMBERS = (1, 3, 5, 7)


class TaraDefinition(TypedDict):
    """One canonical Tara classification definition."""

    identifier: str
    display_name: str
    favorable: bool


TARA_CLASSIFICATIONS: dict[int, TaraDefinition] = {
    1: {"identifier": TARA_JANMA, "display_name": "Janma", "favorable": False},
    2: {"identifier": TARA_SAMPAT, "display_name": "Sampat", "favorable": True},
    3: {"identifier": TARA_VIPAT, "display_name": "Vipat", "favorable": False},
    4: {"identifier": TARA_KSHEMA, "display_name": "Kshema", "favorable": True},
    5: {
        "identifier": TARA_PRATYARI,
        "display_name": "Pratyari",
        "favorable": False,
    },
    6: {
        "identifier": TARA_SADHAKA,
        "display_name": "Sadhaka",
        "favorable": True,
    },
    7: {"identifier": TARA_VADHA, "display_name": "Vadha", "favorable": False},
    8: {"identifier": TARA_MITRA, "display_name": "Mitra", "favorable": True},
    9: {
        "identifier": TARA_ATI_MITRA,
        "display_name": "Ati Mitra / Parama Mitra",
        "favorable": True,
    },
}

TARA_REFERENCES = (
    "https://www.ghvisweswara.com/wp-content/uploads/2021/11/"
    "Comparison_of_Panchangas.pdf",
    "https://astromedha.in/insights/vedic/tara-koota",
)

DIRECTION_MISSING = "direction_missing"
ROLE_INVALID = "role_invalid"

MATCHMAKING_TARA_ISSUE_CODES = (
    *MATCHMAKING_NAKSHATRA_ISSUE_CODES,
    DIRECTION_MISSING,
    ROLE_INVALID,
)

_VALID_PAIR_ROLES = ("person_a", "person_b")

MatchmakingTaraIssueSeverity = Literal["error", "warning"]


class MatchmakingTaraIssue(TypedDict):
    """One localization-ready Tara Koota issue."""

    field: str
    code: str
    message_key: str
    severity: MatchmakingTaraIssueSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingTaraMetadata(TypedDict):
    """Stable metadata for Tara Koota objects."""

    component: str
    schema_version: str
    deterministic: bool
    calculation: str
    maximum_score: float
    compatibility_domain: str
    directional: bool
    nakshatra_count: int
    index_base: int


class MatchmakingTaraClassification(TypedDict):
    """Canonical modulo-9 Tara classification."""

    inclusive_count: int
    tara_number: int
    tara: str
    tara_name: str
    favorable: bool
    score: float


class MatchmakingTaraDirectionalResult(TypedDict):
    """One directional Tara calculation."""

    source_role: str
    destination_role: str
    source_nakshatra: str
    destination_nakshatra: str
    source_index: int | None
    destination_index: int | None
    circular_distance: int | None
    inclusive_count: int | None
    tara_number: int | None
    tara: str
    tara_name: str
    favorable: bool | None
    score: float | None


class MatchmakingTaraKootaResult(TypedDict):
    """Structured Tara Koota score without compatibility judgement."""

    koota: str
    compatibility_domain: str
    status: str
    score: float | None
    maximum_score: float
    person_a_nakshatra: MatchmakingNakshatraIdentity
    person_b_nakshatra: MatchmakingNakshatraIdentity
    direction: dict[str, str]
    bride_to_groom: MatchmakingTaraDirectionalResult
    groom_to_bride: MatchmakingTaraDirectionalResult
    same_nakshatra: bool | None
    same_pada: bool | None
    factors: list[MatchmakingJsonValue]
    errors: list[MatchmakingTaraIssue]
    warnings: list[MatchmakingTaraIssue]
    references: list[str]
    metadata: MatchmakingTaraMetadata


def calculate_tara_inclusive_count(
    index_from: object,
    index_to: object,
) -> int | None:
    """Return the inclusive circular count for two canonical indexes."""

    distance = calculate_nakshatra_distance(index_from, index_to)
    return distance + 1 if distance is not None else None


def classify_tara(inclusive_count: object) -> MatchmakingTaraClassification:
    """Classify one inclusive count from 1 through 27 using modulo 9.

    Raises:
        TypeError: If ``inclusive_count`` is a boolean or not an integer.
        ValueError: If ``inclusive_count`` is outside ``1..27``.
    """

    if isinstance(inclusive_count, bool) or not isinstance(inclusive_count, Integral):
        raise TypeError("inclusive_count must be an integer")

    count = int(inclusive_count)
    if not 1 <= count <= NAKSHATRA_COUNT:
        raise ValueError(f"inclusive_count must be between 1 and {NAKSHATRA_COUNT}")

    tara_number = ((count - 1) % 9) + 1
    definition = TARA_CLASSIFICATIONS[tara_number]
    favorable = definition["favorable"]
    return {
        "inclusive_count": count,
        "tara_number": tara_number,
        "tara": definition["identifier"],
        "tara_name": definition["display_name"],
        "favorable": favorable,
        "score": TARA_DIRECTIONAL_MAXIMUM_SCORE if favorable else 0.0,
    }


def calculate_tara_direction(
    index_from: object,
    index_to: object,
    *,
    source_role: str,
    destination_role: str,
    source_nakshatra: str = "",
    destination_nakshatra: str = "",
) -> MatchmakingTaraDirectionalResult:
    """Calculate one explicit bride/groom Tara direction from valid indexes."""

    _validate_direction_roles(source_role, destination_role)
    distance = calculate_nakshatra_distance(index_from, index_to)
    if distance is None:
        raise ValueError("Nakshatra indexes must be zero-based values from 0 to 26")

    inclusive_count = distance + 1
    classification = classify_tara(inclusive_count)
    return {
        "source_role": source_role,
        "destination_role": destination_role,
        "source_nakshatra": source_nakshatra,
        "destination_nakshatra": destination_nakshatra,
        "source_index": int(index_from),
        "destination_index": int(index_to),
        "circular_distance": distance,
        "inclusive_count": inclusive_count,
        "tara_number": classification["tara_number"],
        "tara": classification["tara"],
        "tara_name": classification["tara_name"],
        "favorable": classification["favorable"],
        "score": classification["score"],
    }


def calculate_tara_koota(
    pair: object,
    *,
    bride_role: object = None,
    groom_role: object = None,
) -> MatchmakingTaraKootaResult:
    """Calculate Tara Koota for an ordered pair with explicit marriage roles."""

    context = build_nakshatra_pair_context(pair)
    bride = _normalize_role(bride_role)
    groom = _normalize_role(groom_role)
    role_errors = _validate_pair_roles(bride, groom, bride_role, groom_role)

    identities = {
        "person_a": context["person_a"],
        "person_b": context["person_b"],
    }
    if not role_errors and bride and groom:
        errors = [
            *_prefix_issues("bride", identities[bride]["errors"]),
            *_prefix_issues("groom", identities[groom]["errors"]),
        ]
    else:
        errors = [_copy_issue(issue) for issue in context["errors"]]
    errors.extend(role_errors)

    bride_to_groom = _empty_direction("bride", "groom")
    groom_to_bride = _empty_direction("groom", "bride")
    score: float | None = None
    factors: list[MatchmakingJsonValue] = []

    if not errors and bride and groom:
        bride_identity = identities[bride]
        groom_identity = identities[groom]
        bride_index = bride_identity["index"]
        groom_index = groom_identity["index"]
        if bride_index is not None and groom_index is not None:
            bride_to_groom = calculate_tara_direction(
                bride_index,
                groom_index,
                source_role="bride",
                destination_role="groom",
                source_nakshatra=bride_identity["name"],
                destination_nakshatra=groom_identity["name"],
            )
            groom_to_bride = calculate_tara_direction(
                groom_index,
                bride_index,
                source_role="groom",
                destination_role="bride",
                source_nakshatra=groom_identity["name"],
                destination_nakshatra=bride_identity["name"],
            )
            score = float(bride_to_groom["score"] or 0.0) + float(
                groom_to_bride["score"] or 0.0
            )
            factors = [
                _direction_factor("bride_to_groom", bride_to_groom),
                _direction_factor("groom_to_bride", groom_to_bride),
                {
                    "factor": "tara_directional_total",
                    "awarded_score": score,
                    "maximum_score": TARA_KOOTA_MAXIMUM_SCORE,
                },
            ]

    status = "invalid" if errors else "complete"
    if status not in MATCHMAKING_STATUSES:
        status = "invalid"

    return {
        "koota": TARA_KOOTA_ID,
        "compatibility_domain": TARA_COMPATIBILITY_DOMAIN,
        "status": status,
        "score": score,
        "maximum_score": TARA_KOOTA_MAXIMUM_SCORE,
        "person_a_nakshatra": context["person_a"],
        "person_b_nakshatra": context["person_b"],
        "direction": {"bride_role": bride, "groom_role": groom},
        "bride_to_groom": bride_to_groom,
        "groom_to_bride": groom_to_bride,
        "same_nakshatra": context["same_nakshatra"],
        "same_pada": context["same_pada"],
        "factors": factors,
        "errors": errors,
        "warnings": [_copy_issue(issue) for issue in context["warnings"]],
        "references": list(TARA_REFERENCES),
        "metadata": _metadata("matchmaking_tara_koota"),
    }


def _validate_direction_roles(source_role: object, destination_role: object) -> None:
    if not isinstance(source_role, str) or not isinstance(destination_role, str):
        raise TypeError("direction roles must be strings")
    if (source_role, destination_role) not in (("bride", "groom"), ("groom", "bride")):
        raise ValueError("direction must be bride-to-groom or groom-to-bride")


def _validate_pair_roles(
    bride: str,
    groom: str,
    raw_bride: object,
    raw_groom: object,
) -> list[MatchmakingTaraIssue]:
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


def _empty_direction(
    source_role: str,
    destination_role: str,
) -> MatchmakingTaraDirectionalResult:
    return {
        "source_role": source_role,
        "destination_role": destination_role,
        "source_nakshatra": "",
        "destination_nakshatra": "",
        "source_index": None,
        "destination_index": None,
        "circular_distance": None,
        "inclusive_count": None,
        "tara_number": None,
        "tara": "",
        "tara_name": "",
        "favorable": None,
        "score": None,
    }


def _direction_factor(
    factor: str,
    result: MatchmakingTaraDirectionalResult,
) -> MatchmakingJsonValue:
    return {
        "factor": factor,
        "inclusive_count": result["inclusive_count"],
        "tara_number": result["tara_number"],
        "tara": result["tara"],
        "favorable": result["favorable"],
        "awarded_score": result["score"],
    }


def _prefix_issues(
    prefix: str,
    issues: list[MatchmakingNakshatraIssue],
) -> list[MatchmakingTaraIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _copy_issue(issue: MatchmakingNakshatraIssue) -> MatchmakingTaraIssue:
    return {**issue, "metadata": dict(issue["metadata"])}


def _issue(field: str, code: str, value: object) -> MatchmakingTaraIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _metadata(component: str) -> MatchmakingTaraMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": TARA_CALCULATION_NAME,
        "maximum_score": TARA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": TARA_COMPATIBILITY_DOMAIN,
        "directional": True,
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
