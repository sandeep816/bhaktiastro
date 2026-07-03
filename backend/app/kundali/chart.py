"""Basic Kundali chart assembly helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional, TypedDict, cast

from backend.app.astronomy import (
    ayanamsa,
    julian,
    planet_positions,
    retrograde as retrograde_motion,
)
from backend.app.kundali import (
    bhava,
    combustion,
    dignity,
    drishti,
    graha_lordship,
    lagna,
    mooltrikona,
    placement,
    rashi as rashi_engine,
    varga,
)
from backend.app.strength.summary import PlanetStrengthSummary
from backend.app.strength.summary import build_planet_strength_summary

DEGREE_PRECISION = 6
SUPPORTED_VARGA_NUMBERS = (
    varga.HORA_NUMBER,
    varga.DREKKANA_NUMBER,
    varga.SAPTAMSA_NUMBER,
    varga.NAVAMSA_NUMBER,
    varga.DASAMSA_NUMBER,
    varga.DWADASHAMSA_NUMBER,
    varga.SHODASAMSA_NUMBER,
    varga.VIMSHAMSA_NUMBER,
    varga.SIDDHAMSA_NUMBER,
    varga.BHAMSA_NUMBER,
    varga.TRIMSAMSA_NUMBER,
    varga.KHAVEDAMSA_NUMBER,
    varga.AKSHAVEDAMSA_NUMBER,
    varga.SHASTIAMSA_NUMBER,
)


class HousePlaceholder(TypedDict, total=False):
    """Placeholder whole-sign-style house metadata."""

    house_number: int
    house_index: int
    start_degree: float
    end_degree: float
    house_degree: float
    planets: list["PlanetChartPosition"]


class PlanetChartPosition(planet_positions.PlanetPosition, total=False):
    """Planet position enriched with internal Rashi metadata."""

    rashi: rashi_engine.RashiResult
    rashi_degree: float
    house_number: int
    house_index: int
    dignity: dignity.PlanetDignityMetadata
    mooltrikona: mooltrikona.PlanetMooltrikonaMetadata
    is_retrograde: bool
    motion_status: retrograde_motion.MotionStatus
    combustion: combustion.PlanetCombustionMetadata
    aspects: drishti.PlanetAspects


class KundaliChart(TypedDict, total=False):
    """Basic internal Kundali chart structure."""

    lagna: lagna.LagnaResult
    planets: list[PlanetChartPosition]
    houses: list[HousePlaceholder]
    vargas: dict[str, varga.VargaChart]
    strength: PlanetStrengthSummary


def assemble_kundali_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_offset: float,
    latitude: float,
    longitude: float,
    ayanamsa_mode: Optional[str] = None,
    include_vargas: bool = False,
    include_strength: bool = False,
) -> KundaliChart:
    """Assemble a basic internal Kundali chart.

    This foundation chart contains Lagna, sidereal planet positions enriched
    with Rashi metadata, and 12 placeholder houses. It deliberately avoids
    predictions, advanced house systems, and public API integration. Varga
    charts and strength summaries remain optional internal metadata until the
    public schema supports them.
    """

    julian_day = julian.calculate_julian_day(
        year,
        month,
        day,
        hour,
        minute,
        second,
        timezone_offset,
    )
    ayanamsa_value = ayanamsa.get_ayanamsa(
        julian_day.julian_day_ut,
        ayanamsa_mode,
    )
    planet_data = planet_positions.get_planet_positions(
        julian_day.julian_day_ut,
        ayanamsa_value,
    )

    lagna_result = lagna.calculate_lagna(
        year,
        month,
        day,
        hour,
        minute,
        second,
        timezone_offset,
        latitude,
        longitude,
        ayanamsa_mode,
    )
    lagna_result = cast(
        lagna.LagnaResult,
        graha_lordship.attach_rashi_lord(lagna_result),
    )
    sun_sidereal_longitude = _get_sun_sidereal_longitude(planet_data)
    planets = [
        _enrich_planet_with_rashi(
            position,
            lagna_result["rashi_index"],
            sun_sidereal_longitude,
        )
        for position in planet_data
    ]

    chart_data: KundaliChart = {
        "lagna": lagna_result,
        "planets": planets,
        "houses": _build_placeholder_houses(planets),
    }
    if include_vargas:
        chart_data["vargas"] = assemble_varga_charts(chart_data)
    if include_strength:
        chart_data["strength"] = build_planet_strength_summary(chart_data)

    return chart_data


def assemble_varga_charts(
    chart_data: Mapping[str, object],
) -> dict[str, varga.VargaChart]:
    """Build supported Varga charts from assembled Kundali chart data."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    varga_charts: dict[str, varga.VargaChart] = {}
    for varga_number in SUPPORTED_VARGA_NUMBERS:
        definition = varga.get_varga_definition(varga_number)
        if not definition.is_implemented:
            continue
        varga_charts[definition.code] = varga.build_varga_chart(
            chart_data,
            definition.number,
        )

    return varga_charts


