"""Dasha system constants and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from backend.app.constants.nakshatra import NAKSHATRA_COUNT, NAKSHATRA_LIST

VIMSHOTTARI_TOTAL_CYCLE_YEARS = 120


@dataclass(frozen=True)
class DashaPeriodDefinition:
    """Immutable Vimshottari Mahadasha definition."""

    planet: str
    duration_years: int


def _normalize_name_for_mapping(name: str) -> str:
    """Normalize a name key for case-insensitive lookup."""

    return " ".join(name.strip().lower().split())


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
NAKSHATRA_DASHA_LORDS: Mapping[int, str] = MappingProxyType(
    {
        nakshatra_index: VIMSHOTTARI_DASHA_SEQUENCE[
            nakshatra_index % len(VIMSHOTTARI_DASHA_SEQUENCE)
        ].planet
        for nakshatra_index in range(NAKSHATRA_COUNT)
    }
)
_NAKSHATRA_NAME_TO_INDEX: Mapping[str, int] = MappingProxyType(
    {
        normalized_name: nakshatra.index
        for nakshatra in NAKSHATRA_LIST
        for normalized_name in {
            _normalize_name_for_mapping(nakshatra.name_en),
            _normalize_name_for_mapping(nakshatra.name_sa),
            _normalize_name_for_mapping(nakshatra.name_hi),
        }
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


def get_nakshatra_dasha_lord(nakshatra_index: int) -> str:
    """Return the Vimshottari Mahadasha lord for a Nakshatra index.

    The project Nakshatra constants use zero-based indexes from 0 to 26.

    Raises:
        TypeError: If nakshatra_index is not an integer.
        ValueError: If nakshatra_index is outside the supported range.
    """

    if isinstance(nakshatra_index, bool) or not isinstance(nakshatra_index, int):
        raise TypeError("nakshatra_index must be an integer")

    try:
        return NAKSHATRA_DASHA_LORDS[nakshatra_index]
    except KeyError as exc:
        raise ValueError(
            f"nakshatra_index must be between 0 and {NAKSHATRA_COUNT - 1}"
        ) from exc


def get_nakshatra_dasha_lord_by_name(nakshatra_name: str) -> str:
    """Return the Vimshottari Mahadasha lord for a Nakshatra name.

    English, Sanskrit/transliteration, and Hindi names from the local
    Nakshatra constants are supported.

    Raises:
        TypeError: If nakshatra_name is not a string.
        ValueError: If nakshatra_name is empty or unsupported.
    """

    normalized_name = _normalize_nakshatra_name(nakshatra_name)
    try:
        nakshatra_index = _NAKSHATRA_NAME_TO_INDEX[normalized_name]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported Nakshatra name for Vimshottari Dasha: {nakshatra_name}"
        ) from exc

    return get_nakshatra_dasha_lord(nakshatra_index)


def _normalize_planet_name(planet: str) -> str:
    """Normalize and validate a planet key for Dasha lookup."""

    if not isinstance(planet, str):
        raise TypeError("planet must be a string")

    normalized = planet.strip().lower()
    if not normalized:
        raise ValueError("planet must not be empty")

    return normalized


def _normalize_nakshatra_name(nakshatra_name: str) -> str:
    """Normalize and validate a Nakshatra name for Dasha lookup."""

    if not isinstance(nakshatra_name, str):
        raise TypeError("nakshatra_name must be a string")

    normalized = _normalize_name_for_mapping(nakshatra_name)
    if not normalized:
        raise ValueError("nakshatra_name must not be empty")

    return normalized

