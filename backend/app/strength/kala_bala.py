"""Foundation-level Kala Bala time-period strength helper."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, TypedDict

KALA_BALA_COMPONENT = "kala_bala"
KALA_BALA_MAX_SCORE = 60

KALA_BALA_DAY_PLANETS = frozenset({"sun", "jupiter", "venus"})
KALA_BALA_NIGHT_PLANETS = frozenset({"moon", "mars", "saturn"})
KALA_BALA_NEUTRAL_PLANETS = frozenset({"mercury"})
KALA_BALA_SUPPORTED_PLANETS = (
    KALA_BALA_DAY_PLANETS | KALA_BALA_NIGHT_PLANETS | KALA_BALA_NEUTRAL_PLANETS
)

KalaBalaStatus = Literal[
    "preferred_period",
    "neutral",
    "non_preferred_period",
    "invalid_input",
]
KalaBalaTimePeriod = Literal["daytime", "nighttime", "unknown"]

KALA_BALA_SCORES: dict[KalaBalaStatus, int | None] = {
    "preferred_period": 60,
    "neutral": 30,
    "non_preferred_period": 15,
    "invalid_input": None,
}

KALA_BALA_REASONS: dict[KalaBalaStatus, str] = {
    "preferred_period": "Planet is in its preferred day/night period.",
    "neutral": "Planet has neutral or unknown day/night strength.",
    "non_preferred_period": "Planet is outside its preferred day/night period.",
    "invalid_input": (
        "Planet or datetime input is not supported for Kala Bala foundation."
    ),
}


class KalaBalaResult(TypedDict):
    """JSON-safe Kala Bala foundation result."""

    planet: str
    component: str
    time_period: str
    status: str
    score: int | None
    max_score: int
    reason: str


def calculate_kala_bala(
    planet: str,
    birth_datetime: datetime | str,
    sunrise_datetime: datetime | str | None = None,
    sunset_datetime: datetime | str | None = None,
) -> KalaBalaResult:
    """Calculate foundation-level time-period strength for a planet.

    This helper uses supplied sunrise and sunset boundaries when available. It
    does not call Panchang or astronomy code directly, so existing calculation
    behavior remains unchanged.
    """

    planet_key = _normalize_planet(planet)
    if planet_key not in KALA_BALA_SUPPORTED_PLANETS:
        return _create_result(planet_key, "unknown", "invalid_input")

    if sunrise_datetime is None or sunset_datetime is None:
        return _create_result(planet_key, "unknown", "neutral")

    try:
        birth_dt = _parse_datetime(birth_datetime, "birth_datetime")
        sunrise_dt = _parse_datetime(sunrise_datetime, "sunrise_datetime")
        sunset_dt = _parse_datetime(sunset_datetime, "sunset_datetime")
    except (TypeError, ValueError):
        return _create_result(planet_key, "unknown", "invalid_input")

    try:
        is_daytime = sunrise_dt <= birth_dt < sunset_dt
    except TypeError:
        return _create_result(planet_key, "unknown", "invalid_input")

    time_period: KalaBalaTimePeriod = "daytime" if is_daytime else "nighttime"
    if planet_key in KALA_BALA_NEUTRAL_PLANETS:
        return _create_result(planet_key, time_period, "neutral")

    prefers_daytime = planet_key in KALA_BALA_DAY_PLANETS
    is_preferred_period = (prefers_daytime and is_daytime) or (
        not prefers_daytime and not is_daytime
    )

    if is_preferred_period:
        return _create_result(planet_key, time_period, "preferred_period")

    return _create_result(planet_key, time_period, "non_preferred_period")


def _create_result(
    planet: str,
    time_period: KalaBalaTimePeriod,
    status: KalaBalaStatus,
) -> KalaBalaResult:
    """Create a JSON-safe Kala Bala result."""

    return {
        "planet": planet,
        "component": KALA_BALA_COMPONENT,
        "time_period": time_period,
        "status": status,
        "score": KALA_BALA_SCORES[status],
        "max_score": KALA_BALA_MAX_SCORE,
        "reason": KALA_BALA_REASONS[status],
    }


def _normalize_planet(planet: object) -> str:
    """Normalize planet output without validating astrology metadata."""

    return str(planet).strip().casefold()


def _parse_datetime(value: datetime | str, field_name: str) -> datetime:
    """Parse a datetime object or ISO datetime string."""

    if isinstance(value, datetime):
        return value.replace(microsecond=0)

    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"

        try:
            return datetime.fromisoformat(normalized).replace(microsecond=0)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid ISO datetime") from exc

    raise TypeError(f"{field_name} must be a datetime object or ISO datetime string")