def _enrich_planet_with_rashi(
    position: planet_positions.PlanetPosition,
    lagna_rashi_index: int,
    sun_sidereal_longitude: float | None = None,
) -> PlanetChartPosition:
    """Copy a planet position and attach internal Rashi and house metadata."""

    try:
        sidereal_longitude = float(position["sidereal_longitude"])
    except KeyError as exc:
        raise RuntimeError("Planet position is missing sidereal_longitude") from exc

    house_placement = placement.get_planet_house_placement(
        lagna_rashi_index,
        sidereal_longitude,
    )
    enriched_position: PlanetChartPosition = {
        **position,
        "rashi": cast(
            rashi_engine.RashiResult,
            graha_lordship.attach_rashi_lord(house_placement["rashi"]),
        ),
        "rashi_degree": house_placement["rashi_degree"],
        "house_number": house_placement["house_number"],
        "house_index": house_placement["house_index"],
    }
    planet = position.get("planet")
    if isinstance(planet, str) and dignity.supports_planet_dignity(planet):
        enriched_position["dignity"] = dignity.get_planet_dignity_metadata(
            planet,
            house_placement["rashi"],
        )
    if isinstance(planet, str) and mooltrikona.supports_mooltrikona(planet):
        enriched_position = cast(
            PlanetChartPosition,
            mooltrikona.attach_mooltrikona_status(enriched_position),
        )
    if isinstance(planet, str) and _supports_speed_motion_metadata(planet, position):
        speed = float(position["speed"])
        enriched_position["is_retrograde"] = retrograde_motion.is_retrograde(speed)
        enriched_position["motion_status"] = retrograde_motion.get_motion_status(speed)
    if (
        isinstance(planet, str)
        and sun_sidereal_longitude is not None
        and combustion.supports_combustion(planet)
    ):
        enriched_position["combustion"] = combustion.get_combustion_metadata(
            planet,
            sidereal_longitude,
            sun_sidereal_longitude,
        )
    if isinstance(planet, str) and drishti.supports_drishti(planet):
        enriched_position["aspects"] = drishti.get_planet_aspects(enriched_position)

    return enriched_position


def _get_sun_sidereal_longitude(
    positions: list[planet_positions.PlanetPosition],
) -> float | None:
    """Return Sun sidereal longitude when it is available in planet positions."""

    for position in positions:
        if position.get("planet") != "sun":
            continue
        try:
            return float(position["sidereal_longitude"])
        except KeyError:
            return None

    return None


def _supports_speed_motion_metadata(
    planet: str,
    position: planet_positions.PlanetPosition,
) -> bool:
    """Return whether speed-based motion metadata is safe for this planet."""

    return planet in {
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    } and "speed" in position


def _build_placeholder_houses(
    planets: list[PlanetChartPosition] | None = None,
) -> list[HousePlaceholder]:
    """Build 12 generic 30-degree placeholder houses."""

    planets_by_house: dict[int, list[PlanetChartPosition]] = {
        house_number: [] for house_number in bhava.HOUSE_NUMBERS
    }
    for planet in planets or []:
        house_number = planet.get("house_number")
        if house_number in planets_by_house:
            planets_by_house[house_number].append(planet)

    houses: list[HousePlaceholder] = []
    for house_number in bhava.HOUSE_NUMBERS:
        start_degree = (house_number - 1) * bhava.HOUSE_SPAN_DEGREES
        end_degree = house_number * bhava.HOUSE_SPAN_DEGREES
        houses.append(
            {
                "house_number": bhava.get_house_number_from_degree(start_degree),
                "house_index": bhava.get_house_index_from_degree(start_degree),
                "start_degree": round(start_degree, DEGREE_PRECISION),
                "end_degree": round(end_degree, DEGREE_PRECISION),
                "house_degree": bhava.get_house_degree(start_degree),
                "planets": planets_by_house[house_number],
            }
        )

    return houses
