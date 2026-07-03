"""Foundation-level Sthana Bala positional strength helper."""

from __future__ import annotations

from typing import Literal, TypedDict

from backend.app.kundali import dignity, graha_lordship, mooltrikona

STHANA_BALA_COMPONENT = "sthana_bala"
STHANA_BALA_MAX_SCORE = 60

SthanaBalaStatus = Literal[
    "exalted",
    "mooltrikona",
    "own_sign",
    "neutral",
    "debilitated",
    "invalid_input",
]

STHANA_BALA_SCORES: dict[SthanaBalaStatus, int | None] = {
    "exalted": 60,
    "mooltrikona": 45,
    "own_sign": 30,
    "neutral": 15,
    "debilitated": 0,
    "invalid_input": None,
}

STHANA_BALA_REASONS: dict[SthanaBalaStatus, str] = {
    "exalted": "Planet is in its exaltation sign.",
    "mooltrikona": "Planet is in its Mooltrikona sign.",
    "own_sign": "Planet is in a sign it owns.",
    "neutral": "Planet is in a neutral or other supported sign.",
    "debilitated": "Planet is in its debilitation sign.",
    "invalid_input": "Planet or Rashi is not supported for Sthana Bala foundation.",
}


class SthanaBalaResult(TypedDict):
    """JSON-safe Sthana Bala foundation result."""

    planet: str
    rashi: str
    component: str
    status: str
    score: int | None
    max_score: int
    reason: str


def calculate_sthana_bala(planet: str, rashi: str) -> SthanaBalaResult:
    """Calculate foundation-level positional strength for a planet in a Rashi.

    This helper intentionally implements only the Sprint 7 placeholder scoring
    boundary. It reuses existing dignity, Mooltrikona, and lordship metadata and
    does not calculate full classical Shadbala.
    """

    planet_key = _normalize_output_value(planet)
    rashi_key = _normalize_output_value(rashi)

    try:
        dignity_status = dignity.get_planet_dignity(planet, rashi)
        rashi_lord = graha_lordship.get_rashi_lord(rashi)
        is_mooltrikona = mooltrikona.is_mooltrikona(planet, rashi)
    except (TypeError, ValueError):
        return _create_result(planet_key, rashi_key, "invalid_input")

    if dignity_status == "exalted":
        return _create_result(planet_key, rashi_key, "exalted")

    if dignity_status == "debilitated":
        return _create_result(planet_key, rashi_key, "debilitated")

    if is_mooltrikona:
        return _create_result(planet_key, rashi_key, "mooltrikona")

    if planet_key == rashi_lord.strip().casefold():
        return _create_result(planet_key, rashi_key, "own_sign")

    return _create_result(planet_key, rashi_key, "neutral")


def _create_result(
    planet: str,
    rashi: str,
    status: SthanaBalaStatus,
) -> SthanaBalaResult:
    """Create a JSON-safe Sthana Bala result."""

    return {
        "planet": planet,
        "rashi": rashi,
        "component": STHANA_BALA_COMPONENT,
        "status": status,
        "score": STHANA_BALA_SCORES[status],
        "max_score": STHANA_BALA_MAX_SCORE,
        "reason": STHANA_BALA_REASONS[status],
    }


def _normalize_output_value(value: object) -> str:
    """Normalize result display values without validating astrology metadata."""

    return str(value).strip().casefold()
