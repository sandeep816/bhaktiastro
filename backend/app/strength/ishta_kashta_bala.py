"""Foundation-level Ishta/Kashta Bala helper."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Real
from typing import Any, Literal, TypedDict

ISHTA_KASHTA_MAX_SCORE = 100.0
ISHTA_KASHTA_NEUTRAL_PERCENTAGE = 50.0
ISHTA_KASHTA_SCORE_PRECISION = 2

ISHTA_KASHTA_SUPPORTED_PLANETS = frozenset(
    {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"}
)

ISHTA_DIGNITY_BONUSES = {
    "exalted": 10.0,
    "mooltrikona": 8.0,
    "own_sign": 5.0,
}
KASHTA_DIGNITY_BONUSES = {
    "debilitated": 10.0,
}

IshtaKashtaBalaStatus = Literal[
    "favorable",
    "challenging",
    "balanced",
    "unsupported",
]

ISHTA_KASHTA_REASONS: dict[IshtaKashtaBalaStatus, str] = {
    "favorable": "Ishta score is greater than Kashta score.",
    "challenging": "Kashta score is greater than Ishta score.",
    "balanced": "Ishta and Kashta scores are balanced.",
    "unsupported": "Planet is not supported for Ishta/Kashta Bala foundation.",
}


class IshtaKashtaBalaMetadata(TypedDict):
    """JSON-safe Ishta/Kashta Bala metadata."""

    calculation_status: str
    shadbala_status: str
    strength_percentage: float
    dignity_status: str | None
    ishta_bonus: float
    kashta_bonus: float


class IshtaKashtaBalaResult(TypedDict):
    """JSON-safe Ishta/Kashta Bala foundation result."""

    planet: str
    ishta_score: float
    kashta_score: float
    total: float
    status: str
    reason: str
    metadata: IshtaKashtaBalaMetadata


def calculate_ishta_kashta_bala(
    planet: str,
    shadbala_result: dict[str, Any] | None = None,
    dignity_status: str | None = None,
) -> IshtaKashtaBalaResult:
    """Calculate foundation-level Ishta/Kashta Bala from Shadbala strength.

    This helper intentionally implements only the Sprint 7 placeholder scoring
    boundary. It consumes an existing Shadbala aggregate result when available
    and does not calculate full classical Ishta/Kashta Bala.
    """

    planet_key = _normalize_text(planet)
    if planet_key not in ISHTA_KASHTA_SUPPORTED_PLANETS:
        return _create_result(
            planet_key,
            0.0,
            0.0,
            "unsupported",
            _create_metadata(
                "unsupported",
                0.0,
                _normalize_optional_text(dignity_status),
                0.0,
                0.0,
            ),
        )

    strength_percentage, shadbala_status = _get_strength_percentage(shadbala_result)
    normalized_dignity_status = _normalize_optional_text(dignity_status)
    ishta_bonus = ISHTA_DIGNITY_BONUSES.get(normalized_dignity_status or "", 0.0)
    kashta_bonus = KASHTA_DIGNITY_BONUSES.get(normalized_dignity_status or "", 0.0)

    ishta_score = _round_score(_clamp_score(strength_percentage + ishta_bonus))
    kashta_score = _round_score(
        _clamp_score((ISHTA_KASHTA_MAX_SCORE - strength_percentage) + kashta_bonus)
    )
    status = _get_status(ishta_score, kashta_score)

    return _create_result(
        planet_key,
        ishta_score,
        kashta_score,
        status,
        _create_metadata(
            shadbala_status,
            strength_percentage,
            normalized_dignity_status,
            ishta_bonus,
            kashta_bonus,
        ),
    )


def _create_result(
    planet: str,
    ishta_score: float,
    kashta_score: float,
    status: IshtaKashtaBalaStatus,
    metadata: IshtaKashtaBalaMetadata,
) -> IshtaKashtaBalaResult:
    """Create a JSON-safe Ishta/Kashta Bala result."""

    return {
        "planet": planet,
        "ishta_score": ishta_score,
        "kashta_score": kashta_score,
        "total": _round_score(ishta_score + kashta_score),
        "status": status,
        "reason": ISHTA_KASHTA_REASONS[status],
        "metadata": metadata,
    }


def _create_metadata(
    shadbala_status: str,
    strength_percentage: float,
    dignity_status: str | None,
    ishta_bonus: float,
    kashta_bonus: float,
) -> IshtaKashtaBalaMetadata:
    """Create JSON-safe foundation metadata."""

    return {
        "calculation_status": "foundation",
        "shadbala_status": shadbala_status,
        "strength_percentage": _round_score(strength_percentage),
        "dignity_status": dignity_status,
        "ishta_bonus": _round_score(ishta_bonus),
        "kashta_bonus": _round_score(kashta_bonus),
    }


def _get_strength_percentage(
    shadbala_result: dict[str, Any] | None,
) -> tuple[float, str]:
    """Return a safe Shadbala percentage and metadata status."""

    if not isinstance(shadbala_result, Mapping):
        return ISHTA_KASHTA_NEUTRAL_PERCENTAGE, "missing"

    strength_percentage = shadbala_result.get("strength_percentage")
    if isinstance(strength_percentage, bool) or not isinstance(
        strength_percentage, Real
    ):
        return ISHTA_KASHTA_NEUTRAL_PERCENTAGE, "placeholder"

    return (
        _round_score(_clamp_score(float(strength_percentage))),
        _normalize_text(shadbala_result.get("status") or "provided"),
    )


def _get_status(
    ishta_score: float,
    kashta_score: float,
) -> IshtaKashtaBalaStatus:
    """Return Ishta/Kashta foundation status."""

    if ishta_score > kashta_score:
        return "favorable"

    if kashta_score > ishta_score:
        return "challenging"

    return "balanced"


def _clamp_score(score: float) -> float:
    """Clamp score to the foundation min/max range."""

    return max(0.0, min(ISHTA_KASHTA_MAX_SCORE, score))


def _round_score(score: float) -> float:
    """Round score with the shared foundation precision."""

    return round(score, ISHTA_KASHTA_SCORE_PRECISION)


def _normalize_text(value: object) -> str:
    """Normalize text output without validating astrology metadata."""

    return str(value or "").strip().casefold()


def _normalize_optional_text(value: object) -> str | None:
    """Normalize optional text into a JSON-safe string or None."""

    if value is None:
        return None

    normalized_value = _normalize_text(value)
    return normalized_value or None
