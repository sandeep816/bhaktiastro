"""Arudha Lagna foundation helper."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any, TypedDict

from backend.app.kundali import bhava, graha_lordship, rashi as rashi_engine

ARUDHA_LAGNA_NAME = "arudha_lagna"
ARUDHA_FORMULA_STATUS = "foundation"
ARUDHA_EXCEPTION_HOUSES = frozenset({1, 7})
ARUDHA_EXCEPTION_OFFSET = 9


class ArudhaCalculationStep(TypedDict):
    """JSON-safe Arudha Lagna calculation step."""

    step: str
    value: int | str | bool | None
    reason: str


class ArudhaLagnaResult(TypedDict):
    """JSON-safe Arudha Lagna foundation result."""

    arudha_lagna: int | None
    arudha_rashi: rashi_engine.RashiResult | None
    lagna_rashi: rashi_engine.RashiResult | None
    lagna_lord: str | None
    lagna_lord_house: int | None
    calculation_steps: list[ArudhaCalculationStep]
    metadata: dict[str, object]


def calculate_arudha_lagna(chart_data: dict[str, Any]) -> ArudhaLagnaResult:
    """Calculate foundation-level Arudha Lagna from Kundali chart metadata."""

    if not isinstance(chart_data, Mapping):
        return _create_missing_result(
            missing_fields=["chart_data"],
            reason="Chart data must be a mapping.",
        )

    lagna_rashi = _get_lagna_rashi(chart_data)
    if lagna_rashi is None:
        return _create_missing_result(
            missing_fields=["lagna_rashi"],
            reason="Lagna Rashi metadata is missing.",
        )

    lagna_lord = _get_lagna_lord(lagna_rashi)
    if lagna_lord is None:
        return _create_missing_result(
            lagna_rashi=lagna_rashi,
            missing_fields=["lagna_lord"],
            reason="Lagna lord metadata is missing.",
        )

    lagna_lord_house = _get_planet_house(chart_data, lagna_lord)
    if lagna_lord_house is None:
        return _create_missing_result(
            lagna_rashi=lagna_rashi,
            lagna_lord=lagna_lord,
            missing_fields=["lagna_lord_house"],
            reason="Lagna lord house placement is missing.",
        )

    initial_arudha_house = bhava.normalize_house_number(
        lagna_lord_house + lagna_lord_house - 1
    )
    exception_applied = initial_arudha_house in ARUDHA_EXCEPTION_HOUSES
    arudha_house = (
        bhava.normalize_house_number(initial_arudha_house + ARUDHA_EXCEPTION_OFFSET)
        if exception_applied
        else initial_arudha_house
    )
    arudha_rashi = _get_rashi_from_lagna_offset(lagna_rashi["index"], arudha_house)

    return {
        "arudha_lagna": arudha_house,
        "arudha_rashi": arudha_rashi,
        "lagna_rashi": lagna_rashi,
        "lagna_lord": lagna_lord,
        "lagna_lord_house": lagna_lord_house,
        "calculation_steps": [
            {
                "step": "lagna_rashi",
                "value": lagna_rashi["index"],
                "reason": "Lagna Rashi index was read from chart metadata.",
            },
            {
                "step": "lagna_lord",
                "value": lagna_lord,
                "reason": "Lagna lord was derived from Lagna Rashi metadata.",
            },
            {
                "step": "lagna_lord_house",
                "value": lagna_lord_house,
                "reason": "Lagna lord house was read from planet placement metadata.",
            },
            {
                "step": "initial_arudha_lagna",
                "value": initial_arudha_house,
                "reason": "Same distance was counted from the Lagna lord house.",
            },
            {
                "step": "exception_applied",
                "value": exception_applied,
                "reason": (
                    "Arudha in Lagna or seventh from Lagna moves to tenth from "
                    "that position."
                ),
            },
            {
                "step": "final_arudha_lagna",
                "value": arudha_house,
                "reason": "Final Arudha Lagna house after foundation rules.",
            },
        ],
        "metadata": {
            "calculation_status": "calculated",
            "formula_status": ARUDHA_FORMULA_STATUS,
            "component": ARUDHA_LAGNA_NAME,
            "exception_applied": exception_applied,
            "missing_fields": [],
        },
    }


def _create_missing_result(
    *,
    missing_fields: list[str],
    reason: str,
    lagna_rashi: rashi_engine.RashiResult | None = None,
    lagna_lord: str | None = None,
    lagna_lord_house: int | None = None,
) -> ArudhaLagnaResult:
    """Create a JSON-safe result when required metadata is unavailable."""

    return {
        "arudha_lagna": None,
        "arudha_rashi": None,
        "lagna_rashi": lagna_rashi,
        "lagna_lord": lagna_lord,
        "lagna_lord_house": lagna_lord_house,
        "calculation_steps": [
            {
                "step": "missing_data",
                "value": ",".join(missing_fields),
                "reason": reason,
            }
        ],
        "metadata": {
            "calculation_status": "missing_data",
            "formula_status": ARUDHA_FORMULA_STATUS,
            "component": ARUDHA_LAGNA_NAME,
            "exception_applied": False,
            "missing_fields": list(missing_fields),
        },
    }


def _get_lagna_rashi(chart_data: Mapping[str, Any]) -> rashi_engine.RashiResult | None:
    """Return Lagna Rashi metadata from Kundali-style chart data."""

    lagna = chart_data.get("lagna")
    if not isinstance(lagna, Mapping):
        return None

    nested_rashi = lagna.get("rashi")
    if isinstance(nested_rashi, Mapping):
        rashi_index = _get_rashi_index(nested_rashi)
        if rashi_index is not None:
            return _get_rashi_from_index(rashi_index)

    rashi_index = _get_rashi_index(lagna)
    if rashi_index is not None:
        return _get_rashi_from_index(rashi_index)

    return None


def _get_lagna_lord(lagna_rashi: Mapping[str, Any]) -> str | None:
    """Return normalized Lagna lord from Rashi metadata."""

    try:
        return graha_lordship.get_rashi_lord(lagna_rashi).strip().casefold()
    except (TypeError, ValueError):
        return None


def _get_planet_house(chart_data: Mapping[str, Any], planet: str) -> int | None:
    """Return normalized house placement for a planet from chart data."""

    planets = chart_data.get("planets")
    if not isinstance(planets, list):
        return None

    planet_key = planet.strip().casefold()
    for planet_data in planets:
        if not isinstance(planet_data, Mapping):
            continue

        planet_name = planet_data.get("planet")
        if not isinstance(planet_name, str):
            continue
        if planet_name.strip().casefold() != planet_key:
            continue

        return _get_house_number(planet_data)

    return None


def _get_house_number(data: Mapping[str, Any]) -> int | None:
    """Return normalized one-based house number from mapping metadata."""

    house_number = data.get("house_number")
    if isinstance(house_number, bool) or not isinstance(house_number, Integral):
        return None

    return bhava.normalize_house_number(int(house_number))


def _get_rashi_index(data: Mapping[str, Any]) -> int | None:
    """Return a normalized one-based Rashi index from metadata."""

    rashi_index = data.get("rashi_index", data.get("index"))
    if isinstance(rashi_index, bool) or not isinstance(rashi_index, Integral):
        return None

    try:
        return bhava.normalize_house_number(int(rashi_index))
    except TypeError:
        return None


def _get_rashi_from_lagna_offset(
    lagna_rashi_index: int,
    house_number: int,
) -> rashi_engine.RashiResult:
    """Return Rashi metadata for a house counted from Lagna Rashi."""

    rashi_index = bhava.normalize_house_number(lagna_rashi_index + house_number - 1)
    return _get_rashi_from_index(rashi_index)


def _get_rashi_from_index(rashi_index: int) -> rashi_engine.RashiResult:
    """Return Rashi metadata for a one-based Rashi index."""

    normalized_index = bhava.normalize_house_number(rashi_index)
    return rashi_engine.get_rashi((normalized_index - 1) * bhava.HOUSE_SPAN_DEGREES)
