"""Reusable Graha lordship helpers for Rashi metadata."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import is_dataclass
from numbers import Integral
from typing import Any

from backend.app.constants.rashi import RASHI_COUNT, RASHI_LIST, Rashi

RASHI_LORDS_BY_INDEX: tuple[str, ...] = tuple(rashi.lord for rashi in RASHI_LIST)

_RASHI_NAME_TO_LORD: dict[str, str] = {
    name.casefold(): rashi.lord
    for rashi in RASHI_LIST
    for name in (rashi.english, rashi.hindi, rashi.sanskrit)
}
_RASHI_NAME_TO_LORD["vrischika"] = "Mars"


def get_rashi_lord(rashi: Rashi | Mapping[str, Any] | str) -> str:
    """Return the lord for a Rashi object, Rashi-like mapping, or Rashi name."""

    if isinstance(rashi, str):
        return _get_rashi_lord_by_name(rashi)

    if isinstance(rashi, Rashi):
        return rashi.lord

    if is_dataclass(rashi) and hasattr(rashi, "lord"):
        lord = getattr(rashi, "lord")
        if isinstance(lord, str):
            return lord

    if isinstance(rashi, Mapping):
        lord = rashi.get("lord")
        if isinstance(lord, str):
            return lord

        index = rashi.get("index")
        if isinstance(index, Integral) and not isinstance(index, bool):
            return get_rashi_lord_by_index(int(index))

        for key in ("sanskrit", "english", "hindi", "name"):
            name = rashi.get(key)
            if isinstance(name, str):
                return _get_rashi_lord_by_name(name)

        raise ValueError("rashi mapping must include lord, index, or name metadata")

    raise TypeError("rashi must be a Rashi, mapping, or string")


def get_rashi_lord_by_index(rashi_index: int) -> str:
    """Return the lord for a one-based Rashi index."""

    if isinstance(rashi_index, bool) or not isinstance(rashi_index, Integral):
        raise TypeError("rashi_index must be an integer")

    index = int(rashi_index)
    if not 1 <= index <= RASHI_COUNT:
        raise ValueError(f"rashi_index must be between 1 and {RASHI_COUNT}")

    return RASHI_LORDS_BY_INDEX[index - 1]


def attach_rashi_lord(data: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of Rashi-like data with lord metadata attached.

    If the supplied mapping has a nested ``rashi`` mapping, the lord is attached
    inside that nested mapping. Otherwise, the supplied mapping itself is treated
    as Rashi metadata and receives a ``lord`` field.
    """

    if not isinstance(data, Mapping):
        raise TypeError("data must be a mapping")

    result = dict(data)
    nested_rashi = result.get("rashi")
    if isinstance(nested_rashi, Mapping):
        enriched_rashi = dict(nested_rashi)
        enriched_rashi["lord"] = get_rashi_lord(enriched_rashi)
        result["rashi"] = enriched_rashi
        return result

    result["lord"] = get_rashi_lord(result)
    return result


def _get_rashi_lord_by_name(name: str) -> str:
    """Return the lord for a Rashi name."""

    normalized_name = name.strip().casefold()
    try:
        return _RASHI_NAME_TO_LORD[normalized_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported rashi: {name}") from exc
