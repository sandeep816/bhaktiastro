"""Pydantic schemas for basic Kundali chart requests and responses."""

from __future__ import annotations

from typing import Any, List, Literal, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

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
    include_vargas: bool = Field(
        False,
        description="Opt-in flag to include supported Varga charts.",
    )
    include_strength: bool = Field(
        False,
        description="Opt-in flag to include Planet Strength Summary.",
    )
    include_ashtakavarga: bool = Field(
        False,
        description="Opt-in flag to include Ashtakavarga Summary.",
    )
    include_special_lagnas: bool = Field(
        False,
        description="Opt-in flag to include Special Lagna Summary.",
    )
    include_predictions: bool = Field(
        False,
        description="Opt-in flag to include Prediction Framework output.",
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


class PlanetCombustionInfo(StrictResponseModel):
    """Combustion foundation metadata for a planet."""

    status: Literal["combust", "not_combust", "unsupported"] = Field(
        ...,
        description="Combustion status relative to the Sun.",
    )
    angular_distance: float = Field(
        ...,
        description="Shortest angular distance from the Sun in degrees.",
    )
    orb: float = Field(
        ...,
        description="Configured conservative combustion orb in degrees.",
    )


class PlanetAspectInfo(StrictResponseModel):
    """House-based Graha Drishti foundation metadata for a planet."""

    planet: str = Field(..., description="Planet key.")
    house_number: int = Field(..., description="Planet placement house number.")
    aspected_houses: Sequence[int] = Field(
        ...,
        description="One-based house numbers aspected by this planet.",
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
    is_retrograde: Optional[bool] = Field(
        None,
        description="Optional speed-based retrograde status, when available.",
    )
    motion_status: Optional[Literal["retrograde", "direct", "stationary"]] = Field(
        None,
        description="Optional speed-based longitudinal motion status.",
    )
    combustion: Optional[PlanetCombustionInfo] = Field(
        None,
        description="Optional combustion metadata, when available.",
    )
    aspects: Optional[PlanetAspectInfo] = Field(
        None,
        description="Optional house-based Graha Drishti metadata.",
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
    planets: List[KundaliPlanetInfo] = Field(
        default_factory=list,
        description="Planets grouped into this house, when available.",
    )


VargaCode = Literal[
    "D2",
    "D3",
    "D7",
    "D9",
    "D10",
    "D12",
    "D16",
    "D20",
    "D24",
    "D27",
    "D30",
    "D40",
    "D45",
    "D60",
]


class VargaPositionInfo(StrictResponseModel):
    """Calculated placement for one body in a Varga chart."""

    varga: Optional[VargaCode] = Field(
        MISSING,
        description="Legacy Varga code key, when emitted by a calculator.",
    )
    varga_number: int = Field(..., description="Divisional chart number.")
    varga_code: VargaCode = Field(..., description="Divisional chart code.")
    varga_name: str = Field(..., description="Divisional chart name.")
    source_longitude: float = Field(
        ...,
        description="Source sidereal longitude in the base Kundali chart.",
    )
    source_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="Source Rashi metadata, when emitted by the calculator.",
    )
    source_degree: Optional[float] = Field(
        MISSING,
        description="Source degree within the source Rashi, when available.",
    )
    division_index: int = Field(..., description="One-based Varga division index.")
    varga_longitude: float = Field(
        ...,
        description="Calculated Varga longitude in degrees.",
    )
    rashi_index: int = Field(..., description="One-based calculated Rashi index.")
    rashi_degree: float = Field(
        ...,
        description="Degree completed within the calculated Varga Rashi.",
    )
    rashi: RashiInfo = Field(..., description="Calculated Varga Rashi metadata.")
    hora_lord: Optional[str] = Field(
        MISSING,
        description="D2 Hora lord, when applicable.",
    )
    hora_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D2 Hora Rashi metadata, when applicable.",
    )
    drekkana_part: Optional[int] = Field(
        MISSING,
        description="D3 Drekkana part, when applicable.",
    )
    drekkana_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D3 Drekkana Rashi metadata, when applicable.",
    )
    saptamsa_part: Optional[int] = Field(
        MISSING,
        description="D7 Saptamsa part, when applicable.",
    )
    saptamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D7 Saptamsa Rashi metadata, when applicable.",
    )
    dasamsa_part: Optional[int] = Field(
        MISSING,
        description="D10 Dasamsa part, when applicable.",
    )
    dasamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D10 Dasamsa Rashi metadata, when applicable.",
    )
    dwadashamsa_part: Optional[int] = Field(
        MISSING,
        description="D12 Dwadashamsa part, when applicable.",
    )
    dwadashamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D12 Dwadashamsa Rashi metadata, when applicable.",
    )
    shodasamsa_part: Optional[int] = Field(
        MISSING,
        description="D16 Shodasamsa part, when applicable.",
    )
    shodasamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D16 Shodasamsa Rashi metadata, when applicable.",
    )
    vimshamsa_part: Optional[int] = Field(
        MISSING,
        description="D20 Vimshamsa part, when applicable.",
    )
    vimshamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D20 Vimshamsa Rashi metadata, when applicable.",
    )
    siddhamsa_part: Optional[int] = Field(
        MISSING,
        description="D24 Siddhamsa part, when applicable.",
    )
    siddhamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D24 Siddhamsa Rashi metadata, when applicable.",
    )
    bhamsa_part: Optional[int] = Field(
        MISSING,
        description="D27 Bhamsa part, when applicable.",
    )
    bhamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D27 Bhamsa Rashi metadata, when applicable.",
    )
    trimsamsa_lord: Optional[str] = Field(
        MISSING,
        description="D30 Trimsamsa lord, when applicable.",
    )
    trimsamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D30 Trimsamsa Rashi metadata, when applicable.",
    )
    khavedamsa_part: Optional[int] = Field(
        MISSING,
        description="D40 Khavedamsa part, when applicable.",
    )
    khavedamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D40 Khavedamsa Rashi metadata, when applicable.",
    )
    akshavedamsa_part: Optional[int] = Field(
        MISSING,
        description="D45 Akshavedamsa part, when applicable.",
    )
    akshavedamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D45 Akshavedamsa Rashi metadata, when applicable.",
    )
    shastiamsa_part: Optional[int] = Field(
        MISSING,
        description="D60 Shastiamsa part, when applicable.",
    )
    shastiamsa_rashi: Optional[RashiInfo] = Field(
        MISSING,
        description="D60 Shastiamsa Rashi metadata, when applicable.",
    )


