"""Basic Kundali chart assembly helpers."""

from __future__ import annotations

from typing import Optional, TypedDict

from backend.app.astronomy import ayanamsa, julian, planet_positions
from backend.app.kundali import bhava, lagna, rashi as rashi_engine

DEGREE_PRECISION = 6


class HousePlaceholder(TypedDict):
    """Placeholder whole-sign-style house metadata."""

    house_number: int
    house_index: int
    start_degree: float
    end_degree: float
    house_degree: float


class PlanetChartPosition(planet_positions.PlanetPosition, total=False):
    """Planet position enriched with internal Rashi metadata."""

    rashi: rashi_engine.RashiResult
    rashi_degree: float


class KundaliChart(TypedDict):
    """Basic internal Kundali chart structure."""

    lagna: lagna.LagnaResult
    planets: list[PlanetChartPosition]
    houses: list[HousePlaceholder]


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
) -> KundaliChart:
    """Assemble a basic internal Kundali chart.

    This foundation chart contains Lagna, sidereal planet positions enriched
    with Rashi metadata, and 12 placeholder houses. It deliberately avoids
    predictions, divisional charts, advanced house systems, and public API
    integration.
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

    return {
        "lagna": lagna.calculate_lagna(
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
        ),
        "planets": [_enrich_planet_with_rashi(position) for position in planet_data],
        "houses": _build_placeholder_houses(),
    }


def _enrich_planet_with_rashi(
    position: planet_positions.PlanetPosition,
) -> PlanetChartPosition:
    """Copy a planet position and attach internal Rashi metadata."""

    try:
        sidereal_longitude = float(position["sidereal_longitude"])
    except KeyError as exc:
        raise RuntimeError("Planet position is missing sidereal_longitude") from exc

    rashi = rashi_engine.get_rashi(sidereal_longitude)
    enriched_position: PlanetChartPosition = {
        **position,
        "rashi": rashi,
        "rashi_degree": rashi_engine.get_rashi_degree(sidereal_longitude),
    }
    return enriched_position


def _build_placeholder_houses() -> list[HousePlaceholder]:
    """Build 12 generic 30-degree placeholder houses."""

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
            }
        )

    return houses
