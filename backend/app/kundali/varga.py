"""Reusable divisional chart (Varga) foundations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Any, Callable, Optional, Tuple, TypedDict, cast

from backend.app.constants.rashi import RASHI_COUNT, RASHI_SPAN_DEGREES
from backend.app.kundali import rashi as rashi_engine

DEGREE_PRECISION = 6
BHAMSA_NUMBER = 27
BHAMSA_DUAL_START_RASHI_INDEX = 9
BHAMSA_FIXED_START_RASHI_INDEX = 5
BHAMSA_MOVABLE_START_RASHI_INDEX = 1
DASAMSA_NUMBER = 10
DASAMSA_SPAN_DEGREES = 3.0
DIVISION_BOUNDARY_EPSILON = 0.000001
DWADASHAMSA_NUMBER = 12
DWADASHAMSA_SPAN_DEGREES = 2.5
DREKKANA_NUMBER = 3
DREKKANA_SPAN_DEGREES = 10.0
HORA_NUMBER = 2
HORA_SPLIT_DEGREES = 15.0
HORA_SUN_RASHI_INDEX = 5
HORA_MOON_RASHI_INDEX = 4
KHAVEDAMSA_NUMBER = 40
KHAVEDAMSA_EVEN_START_RASHI_INDEX = 7
KHAVEDAMSA_ODD_START_RASHI_INDEX = 1
NAVAMSA_NUMBER = 9
SAPTAMSA_NUMBER = 7
SHODASAMSA_NUMBER = 16
SHODASAMSA_DUAL_START_RASHI_INDEX = 9
SHODASAMSA_FIXED_START_RASHI_INDEX = 5
SHODASAMSA_MOVABLE_START_RASHI_INDEX = 1
SIDDHAMSA_NUMBER = 24
SIDDHAMSA_EVEN_START_RASHI_INDEX = 4
SIDDHAMSA_ODD_START_RASHI_INDEX = 5
SUPPORTED_PLACEHOLDER_VARGAS = (45, 60)
TRIMSAMSA_NUMBER = 30
VIMSHAMSA_NUMBER = 20
VIMSHAMSA_DUAL_START_RASHI_INDEX = 5
VIMSHAMSA_FIXED_START_RASHI_INDEX = 9
VIMSHAMSA_MOVABLE_START_RASHI_INDEX = 1

TrimsamsaSegment = Tuple[float, str, int]
TRIMSAMSA_ODD_SEGMENTS: tuple[TrimsamsaSegment, ...] = (
    (5.0, "Mars", 1),
    (10.0, "Saturn", 11),
    (18.0, "Jupiter", 9),
    (25.0, "Mercury", 3),
    (RASHI_SPAN_DEGREES, "Venus", 7),
)
TRIMSAMSA_EVEN_SEGMENTS: tuple[TrimsamsaSegment, ...] = (
    (5.0, "Venus", 2),
    (12.0, "Mercury", 6),
    (20.0, "Jupiter", 12),
    (25.0, "Saturn", 10),
    (RASHI_SPAN_DEGREES, "Mars", 8),
)


class VargaPosition(TypedDict):
    """Calculated Varga placement for one longitude."""

    varga_number: int
    varga_code: str
    varga_name: str
    source_longitude: float
    division_index: int
    varga_longitude: float
    rashi_index: int
    rashi_degree: float
    rashi: rashi_engine.RashiResult


class VargaPlanetPosition(TypedDict):
    """Planet placement in a Varga chart."""

    planet: str
    source_longitude: float
    varga_position: VargaPosition


class VargaChart(TypedDict, total=False):
    """Generic Varga chart structure."""

    varga_number: int
    varga_code: str
    varga_name: str
    lagna: VargaPosition
    planets: list[VargaPlanetPosition]


VargaCalculator = Callable[[float, "VargaDefinition"], VargaPosition]


@dataclass(frozen=True)
class VargaDefinition:
    """Registered Varga definition."""

    number: int
    code: str
    name: str
    is_implemented: bool = False
    calculator: Optional[VargaCalculator] = None


_VARGA_DEFINITIONS: dict[int, VargaDefinition] = {}


def normalize_varga_number(varga_number: int | str) -> int:
    """Normalize a Varga number or code to a registered integer number."""

    if isinstance(varga_number, bool):
        raise TypeError("varga_number must be an integer or D-code string")

    if isinstance(varga_number, Integral):
        normalized = int(varga_number)
    elif isinstance(varga_number, str):
        normalized = _normalize_varga_code(varga_number)
    else:
        raise TypeError("varga_number must be an integer or D-code string")

    if normalized not in _VARGA_DEFINITIONS:
        supported = ", ".join(f"D{number}" for number in get_registered_vargas())
        raise ValueError(
            f"Unsupported Varga number: D{normalized}. Supported: {supported}"
        )

    return normalized


def calculate_varga_position(
    varga_number: int | str,
    sidereal_longitude: float,
) -> VargaPosition:
    """Calculate one Varga placement from a sidereal longitude."""

    definition = get_varga_definition(varga_number)
    if not definition.is_implemented or definition.calculator is None:
        raise NotImplementedError(
            f"{definition.code} is registered but not implemented"
        )

    return definition.calculator(sidereal_longitude, definition)


def calculate_navamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D9 Navamsa placement from longitude or planet-shaped data."""

    return calculate_varga_position(
        NAVAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_hora_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D2 Hora placement from longitude or planet-shaped data."""

    return calculate_varga_position(
        HORA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_drekkana_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D3 Drekkana placement from longitude or planet-shaped data."""

    return calculate_varga_position(
        DREKKANA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_saptamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D7 Saptamsa placement from longitude or planet-shaped data."""

    return calculate_varga_position(
        SAPTAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_dasamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D10 Dasamsa placement from longitude or planet-shaped data."""

    return calculate_varga_position(
        DASAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_dwadashamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D12 Dwadashamsa placement from longitude or planet data."""

    return calculate_varga_position(
        DWADASHAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_shodasamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D16 Shodasamsa placement from longitude or planet data."""

    return calculate_varga_position(
        SHODASAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_vimshamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D20 Vimshamsa placement from longitude or planet data."""

    return calculate_varga_position(
        VIMSHAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_siddhamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D24 Siddhamsa placement from longitude or planet data."""

    return calculate_varga_position(
        SIDDHAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_bhamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D27 Bhamsa placement from longitude or planet data."""

    return calculate_varga_position(
        BHAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_trimsamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D30 Trimsamsa placement from longitude or planet data."""

    return calculate_varga_position(
        TRIMSAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def calculate_khavedamsa_position(
    planet_data_or_longitude: Mapping[str, Any] | float,
) -> VargaPosition:
    """Calculate D40 Khavedamsa placement from longitude or planet data."""

    return calculate_varga_position(
        KHAVEDAMSA_NUMBER,
        _get_sidereal_longitude(planet_data_or_longitude),
    )


def build_varga_chart(
    chart_data: Mapping[str, Any],
    varga_number: int | str,
) -> VargaChart:
    """Build a generic Varga chart from existing Kundali chart data."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    definition = get_varga_definition(varga_number)
    result: VargaChart = {
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "planets": [],
    }

    lagna = chart_data.get("lagna")
    if isinstance(lagna, Mapping) and "sidereal_longitude" in lagna:
        result["lagna"] = calculate_varga_position(
            definition.number,
            float(lagna["sidereal_longitude"]),
        )

    planets = chart_data.get("planets")
    if isinstance(planets, list):
        result["planets"] = [
            _build_varga_planet(planet, definition.number)
            for planet in planets
            if isinstance(planet, Mapping)
        ]

    return result


def register_varga(definition: VargaDefinition) -> None:
    """Register a Varga definition for future chart support."""

    if not isinstance(definition, VargaDefinition):
        raise TypeError("definition must be a VargaDefinition")

    if definition.number < 1:
        raise ValueError("Varga number must be positive")

    _VARGA_DEFINITIONS[definition.number] = definition


def get_varga_definition(varga_number: int | str) -> VargaDefinition:
    """Return a registered Varga definition."""

    return _VARGA_DEFINITIONS[normalize_varga_number(varga_number)]


def get_registered_vargas() -> tuple[int, ...]:
    """Return registered Varga numbers."""

    return tuple(sorted(_VARGA_DEFINITIONS))


def _calculate_khavedamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D40 Khavedamsa using odd/even sign start rules."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    khavedamsa_part = min(
        int((source_degree + DIVISION_BOUNDARY_EPSILON) // division_span) + 1,
        definition.number,
    )
    start_rashi_index = (
        KHAVEDAMSA_ODD_START_RASHI_INDEX
        if source_rashi_index % 2 == 1
        else KHAVEDAMSA_EVEN_START_RASHI_INDEX
    )
    khavedamsa_rashi_index = _wrap_rashi_index(
        start_rashi_index + khavedamsa_part - 1
    )
    khavedamsa_longitude = (khavedamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    khavedamsa_rashi = rashi_engine.get_rashi(khavedamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": khavedamsa_part,
        "khavedamsa_part": khavedamsa_part,
        "varga_longitude": khavedamsa_longitude,
        "rashi_index": khavedamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": khavedamsa_rashi,
        "khavedamsa_rashi": khavedamsa_rashi,
    }


def _calculate_trimsamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D30 Trimsamsa using Parashari odd/even segments."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    segments = (
        TRIMSAMSA_ODD_SEGMENTS
        if source_rashi_index % 2 == 1
        else TRIMSAMSA_EVEN_SEGMENTS
    )
    trimsamsa_part, trimsamsa_lord, trimsamsa_rashi_index = (
        _get_trimsamsa_segment(source_degree, segments)
    )
    trimsamsa_longitude = (trimsamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    trimsamsa_rashi = rashi_engine.get_rashi(trimsamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": trimsamsa_part,
        "trimsamsa_lord": trimsamsa_lord,
        "varga_longitude": trimsamsa_longitude,
        "rashi_index": trimsamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": trimsamsa_rashi,
        "trimsamsa_rashi": trimsamsa_rashi,
    }


def _calculate_bhamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D27 Bhamsa using modality-based start Rashis."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    bhamsa_part = min(
        int((source_degree + DIVISION_BOUNDARY_EPSILON) // division_span) + 1,
        definition.number,
    )
    start_rashi_index = _get_bhamsa_start_rashi_index(source_rashi)
    bhamsa_rashi_index = _wrap_rashi_index(start_rashi_index + bhamsa_part - 1)
    bhamsa_longitude = (bhamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    bhamsa_rashi = rashi_engine.get_rashi(bhamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": bhamsa_part,
        "bhamsa_part": bhamsa_part,
        "varga_longitude": bhamsa_longitude,
        "rashi_index": bhamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": bhamsa_rashi,
        "bhamsa_rashi": bhamsa_rashi,
    }


def _calculate_siddhamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D24 Siddhamsa using odd/even sign start rules."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    siddhamsa_part = min(
        int((source_degree + DIVISION_BOUNDARY_EPSILON) // division_span) + 1,
        definition.number,
    )
    start_rashi_index = (
        SIDDHAMSA_ODD_START_RASHI_INDEX
        if source_rashi_index % 2 == 1
        else SIDDHAMSA_EVEN_START_RASHI_INDEX
    )
    siddhamsa_rashi_index = _wrap_rashi_index(
        start_rashi_index + siddhamsa_part - 1
    )
    siddhamsa_longitude = (siddhamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    siddhamsa_rashi = rashi_engine.get_rashi(siddhamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": siddhamsa_part,
        "siddhamsa_part": siddhamsa_part,
        "varga_longitude": siddhamsa_longitude,
        "rashi_index": siddhamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": siddhamsa_rashi,
        "siddhamsa_rashi": siddhamsa_rashi,
    }


def _calculate_vimshamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D20 Vimshamsa using modality-based start Rashis."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    vimshamsa_part = min(
        int((source_degree + DIVISION_BOUNDARY_EPSILON) // division_span) + 1,
        definition.number,
    )
    start_rashi_index = _get_vimshamsa_start_rashi_index(source_rashi)
    vimshamsa_rashi_index = _wrap_rashi_index(
        start_rashi_index + vimshamsa_part - 1
    )
    vimshamsa_longitude = (vimshamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    vimshamsa_rashi = rashi_engine.get_rashi(vimshamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": vimshamsa_part,
        "vimshamsa_part": vimshamsa_part,
        "varga_longitude": vimshamsa_longitude,
        "rashi_index": vimshamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": vimshamsa_rashi,
        "vimshamsa_rashi": vimshamsa_rashi,
    }


def _calculate_shodasamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D16 Shodasamsa using modality-based start Rashis."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    shodasamsa_part = min(
        int((source_degree + DIVISION_BOUNDARY_EPSILON) // division_span) + 1,
        definition.number,
    )
    start_rashi_index = _get_shodasamsa_start_rashi_index(source_rashi)
    shodasamsa_rashi_index = _wrap_rashi_index(
        start_rashi_index + shodasamsa_part - 1
    )
    shodasamsa_longitude = (shodasamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    shodasamsa_rashi = rashi_engine.get_rashi(shodasamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": shodasamsa_part,
        "shodasamsa_part": shodasamsa_part,
        "varga_longitude": shodasamsa_longitude,
        "rashi_index": shodasamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": shodasamsa_rashi,
        "shodasamsa_rashi": shodasamsa_rashi,
    }


def _calculate_dwadashamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D12 Dwadashamsa placement counting from the source Rashi."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    dwadashamsa_part = min(
        int(source_degree // DWADASHAMSA_SPAN_DEGREES) + 1,
        definition.number,
    )
    dwadashamsa_rashi_index = _wrap_rashi_index(
        source_rashi_index + dwadashamsa_part - 1
    )
    dwadashamsa_longitude = (
        dwadashamsa_rashi_index - 1
    ) * RASHI_SPAN_DEGREES
    dwadashamsa_rashi = rashi_engine.get_rashi(dwadashamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": dwadashamsa_part,
        "dwadashamsa_part": dwadashamsa_part,
        "varga_longitude": dwadashamsa_longitude,
        "rashi_index": dwadashamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": dwadashamsa_rashi,
        "dwadashamsa_rashi": dwadashamsa_rashi,
    }


def _calculate_dasamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D10 Dasamsa placement using odd/even sign start rules."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    dasamsa_part = min(
        int(source_degree // DASAMSA_SPAN_DEGREES) + 1,
        definition.number,
    )
    start_rashi_index = (
        source_rashi_index
        if source_rashi_index % 2 == 1
        else _wrap_rashi_index(source_rashi_index + 8)
    )
    dasamsa_rashi_index = _wrap_rashi_index(start_rashi_index + dasamsa_part - 1)
    dasamsa_longitude = (dasamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    dasamsa_rashi = rashi_engine.get_rashi(dasamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": dasamsa_part,
        "dasamsa_part": dasamsa_part,
        "varga_longitude": dasamsa_longitude,
        "rashi_index": dasamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": dasamsa_rashi,
        "dasamsa_rashi": dasamsa_rashi,
    }


def _calculate_saptamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D7 Saptamsa placement using odd/even sign start rules."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    saptamsa_part = min(
        int((source_degree + DIVISION_BOUNDARY_EPSILON) // division_span) + 1,
        definition.number,
    )
    start_rashi_index = (
        source_rashi_index
        if source_rashi_index % 2 == 1
        else _wrap_rashi_index(source_rashi_index + 6)
    )
    saptamsa_rashi_index = _wrap_rashi_index(
        start_rashi_index + saptamsa_part - 1
    )
    saptamsa_longitude = (saptamsa_rashi_index - 1) * RASHI_SPAN_DEGREES
    saptamsa_rashi = rashi_engine.get_rashi(saptamsa_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": saptamsa_part,
        "saptamsa_part": saptamsa_part,
        "varga_longitude": saptamsa_longitude,
        "rashi_index": saptamsa_rashi_index,
        "rashi_degree": 0.0,
        "rashi": saptamsa_rashi,
        "saptamsa_rashi": saptamsa_rashi,
    }


def _calculate_drekkana_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D3 Drekkana placement using 1st/5th/9th Rashi rule."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    drekkana_part = min(
        int(source_degree // DREKKANA_SPAN_DEGREES) + 1,
        definition.number,
    )
    drekkana_rashi_index = _wrap_rashi_index(
        source_rashi_index + ((drekkana_part - 1) * 4)
    )
    drekkana_longitude = (drekkana_rashi_index - 1) * RASHI_SPAN_DEGREES
    drekkana_rashi = rashi_engine.get_rashi(drekkana_longitude)

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": drekkana_part,
        "drekkana_part": drekkana_part,
        "varga_longitude": drekkana_longitude,
        "rashi_index": drekkana_rashi_index,
        "rashi_degree": 0.0,
        "rashi": drekkana_rashi,
        "drekkana_rashi": drekkana_rashi,
    }


def _calculate_hora_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D2 Hora placement using the Parashari Sun/Moon rule."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi = rashi_engine.get_rashi(source_longitude)
    source_rashi_index = source_rashi["index"]
    source_degree = rashi_engine.get_rashi_degree(source_longitude)
    is_first_half = source_degree < HORA_SPLIT_DEGREES
    is_odd_rashi = source_rashi_index % 2 == 1

    if is_odd_rashi == is_first_half:
        hora_lord = "Sun"
        hora_rashi_index = HORA_SUN_RASHI_INDEX
    else:
        hora_lord = "Moon"
        hora_rashi_index = HORA_MOON_RASHI_INDEX

    hora_longitude = (hora_rashi_index - 1) * RASHI_SPAN_DEGREES
    hora_rashi = rashi_engine.get_rashi(hora_longitude)
    division_index = 1 if is_first_half else 2

    return {
        "varga": definition.code,
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "source_rashi": source_rashi,
        "source_degree": source_degree,
        "division_index": division_index,
        "varga_longitude": hora_longitude,
        "rashi_index": hora_rashi_index,
        "rashi_degree": 0.0,
        "rashi": hora_rashi,
        "hora_lord": hora_lord,
        "hora_rashi": hora_rashi,
    }


def _calculate_navamsa_position(
    sidereal_longitude: float,
    definition: VargaDefinition,
) -> VargaPosition:
    """Calculate D9 Navamsa placement from a sidereal longitude."""

    source_longitude = rashi_engine.normalize_longitude(sidereal_longitude)
    source_rashi_index = rashi_engine.get_rashi_index(source_longitude)
    degree_in_rashi = rashi_engine.get_rashi_degree(source_longitude)
    division_span = RASHI_SPAN_DEGREES / definition.number
    division_index = min(
        int(degree_in_rashi // division_span) + 1,
        definition.number,
    )
    navamsa_rashi_index = _get_navamsa_rashi_index(
        source_rashi_index,
        division_index,
    )
    rashi_degree = round(
        (degree_in_rashi - ((division_index - 1) * division_span))
        * definition.number,
        DEGREE_PRECISION,
    )
    varga_longitude = rashi_engine.normalize_longitude(
        ((navamsa_rashi_index - 1) * RASHI_SPAN_DEGREES) + rashi_degree
    )

    return {
        "varga_number": definition.number,
        "varga_code": definition.code,
        "varga_name": definition.name,
        "source_longitude": source_longitude,
        "division_index": division_index,
        "varga_longitude": varga_longitude,
        "rashi_index": navamsa_rashi_index,
        "rashi_degree": rashi_degree,
        "rashi": rashi_engine.get_rashi(varga_longitude),
    }


def _get_navamsa_rashi_index(
    source_rashi_index: int,
    division_index: int,
) -> int:
    """Return D9 Rashi index using movable/fixed/dual start rules."""

    source_offset = source_rashi_index - 1
    modality_offset = source_offset % 3
    if modality_offset == 0:
        start_rashi_index = source_rashi_index
    elif modality_offset == 1:
        start_rashi_index = _wrap_rashi_index(source_rashi_index + 8)
    else:
        start_rashi_index = _wrap_rashi_index(source_rashi_index + 4)

    return _wrap_rashi_index(start_rashi_index + division_index - 1)


def _get_shodasamsa_start_rashi_index(
    source_rashi: rashi_engine.RashiResult,
) -> int:
    """Return the D16 start Rashi index from the source Rashi modality."""

    return _get_modality_start_rashi_index(
        source_rashi,
        movable_start=SHODASAMSA_MOVABLE_START_RASHI_INDEX,
        fixed_start=SHODASAMSA_FIXED_START_RASHI_INDEX,
        dual_start=SHODASAMSA_DUAL_START_RASHI_INDEX,
    )


def _get_vimshamsa_start_rashi_index(
    source_rashi: rashi_engine.RashiResult,
) -> int:
    """Return the D20 start Rashi index from the source Rashi modality."""

    return _get_modality_start_rashi_index(
        source_rashi,
        movable_start=VIMSHAMSA_MOVABLE_START_RASHI_INDEX,
        fixed_start=VIMSHAMSA_FIXED_START_RASHI_INDEX,
        dual_start=VIMSHAMSA_DUAL_START_RASHI_INDEX,
    )


def _get_bhamsa_start_rashi_index(
    source_rashi: rashi_engine.RashiResult,
) -> int:
    """Return the D27 start Rashi index from the source Rashi modality."""

    return _get_modality_start_rashi_index(
        source_rashi,
        movable_start=BHAMSA_MOVABLE_START_RASHI_INDEX,
        fixed_start=BHAMSA_FIXED_START_RASHI_INDEX,
        dual_start=BHAMSA_DUAL_START_RASHI_INDEX,
    )


def _get_modality_start_rashi_index(
    source_rashi: rashi_engine.RashiResult,
    *,
    movable_start: int,
    fixed_start: int,
    dual_start: int,
) -> int:
    """Return a configured start Rashi index from source Rashi modality."""

    modality = source_rashi["modality"]
    if modality == "Movable":
        return movable_start
    if modality == "Fixed":
        return fixed_start
    if modality == "Dual":
        return dual_start

    raise ValueError(f"Unsupported Rashi modality: {modality}")


def _get_trimsamsa_segment(
    source_degree: float,
    segments: tuple[TrimsamsaSegment, ...],
) -> tuple[int, str, int]:
    """Return the D30 segment index, lord, and Rashi index."""

    for index, (upper_bound, lord, rashi_index) in enumerate(segments, start=1):
        if source_degree < upper_bound:
            return index, lord, rashi_index

    return len(segments), segments[-1][1], segments[-1][2]


def _build_varga_planet(
    planet_data: Mapping[str, Any],
    varga_number: int,
) -> VargaPlanetPosition:
    """Build one planet placement for a Varga chart."""

    planet_name = planet_data.get("planet")
    if not isinstance(planet_name, str):
        raise ValueError("planet data must include planet name")

    if "sidereal_longitude" not in planet_data:
        raise ValueError(f"{planet_name} is missing sidereal_longitude")

    source_longitude = float(planet_data["sidereal_longitude"])
    return {
        "planet": planet_name,
        "source_longitude": rashi_engine.normalize_longitude(source_longitude),
        "varga_position": calculate_varga_position(varga_number, source_longitude),
    }


def _get_sidereal_longitude(
    data_or_longitude: Mapping[str, Any] | float,
) -> float:
    """Return sidereal longitude from a numeric value or chart data mapping."""

    if isinstance(data_or_longitude, Mapping):
        if "sidereal_longitude" not in data_or_longitude:
            raise ValueError("data must include sidereal_longitude")
        longitude = data_or_longitude["sidereal_longitude"]
        if isinstance(longitude, bool) or not isinstance(longitude, Real):
            raise TypeError("sidereal_longitude must be a real number")
        return float(longitude)

    if isinstance(data_or_longitude, bool) or not isinstance(
        data_or_longitude,
        Real,
    ):
        raise TypeError("sidereal_longitude must be a real number")

    return float(data_or_longitude)


def _normalize_varga_code(varga_number: str) -> int:
    """Normalize D-code strings like D9 or 9."""

    normalized = varga_number.strip().upper()
    if normalized.startswith("D"):
        normalized = normalized[1:]

    if not normalized.isdigit():
        raise ValueError("varga_number string must be a D-code or integer string")

    return int(normalized)


def _wrap_rashi_index(rashi_index: int) -> int:
    """Wrap a one-based Rashi index into the 1..12 range."""

    return ((rashi_index - 1) % RASHI_COUNT) + 1


def _register_default_vargas() -> None:
    """Register supported Varga definitions."""

    register_varga(
        VargaDefinition(
            number=KHAVEDAMSA_NUMBER,
            code="D40",
            name="Khavedamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_khavedamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=TRIMSAMSA_NUMBER,
            code="D30",
            name="Trimsamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_trimsamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=BHAMSA_NUMBER,
            code="D27",
            name="Bhamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_bhamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=SIDDHAMSA_NUMBER,
            code="D24",
            name="Siddhamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_siddhamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=VIMSHAMSA_NUMBER,
            code="D20",
            name="Vimshamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_vimshamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=SHODASAMSA_NUMBER,
            code="D16",
            name="Shodasamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_shodasamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=DWADASHAMSA_NUMBER,
            code="D12",
            name="Dwadashamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_dwadashamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=DASAMSA_NUMBER,
            code="D10",
            name="Dasamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_dasamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=SAPTAMSA_NUMBER,
            code="D7",
            name="Saptamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_saptamsa_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=DREKKANA_NUMBER,
            code="D3",
            name="Drekkana",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_drekkana_position),
        )
    )

    register_varga(
        VargaDefinition(
            number=HORA_NUMBER,
            code="D2",
            name="Hora",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_hora_position),
        )
    )

    for placeholder in SUPPORTED_PLACEHOLDER_VARGAS:
        register_varga(
            VargaDefinition(
                number=placeholder,
                code=f"D{placeholder}",
                name=f"D{placeholder}",
            )
        )

    register_varga(
        VargaDefinition(
            number=NAVAMSA_NUMBER,
            code="D9",
            name="Navamsa",
            is_implemented=True,
            calculator=cast(VargaCalculator, _calculate_navamsa_position),
        )
    )


_register_default_vargas()
