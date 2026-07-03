"""Foundation-level Chesta Bala motion strength helper."""

from __future__ import annotations

from typing import Literal, TypedDict

from backend.app.astronomy import retrograde

CHESTA_BALA_COMPONENT = "chesta_bala"
CHESTA_BALA_MAX_SCORE = 60

CHESTA_BALA_SUPPORTED_PLANETS = frozenset(
    {"mars", "mercury", "jupiter", "venus", "saturn"}
)

ChestaBalaStatus = Literal[
    "retrograde",
    "stationary",
    "direct",
    "unknown",
    "unsupported",
]

CHESTA_BALA_SCORES: dict[ChestaBalaStatus, int] = {
    "retrograde": 60,
    "stationary": 45,
    "direct": 30,
    "unknown": 0,
    "unsupported": 0,
}

CHESTA_BALA_REASONS: dict[ChestaBalaStatus, str] = {
    "retrograde": "Planet has retrograde longitudinal motion.",
    "stationary": "Planet has stationary longitudinal motion.",
    "direct": "Planet has direct longitudinal motion.",
    "unknown": "Motion data is missing or unsupported for Chesta Bala foundation.",
    "unsupported": "Planet is not supported for Chesta Bala foundation.",
}


class ChestaBalaResult(TypedDict):
    """JSON-safe Chesta Bala foundation result."""

    planet: str
    component: str
    motion_status: str
    status: str
    score: int
    max_score: int
    reason: str


def calculate_chesta_bala(
    planet: str,
    speed_longitude: float | None = None,
    motion_status: str | None = None,
) -> ChestaBalaResult:
    """Calculate foundation-level motion strength for a supported planet.

    Motion status is accepted directly when supplied. Otherwise, speed-based
    status is derived through the existing retrograde helper.
    """

    planet_key = _normalize_planet(planet)
    if planet_key not in CHESTA_BALA_SUPPORTED_PLANETS:
        return _create_result(planet_key, "unknown", "unsupported")

    resolved_motion_status = _resolve_motion_status(
        speed_longitude=speed_longitude,
        motion_status=motion_status,
    )
    if resolved_motion_status is None:
        return _create_result(planet_key, "unknown", "unknown")

    return _create_result(planet_key, resolved_motion_status, resolved_motion_status)


def _create_result(
    planet: str,
    motion_status: str,
    status: ChestaBalaStatus,
) -> ChestaBalaResult:
    """Create a JSON-safe Chesta Bala result."""

    return {
        "planet": planet,
        "component": CHESTA_BALA_COMPONENT,
        "motion_status": motion_status,
        "status": status,
        "score": CHESTA_BALA_SCORES[status],
        "max_score": CHESTA_BALA_MAX_SCORE,
        "reason": CHESTA_BALA_REASONS[status],
    }


def _normalize_planet(planet: object) -> str:
    """Normalize planet output without validating astrology metadata."""

    return str(planet).strip().casefold()


def _resolve_motion_status(
    *,
    speed_longitude: float | None,
    motion_status: str | None,
) -> ChestaBalaStatus | None:
    """Resolve direct or speed-derived motion status."""

    if motion_status is not None:
        return _normalize_motion_status(motion_status)

    if speed_longitude is None:
        return None

    try:
        return retrograde.get_motion_status(speed_longitude)
    except (TypeError, ValueError):
        return None


def _normalize_motion_status(motion_status: object) -> ChestaBalaStatus | None:
    """Normalize a provided motion status, or return None for unknown values."""

    if not isinstance(motion_status, str):
        return None

    normalized = motion_status.strip().casefold()
    if normalized in {"retrograde", "stationary", "direct"}:
        return normalized

    return None
