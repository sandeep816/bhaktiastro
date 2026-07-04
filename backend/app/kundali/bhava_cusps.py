"""Bhava Madhya / house cusp foundation helper."""

from __future__ import annotations

from typing import TypedDict

from backend.app.kundali import bhava, rashi as rashi_engine

BHAVA_CUSP_COMPONENT = "bhava_cusps"
BHAVA_CUSP_HOUSE_SYSTEM = "equal_foundation"
BHAVA_CUSP_FORMULA_STATUS = "foundation"


class BhavaCusp(TypedDict):
    """JSON-safe equal-house cusp metadata."""

    house_number: int
    cusp_longitude: float
    rashi: rashi_engine.RashiResult
    rashi_index: int
    rashi_degree: float


class BhavaCuspResult(TypedDict):
    """JSON-safe Bhava cusp foundation result."""

    house_cusps: list[BhavaCusp]
    house_system: str
    metadata: dict[str, object]


def calculate_bhava_cusps(lagna_longitude: float) -> BhavaCuspResult:
    """Calculate foundation-level equal-house cusps from Lagna longitude."""

    try:
        normalized_lagna = rashi_engine.normalize_longitude(lagna_longitude)
    except (TypeError, ValueError):
        return _create_missing_result(
            missing_fields=["lagna_longitude"],
            reason="Lagna longitude must be a finite real number.",
        )

    house_cusps = [
        _create_house_cusp(
            house_number=house_number,
            cusp_longitude=rashi_engine.normalize_longitude(
                normalized_lagna
                + ((house_number - 1) * bhava.HOUSE_SPAN_DEGREES)
            ),
        )
        for house_number in bhava.HOUSE_NUMBERS
    ]

    return {
        "house_cusps": house_cusps,
        "house_system": BHAVA_CUSP_HOUSE_SYSTEM,
        "metadata": {
            "calculation_status": "calculated",
            "formula_status": BHAVA_CUSP_FORMULA_STATUS,
            "component": BHAVA_CUSP_COMPONENT,
            "lagna_longitude": normalized_lagna,
            "house_span_degrees": bhava.HOUSE_SPAN_DEGREES,
            "missing_fields": [],
        },
    }


def _create_house_cusp(*, house_number: int, cusp_longitude: float) -> BhavaCusp:
    """Create JSON-safe Rashi metadata for one equal-house cusp."""

    rashi = rashi_engine.get_rashi(cusp_longitude)
    return {
        "house_number": house_number,
        "cusp_longitude": cusp_longitude,
        "rashi": rashi,
        "rashi_index": rashi["index"],
        "rashi_degree": rashi_engine.get_rashi_degree(cusp_longitude),
    }


def _create_missing_result(
    *,
    missing_fields: list[str],
    reason: str,
) -> BhavaCuspResult:
    """Create a JSON-safe result when cusp inputs are unavailable."""

    return {
        "house_cusps": [],
        "house_system": BHAVA_CUSP_HOUSE_SYSTEM,
        "metadata": {
            "calculation_status": "missing_data",
            "formula_status": BHAVA_CUSP_FORMULA_STATUS,
            "component": BHAVA_CUSP_COMPONENT,
            "lagna_longitude": None,
            "house_span_degrees": bhava.HOUSE_SPAN_DEGREES,
            "missing_fields": list(missing_fields),
            "reason": reason,
        },
    }
