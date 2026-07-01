"""Reusable Mooltrikona helpers for supported planets."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import is_dataclass
from numbers import Integral
from typing import Any, TypedDict

from backend.app.constants.rashi import RASHI_COUNT, RASHI_LIST, Rashi

MOOLTRIKONA_BY_PLANET: dict[str, int] = {
    "sun": 5,
    "moon": 2,
    "mars": 1,
    "mercury": 6,
    "jupiter": 9,
    "venus": 7,
    "saturn": 11,
}

_RASHI_NAME_TO_INDEX: dict[str, int] = {
    name.casefold(): rashi.index
    for rashi in RASHI_LIST
    for name in (rashi.english, rashi.hindi, rashi.sanskrit)
}
_RASHI_NAME_TO_INDEX["vrischika"] = 8


class PlanetMooltrikonaMetadata(TypedDict):
    """Mooltrikona metadata for chart enrichment."""

    rashi: str
    is_mooltrikona: bool


def get_mooltrikona_rashi(planet: str) -> str:
    """Return the Sanskrit Rashi name for a planet's Mooltrikona sign."""

    return _get_rashi_name(MOOLTRIKONA_BY_PLANET[_normalize_planet(planet)])


def is_mooltrikona(
    planet: str,
    rashi: Rashi | Mapping[str, Any] | str | int,
) -> bool:
    """Return whether the supplied Rashi is the planet's Mooltrikona sign."""

    planet_key = _normalize_planet(planet)
    return _get_rashi_index(rashi) == MOOLTRIKONA_BY_PLANET[planet_key]


def attach_mooltrikona_status(data: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of planet data with Mooltrikona metadata attached."""

    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping")

    result = dict(data)
    planet = result.get("planet")
    if not isinstance(planet, str):
        raise ValueError("data must include a planet key")

    rashi = result.get("rashi")
    if rashi is None:
        raise ValueError("data must include rashi metadata")

    result["mooltrikona"] = {
        "rashi": get_mooltrikona_rashi(planet),
        "is_mooltrikona": is_mooltrikona(planet, rashi),
    }
    return result


def supports_mooltrikona(planet: str) -> bool:
    """Return whether the project has Mooltrikona mapping for the planet."""

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
    if planet_key not in MOOLTRIKONA_BY_PLANET:
        raise ValueError(f"Unsupported planet Mooltrikona mapping: {planet}")

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
