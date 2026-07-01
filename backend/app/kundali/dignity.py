"""Reusable planet dignity helpers for exaltation and debilitation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import is_dataclass
from numbers import Integral
from typing import Any, Literal, TypedDict

from backend.app.constants.rashi import RASHI_COUNT, RASHI_LIST, Rashi

DignityStatus = Literal["exalted", "debilitated", "neutral"]

DIGNITY_EXALTATION_BY_PLANET: dict[str, int] = {
    "sun": 1,
    "moon": 2,
    "mars": 10,
    "mercury": 6,
    "jupiter": 4,
    "venus": 12,
    "saturn": 7,
}

DIGNITY_DEBILITATION_BY_PLANET: dict[str, int] = {
    "sun": 7,
    "moon": 8,
    "mars": 4,
    "mercury": 12,
    "jupiter": 10,
    "venus": 6,
    "saturn": 1,
}

_RASHI_NAME_TO_INDEX: dict[str, int] = {
    name.casefold(): rashi.index
    for rashi in RASHI_LIST
    for name in (rashi.english, rashi.hindi, rashi.sanskrit)
}
_RASHI_NAME_TO_INDEX["vrischika"] = 8


class PlanetDignityMetadata(TypedDict):
    """Planet dignity metadata for chart enrichment."""

    status: DignityStatus
    exaltation_rashi: str
    debilitation_rashi: str


def get_exaltation_rashi(planet: str) -> str:
    """Return the Sanskrit Rashi name where the planet is exalted."""

    return _get_rashi_name(DIGNITY_EXALTATION_BY_PLANET[_normalize_planet(planet)])


def get_debilitation_rashi(planet: str) -> str:
    """Return the Sanskrit Rashi name where the planet is debilitated."""

    return _get_rashi_name(DIGNITY_DEBILITATION_BY_PLANET[_normalize_planet(planet)])


def get_planet_dignity(
    planet: str,
    rashi: Rashi | Mapping[str, Any] | str | int,
) -> DignityStatus:
    """Return whether a planet is exalted, debilitated, or neutral in a Rashi."""

    planet_key = _normalize_planet(planet)
    rashi_index = _get_rashi_index(rashi)

    if rashi_index == DIGNITY_EXALTATION_BY_PLANET[planet_key]:
        return "exalted"

    if rashi_index == DIGNITY_DEBILITATION_BY_PLANET[planet_key]:
        return "debilitated"

    return "neutral"


def get_planet_dignity_metadata(
    planet: str,
    rashi: Rashi | Mapping[str, Any] | str | int,
) -> PlanetDignityMetadata:
    """Return dignity status plus reference exaltation/debilitation Rashis."""

    planet_key = _normalize_planet(planet)
    return {
        "status": get_planet_dignity(planet_key, rashi),
        "exaltation_rashi": get_exaltation_rashi(planet_key),
        "debilitation_rashi": get_debilitation_rashi(planet_key),
    }


def supports_planet_dignity(planet: str) -> bool:
    """Return whether the project has dignity mapping for the planet."""

    try:
        _normalize_planet(planet)
    except (TypeError, ValueError):
        return False
    return True


def _normalize_planet(planet: str) -> str:
    """Return the normalized project planet key."""

    if not isinstance(planet, str):
        raise TypeError("planet must be a string")

    planet_key = planet.strip().casefold()
    if planet_key not in DIGNITY_EXALTATION_BY_PLANET:
        raise ValueError(f"Unsupported planet dignity mapping: {planet}")

    return planet_key


def _get_rashi_index(rashi: Rashi | Mapping[str, Any] | str | int) -> int:
    """Return a one-based Rashi index from common Rashi representations."""

    if isinstance(rashi, bool):
        raise TypeError("rashi index must be an integer")

    if isinstance(rashi, Integral):
        index = int(rashi)
        if not 1 <= index <= RASHI_COUNT:
            raise ValueError(f"rashi index must be between 1 and {RASHI_COUNT}")
        return index

    if isinstance(rashi, str):
        return _get_rashi_index_by_name(rashi)

    if isinstance(rashi, Rashi):
        return rashi.index

    if is_dataclass(rashi) and hasattr(rashi, "index"):
        index = getattr(rashi, "index")
        if isinstance(index, Integral) and not isinstance(index, bool):
            return _get_rashi_index(index)

    if isinstance(rashi, Mapping):
        index = rashi.get("index")
        if isinstance(index, Integral) and not isinstance(index, bool):
            return _get_rashi_index(index)

        for key in ("sanskrit", "english", "hindi", "name"):
            name = rashi.get(key)
            if isinstance(name, str):
                return _get_rashi_index_by_name(name)

        raise ValueError("rashi mapping must include index or name metadata")

    raise TypeError("rashi must be a Rashi, mapping, string, or integer")


def _get_rashi_index_by_name(name: str) -> int:
    """Return a one-based Rashi index from a Rashi name."""

    normalized_name = name.strip().casefold()
    try:
        return _RASHI_NAME_TO_INDEX[normalized_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported rashi: {name}") from exc


def _get_rashi_name(rashi_index: int) -> str:
    """Return the existing Sanskrit/transliteration name for a Rashi index."""

    return RASHI_LIST[_get_rashi_index(rashi_index) - 1].sanskrit
