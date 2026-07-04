"""Upapada Lagna foundation helper."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any, TypedDict

from backend.app.kundali import bhava, graha_lordship, rashi as rashi_engine
from backend.app.kundali.arudha_lagna import (
    ARUDHA_EXCEPTION_HOUSES,
    ARUDHA_EXCEPTION_OFFSET,
    ARUDHA_FORMULA_STATUS,
)

UPAPADA_LAGNA_NAME = "upapada_lagna"
UPAPADA_SOURCE_HOUSE = 12


class UpapadaCalculationStep(TypedDict):
    """JSON-safe Upapada Lagna calculation step."""

    step: str
    value: int | str | bool | None
    reason: str


class UpapadaLagnaResult(TypedDict):
    """JSON-safe Upapada Lagna foundation result."""

    upapada_lagna: int | None
    upapada_rashi: rashi_engine.RashiResult | None
    source_house: int
    source_rashi: rashi_engine.RashiResult | None
    source_lord: str | None
    source_lord_house: int | None
    calculation_steps: list[UpapadaCalculationStep]
    metadata: dict[str, object]


def calculate_upapada_lagna(chart_data: dict[str, Any]) -> UpapadaLagnaResult:
    """Calculate foundation-level Upapada Lagna from Kundali chart metadata."""

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

    source_rashi = _get_rashi_from_lagna_offset(
        lagna_rashi["index"],
        UPAPADA_SOURCE_HOUSE,
    )
    source_lord = _get_rashi_lord(source_rashi)
    if source_lord is None:
        return _create_missing_result(
            source_rashi=source_rashi,
            missing_fields=["source_lord"],
            reason="Twelfth house lord metadata is missing.",
        )

    source_lord_house = _get_planet_house(chart_data, source_lord)
    if source_lord_house is None:
        return _create_missing_result(
            source_rashi=source_rashi,
            source_lord=source_lord,
            missing_fields=["source_lord_house"],
            reason="Twelfth lord house placement is missing.",
        )

    distance_from_source = bhava.normalize_house_number(
        source_lord_house - UPAPADA_SOURCE_HOUSE + 1
    )
    initial_upapada_house = bhava.normalize_house_number(
        source_lord_house + distance_from_source - 1
    )
    relative_to_source = bhava.normalize_house_number(
        initial_upapada_house - UPAPADA_SOURCE_HOUSE + 1
    )
    exception_applied = relative_to_source in ARUDHA_EXCEPTION_HOUSES
    upapada_house = (
        bhava.normalize_house_number(initial_upapada_house + ARUDHA_EXCEPTION_OFFSET)
        if exception_applied
        else initial_upapada_house
    )
    upapada_rashi = _get_rashi_from_lagna_offset(lagna_rashi["index"], upapada_house)

    return {
        "upapada_lagna": upapada_house,
        "upapada_rashi": upapada_rashi,
        "source_house": UPAPADA_SOURCE_HOUSE,
        "source_rashi": source_rashi,
        "source_lord": source_lord,
        "source_lord_house": source_lord_house,
        "calculation_steps": [
            {
                "step": "source_house",
                "value": UPAPADA_SOURCE_HOUSE,
                "reason": "Upapada Lagna uses the twelfth house as source.",
            },
            {
                "step": "source_rashi",
                "value": source_rashi["index"],
                "reason": "Twelfth house Rashi was counted from Lagna.",
            },
            {
                "step": "source_lord",
                "value": source_lord,
                "reason": "Twelfth house lord was derived from source Rashi.",
            },
            {
                "step": "source_lord_house",
                "value": source_lord_house,
                "reason": "Twelfth lord house was read from planet placement metadata.",
            },
            {
                "step": "distance_from_source",
                "value": distance_from_source,
                "reason": "Distance from source house to source lord placement.",
            },
            {
                "step": "initial_upapada_lagna",
                "value": initial_upapada_house,
                "reason": "Same distance was counted from the source lord house.",
            },
            {
                "step": "exception_applied",
                "value": exception_applied,
                "reason": (
                    "Arudha in source house or seventh from source moves to "
                    "tenth from that position."
                ),
            },
            {
                "step": "final_upapada_lagna",
                "value": upapada_house,
                "reason": "Final Upapada Lagna house after foundation rules.",
            },
        ],
        "metadata": {
            "calculation_status": "calculated",
            "formula_status": ARUDHA_FORMULA_STATUS,
            "component": UPAPADA_LAGNA_NAME,
            "exception_applied": exception_applied,
            "missing_fields": [],
        },
    }


def _create_missing_result(
    *,
    missing_fields: list[str],
    reason: str,
    source_rashi: rashi_engine.RashiResult | None = None,
    source_lord: str | None = None,
    source_lord_house: int | None = None,
) -> UpapadaLagnaResult:
    """Create a JSON-safe result when required metadata is unavailable."""

    return {
        "upapada_lagna": None,
        "upapada_rashi": None,
        "source_house": UPAPADA_SOURCE_HOUSE,
        "source_rashi": source_rashi,
        "source_lord": source_lord,
        "source_lord_house": source_lord_house,
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
            "component": UPAPADA_LAGNA_NAME,
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


def _get_rashi_lord(rashi: Mapping[str, Any]) -> str | None:
    """Return normalized lord from Rashi metadata."""

    try:
        return graha_lordship.get_rashi_lord(rashi).strip().casefold()
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
