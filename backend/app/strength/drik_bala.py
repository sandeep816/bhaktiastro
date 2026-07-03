"""Foundation-level Drik Bala aspect strength helper."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypedDict

from backend.app.kundali import drishti

DRIK_BALA_COMPONENT = "drik_bala"
DRIK_BALA_MAX_SCORE = 60
DRIK_BALA_MIN_SCORE = -60
DRIK_BALA_ASPECT_SCORE = 15

DRIK_BALA_BENEFICS = frozenset({"jupiter", "venus", "mercury", "moon"})
DRIK_BALA_MALEFICS = frozenset({"sun", "mars", "saturn"})

DrikBalaStatus = Literal[
    "positive",
    "negative",
    "mixed",
    "neutral",
    "unsupported",
]
AspectClassification = Literal["benefic", "malefic", "unsupported"]

DRIK_BALA_REASONS: dict[DrikBalaStatus, str] = {
    "positive": "Benefic received aspects outweigh malefic received aspects.",
    "negative": "Malefic received aspects outweigh benefic received aspects.",
    "mixed": "Benefic and malefic received aspects balance each other.",
    "neutral": "No supported received aspects were provided.",
    "unsupported": "Planet is not supported for Drik Bala foundation.",
}


class DrikBalaAspect(TypedDict):
    """JSON-safe received aspect metadata for Drik Bala foundation."""

    from_planet: str
    aspect_type: str | None
    strength: float | int | str | bool | None
    classification: str
    score: int


class DrikBalaResult(TypedDict):
    """JSON-safe Drik Bala foundation result."""

    planet: str
    component: str
    status: str
    score: int
    max_score: int
    received_aspects: list[DrikBalaAspect]
    reason: str


def calculate_drik_bala(
    planet: str,
    received_aspects: list[dict[str, Any]] | None = None,
) -> DrikBalaResult:
    """Calculate foundation-level aspect strength from received aspects.

    This helper scores already-supplied aspect metadata. It does not calculate
    Graha Drishti placements or mutate Kundali chart data.
    """

    planet_key = _normalize_planet(planet)
    if not drishti.supports_drishti(planet_key):
        return _create_result(planet_key, "unsupported", 0, [])

    aspects = _normalize_received_aspects(received_aspects)
    score = _clamp_score(sum(aspect["score"] for aspect in aspects))
    status = _get_status(score, aspects)

    return _create_result(planet_key, status, score, aspects)


def _create_result(
    planet: str,
    status: DrikBalaStatus,
    score: int,
    received_aspects: list[DrikBalaAspect],
) -> DrikBalaResult:
    """Create a JSON-safe Drik Bala result."""

    return {
        "planet": planet,
        "component": DRIK_BALA_COMPONENT,
        "status": status,
        "score": score,
        "max_score": DRIK_BALA_MAX_SCORE,
        "received_aspects": received_aspects,
        "reason": DRIK_BALA_REASONS[status],
    }


def _normalize_received_aspects(
    received_aspects: list[dict[str, Any]] | None,
) -> list[DrikBalaAspect]:
    """Normalize received aspect dictionaries and skip unsafe entries."""

    if received_aspects is None:
        return []

    if not isinstance(received_aspects, list):
        return []

    normalized_aspects: list[DrikBalaAspect] = []
    for aspect in received_aspects:
        normalized_aspect = _normalize_aspect(aspect)
        if normalized_aspect is not None:
            normalized_aspects.append(normalized_aspect)

    return normalized_aspects


def _normalize_aspect(aspect: object) -> DrikBalaAspect | None:
    """Return normalized aspect metadata, or None for malformed input."""

    if not isinstance(aspect, Mapping):
        return None

    from_planet = aspect.get("from_planet")
    if not isinstance(from_planet, str) or not from_planet.strip():
        return None

    planet_key = _normalize_planet(from_planet)
    classification = _classify_aspect_planet(planet_key)
    score = _get_aspect_score(classification)

    return {
        "from_planet": planet_key,
        "aspect_type": _normalize_optional_string(aspect.get("aspect_type")),
        "strength": _json_safe_scalar(aspect.get("strength")),
        "classification": classification,
        "score": score,
    }


def _classify_aspect_planet(planet: str) -> AspectClassification:
    """Return the natural aspect classification for a planet."""

    if planet in DRIK_BALA_BENEFICS:
        return "benefic"

    if planet in DRIK_BALA_MALEFICS:
        return "malefic"

    return "unsupported"


def _get_aspect_score(classification: AspectClassification) -> int:
    """Return the placeholder score contribution for one received aspect."""

    if classification == "benefic":
        return DRIK_BALA_ASPECT_SCORE

    if classification == "malefic":
        return -DRIK_BALA_ASPECT_SCORE

    return 0


def _get_status(
    score: int,
    received_aspects: list[DrikBalaAspect],
) -> DrikBalaStatus:
    """Return the Drik Bala foundation status for a score."""

    supported_aspects = [
        aspect
        for aspect in received_aspects
        if aspect["classification"] in {"benefic", "malefic"}
    ]
    if not supported_aspects:
        return "neutral"

    if score > 0:
        return "positive"

    if score < 0:
        return "negative"

    return "mixed"


def _clamp_score(score: int) -> int:
    """Clamp Drik Bala score to the foundation min/max range."""

    return max(DRIK_BALA_MIN_SCORE, min(DRIK_BALA_MAX_SCORE, score))


def _normalize_planet(planet: object) -> str:
    """Normalize planet output without validating astrology metadata."""

    return str(planet).strip().casefold()


def _normalize_optional_string(value: object) -> str | None:
    """Normalize optional text metadata into a JSON-safe string or None."""

    if value is None:
        return None

    return str(value).strip().casefold()


def _json_safe_scalar(value: object) -> float | int | str | bool | None:
    """Return a JSON-safe scalar placeholder value."""

    if value is None or isinstance(value, bool | int | float | str):
        return value

    return str(value)
