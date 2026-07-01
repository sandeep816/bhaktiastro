"""Pydantic schemas for basic Kundali chart requests and responses."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.panchang import DmsInfo


class KundaliRequest(BaseModel):
    """Request schema for basic Kundali chart assembly."""

    year: int = Field(
        ...,
        ge=1900,
        le=2100,
        description="Local calendar year for MVP calculations.",
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Local calendar month from 1 to 12.",
    )
    day: int = Field(
        ...,
        ge=1,
        le=31,
        description="Local calendar day from 1 to 31.",
    )
    hour: int = Field(
        12,
        ge=0,
        le=23,
        description="Local hour from 0 to 23.",
    )
    minute: int = Field(
        0,
        ge=0,
        le=59,
        description="Local minute from 0 to 59.",
    )
    second: int = Field(
        0,
        ge=0,
        le=59,
        description="Local second from 0 to 59.",
    )
    timezone_offset: float = Field(
        5.5,
        ge=-12.0,
        le=14.0,
        description="Local UTC offset in decimal hours.",
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Geographic latitude in degrees, north positive.",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Geographic longitude in degrees, east positive.",
    )
    ayanamsa: Literal["lahiri"] = Field(
        "lahiri",
        description="Ayanamsa mode for MVP calculations.",
    )


class StrictResponseModel(BaseModel):
    """Base model for response sections with stable, explicit keys."""

    model_config = ConfigDict(extra="forbid")


class RashiInfo(StrictResponseModel):
    """Rashi metadata."""

    index: int = Field(..., description="One-based Rashi index.")
    english: str = Field(..., description="English Rashi name.")
    hindi: str = Field(..., description="Hindi Rashi name.")
    sanskrit: str = Field(..., description="Sanskrit/transliteration Rashi name.")
    lord: str = Field(..., description="Rashi lord.")
    element: str = Field(..., description="Rashi element.")
    modality: str = Field(..., description="Rashi modality.")
    start_degree: float = Field(..., description="Rashi start degree.")
    end_degree: float = Field(..., description="Rashi end degree.")
    degree_in_rashi: float = Field(
        ...,
        description="Degree completed within the Rashi.",
    )


class LagnaInfo(StrictResponseModel):
    """Lagna section of a Kundali response."""

    ascendant_longitude: float = Field(
        ...,
        description="Sidereal Ascendant longitude in degrees.",
    )
    sidereal_longitude: float = Field(
        ...,
        description="Sidereal Ascendant longitude in degrees.",
    )
    tropical_longitude: float = Field(
        ...,
        description="Tropical Ascendant longitude in degrees.",
    )
    ayanamsa: float = Field(..., description="Ayanamsa value in degrees.")
    rashi: RashiInfo = Field(..., description="Lagna Rashi metadata.")
    rashi_index: int = Field(..., description="One-based Lagna Rashi index.")
    rashi_degree: float = Field(
        ...,
        description="Degree completed within the Lagna Rashi.",
    )


class PlanetDignityInfo(StrictResponseModel):
    """Exaltation/debilitation foundation metadata for a planet."""

    status: Literal["exalted", "debilitated", "neutral"] = Field(
        ...,
        description="Planet dignity status in the current Rashi.",
    )
    exaltation_rashi: str = Field(
        ...,
        description="Sanskrit/transliteration Rashi where the planet is exalted.",
    )
    debilitation_rashi: str = Field(
        ...,
        description="Sanskrit/transliteration Rashi where the planet is debilitated.",
    )


class PlanetMooltrikonaInfo(StrictResponseModel):
    """Mooltrikona foundation metadata for a planet."""

    rashi: str = Field(
        ...,
        description="Sanskrit/transliteration Mooltrikona Rashi for the planet.",
    )
    is_mooltrikona: bool = Field(
        ...,
        description="Whether the planet is currently in its Mooltrikona Rashi.",
    )


class KundaliPlanetInfo(StrictResponseModel):
    """Planet position section of a Kundali response."""

    planet: str = Field(..., description="Planet key.")
    tropical_longitude: Optional[float] = Field(
        None,
        description="Tropical longitude in degrees, when available.",
    )
    sidereal_longitude: float = Field(
        ...,
        description="Sidereal longitude in degrees.",
    )
    rashi_index: int = Field(
        ...,
        description="Zero-based rashi index preserved from planet positions.",
    )
    rashi_name_hi: str = Field(..., description="Hindi rashi name.")
    degree_in_rashi: float = Field(..., description="Degree within the rashi.")
    dms: DmsInfo = Field(..., description="DMS position within the rashi.")
    speed: Optional[float] = Field(None, description="Planet speed, when available.")
    retrograde: bool = Field(..., description="Retrograde status.")
    rashi: RashiInfo = Field(..., description="Rashi metadata.")
    rashi_degree: float = Field(
        ...,
        description="Degree completed within the Rashi.",
    )
    house_number: Optional[int] = Field(
        None,
        description="One-based whole-sign house number, when available.",
    )
    house_index: Optional[int] = Field(
        None,
        description="Zero-based whole-sign house index, when available.",
    )
    dignity: Optional[PlanetDignityInfo] = Field(
        None,
        description="Optional planet dignity metadata, when available.",
    )
    mooltrikona: Optional[PlanetMooltrikonaInfo] = Field(
        None,
        description="Optional planet Mooltrikona metadata, when available.",
    )


class HousePlaceholderInfo(StrictResponseModel):
    """Placeholder house section of a Kundali response."""

    house_number: int = Field(..., description="One-based house number.")
    house_index: int = Field(..., description="Zero-based house index.")
    start_degree: float = Field(..., description="Placeholder house start degree.")
    end_degree: float = Field(..., description="Placeholder house end degree.")
    house_degree: float = Field(
        ...,
        description="Degree completed within the placeholder house.",
    )
    planets: list[KundaliPlanetInfo] = Field(
        default_factory=list,
        description="Planets grouped into this house, when available.",
    )


class KundaliResponse(StrictResponseModel):
    """Response schema matching basic Kundali chart assembly output."""

    lagna: LagnaInfo = Field(..., description="Lagna information.")
    planets: list[KundaliPlanetInfo] = Field(..., description="Planet positions.")
    houses: list[HousePlaceholderInfo] = Field(
        ...,
        description="Placeholder house information.",
    )
