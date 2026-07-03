"""Dasha system constants and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

VIMSHOTTARI_TOTAL_CYCLE_YEARS = 120


@dataclass(frozen=True)
class DashaPeriodDefinition:
    """Immutable Vimshottari Mahadasha definition."""

    planet: str
    duration_years: int


VIMSHOTTARI_DASHA_SEQUENCE: tuple[DashaPeriodDefinition, ...] = (
    DashaPeriodDefinition("ketu", 7),
    DashaPeriodDefinition("venus", 20),
    DashaPeriodDefinition("sun", 6),
    DashaPeriodDefinition("moon", 10),
    DashaPeriodDefinition("mars", 7),
    DashaPeriodDefinition("rahu", 18),
    DashaPeriodDefinition("jupiter", 16),
    DashaPeriodDefinition("saturn", 19),
    DashaPeriodDefinition("mercury", 17),
)

VIMSHOTTARI_DASHA_DURATIONS: Mapping[str, int] = MappingProxyType(
    {
        definition.planet: definition.duration_years
        for definition in VIMSHOTTARI_DASHA_SEQUENCE
    }
)


def get_dasha_sequence() -> tuple[str, ...]:
    """Return the classical Vimshottari Mahadasha planet sequence."""

    return tuple(definition.planet for definition in VIMSHOTTARI_DASHA_SEQUENCE)


def get_dasha_duration(planet: str) -> int:
    """Return the Vimshottari Mahadasha duration for a planet.

    Args:
        planet: Planet key. Matching is case-insensitive and ignores
            surrounding whitespace.

    Raises:
        TypeError: If planet is not a string.
        ValueError: If planet is not supported by Vimshottari Dasha.
    """

    normalized_planet = _normalize_planet_name(planet)
    try:
        return VIMSHOTTARI_DASHA_DURATIONS[normalized_planet]
    except KeyError as exc:
        supported = ", ".join(get_dasha_sequence())
        raise ValueError(
            f"Unsupported Vimshottari Dasha planet: {planet}. "
            f"Supported planets: {supported}"
        ) from exc


def get_total_cycle_years() -> int:
    """Return the total Vimshottari Dasha cycle duration in years."""

    return sum(definition.duration_years for definition in VIMSHOTTARI_DASHA_SEQUENCE)


def _normalize_planet_name(planet: str) -> str:
    """Normalize and validate a planet key for Dasha lookup."""

    if not isinstance(planet, str):
        raise TypeError("planet must be a string")

    normalized = planet.strip().lower()
    if not normalized:
        raise ValueError("planet must not be empty")

    return normalized
