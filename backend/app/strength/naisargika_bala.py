"""Foundation-level Naisargika Bala natural strength helper."""

from __future__ import annotations

from types import MappingProxyType
from typing import Literal, Mapping, TypedDict

NAISARGIKA_BALA_COMPONENT = "naisargika_bala"
NAISARGIKA_BALA_MAX_SCORE = 60.0

NaisargikaBalaStatus = Literal["supported", "unsupported"]

NAISARGIKA_BALA_SCORES: Mapping[str, float] = MappingProxyType(
    {
        "sun": 60.0,
        "moon": 51.43,
        "venus": 42.86,
        "jupiter": 34.29,
        "mercury": 25.71,
        "mars": 17.14,
        "saturn": 8.57,
    }
)

NAISARGIKA_BALA_REASONS: dict[NaisargikaBalaStatus, str] = {
    "supported": "Planet has a natural strength mapping.",
    "unsupported": "Planet is not supported for Naisargika Bala foundation.",
}


class NaisargikaBalaResult(TypedDict):
    """JSON-safe Naisargika Bala foundation result."""

    planet: str
    component: str
    status: str
    score: float
    max_score: float
    reason: str


def calculate_naisargika_bala(planet: str) -> NaisargikaBalaResult:
    """Return foundation-level natural planetary strength for a planet."""

    planet_key = _normalize_planet(planet)
    score = NAISARGIKA_BALA_SCORES.get(planet_key)
    if score is None:
        return _create_result(planet_key, "unsupported", 0.0)

    return _create_result(planet_key, "supported", score)


def _create_result(
    planet: str,
    status: NaisargikaBalaStatus,
    score: float,
) -> NaisargikaBalaResult:
    """Create a JSON-safe Naisargika Bala result."""

    return {
        "planet": planet,
        "component": NAISARGIKA_BALA_COMPONENT,
        "status": status,
        "score": score,
        "max_score": NAISARGIKA_BALA_MAX_SCORE,
        "reason": NAISARGIKA_BALA_REASONS[status],
    }


def _normalize_planet(planet: object) -> str:
    """Normalize planet output without validating astrology metadata."""

    return str(planet).strip().casefold()