class VargaPlanetInfo(StrictResponseModel):
    """Planet placement in a Varga chart."""

    planet: str = Field(..., description="Planet key.")
    source_longitude: float = Field(
        ...,
        description="Source sidereal longitude in the base Kundali chart.",
    )
    varga_position: VargaPositionInfo = Field(
        ...,
        description="Calculated Varga placement for the planet.",
    )


class VargaChartInfo(StrictResponseModel):
    """One supported Varga chart in a Kundali API response."""

    varga_number: int = Field(..., description="Divisional chart number.")
    varga_code: VargaCode = Field(..., description="Divisional chart code.")
    varga_name: str = Field(..., description="Divisional chart name.")
    lagna: Optional[VargaPositionInfo] = Field(
        MISSING,
        description="Calculated Varga placement for Lagna, when available.",
    )
    planets: List[VargaPlanetInfo] = Field(
        default_factory=list,
        description="Planet placements in this Varga chart.",
    )


class KundaliResponse(StrictResponseModel):
    """Response schema matching basic Kundali chart assembly output."""

    lagna: LagnaInfo = Field(..., description="Lagna information.")
    planets: List[KundaliPlanetInfo] = Field(..., description="Planet positions.")
    houses: List[HousePlaceholderInfo] = Field(
        ...,
        description="Placeholder house information.",
    )
    vargas: Optional[dict[str, VargaChartInfo]] = Field(
        MISSING,
        description="Optional supported Varga charts when explicitly requested.",
    )
    strength: Optional[dict[str, Any]] = Field(
        MISSING,
        description="Optional Planet Strength Summary when explicitly requested.",
    )
    ashtakavarga: Optional[dict[str, Any]] = Field(
        MISSING,
        description="Optional Ashtakavarga Summary when explicitly requested.",
    )
    special_lagna: Optional[dict[str, Any]] = Field(
        MISSING,
        description="Optional Special Lagna Summary when explicitly requested.",
    )
    predictions: Optional[dict[str, Any]] = Field(
        MISSING,
        description="Optional Prediction Framework output when explicitly requested.",
    )
