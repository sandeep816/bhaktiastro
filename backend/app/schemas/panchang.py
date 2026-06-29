"""Pydantic schemas for basic Panchang requests and responses."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class PanchangRequest(BaseModel):
    """Request schema for basic Panchang calculation."""

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
    language: Literal["hi", "en"] = Field(
        "hi",
        description="Response language preference for MVP.",
    )
    ayanamsa: Literal["lahiri"] = Field(
        "lahiri",
        description="Ayanamsa mode for MVP calculations.",
    )


class JulianDayInfo(BaseModel):
    """Julian Day section of a Panchang response."""

    utc_datetime: str = Field(
        ...,
        description="UTC datetime used for Julian Day calculation.",
    )
    julian_day_ut: float = Field(
        ...,
        description="Julian Day in Universal Time.",
    )


class AyanamsaInfo(BaseModel):
    """Ayanamsa section of a Panchang response."""

    value: float = Field(
        ...,
        description="Ayanamsa value in degrees.",
    )


class DmsInfo(BaseModel):
    """Degrees, minutes, and seconds for a planetary rashi position."""

    degrees: int = Field(..., description="Whole degrees.")
    minutes: int = Field(..., description="Whole minutes.")
    seconds: float = Field(..., description="Seconds.")


class PlanetSummary(BaseModel):
    """Sun or Moon summary from the planet position engine."""

    planet: str = Field(..., description="Planet key.")
    sidereal_longitude: float = Field(
        ...,
        description="Sidereal longitude in degrees.",
    )
    tropical_longitude: Optional[float] = Field(
        None,
        description="Tropical longitude in degrees when available.",
    )
    rashi_index: Optional[int] = Field(
        None,
        description="Zero-based rashi index when available.",
    )
    rashi_name_hi: Optional[str] = Field(
        None,
        description="Hindi rashi name when available.",
    )
    degree_in_rashi: Optional[float] = Field(
        None,
        description="Degree within the rashi when available.",
    )
    dms: Optional[DmsInfo] = Field(
        None,
        description="Degree-minute-second position within the rashi.",
    )
    speed: Optional[float] = Field(
        None,
        description="Planet speed when available.",
    )
    retrograde: Optional[bool] = Field(
        None,
        description="Retrograde status when available.",
    )


class TithiInfo(BaseModel):
    """Tithi section of a Panchang response."""

    tithi_number: int = Field(..., description="Tithi number from 1 to 30.")
    name_en: str = Field(..., description="English Tithi name.")
    name_hi: str = Field(..., description="Hindi Tithi name.")
    name_sa: str = Field(..., description="Sanskrit/transliteration Tithi name.")
    paksha: str = Field(..., description="Paksha name.")
    start_angle: float = Field(..., description="Tithi start angle in degrees.")
    end_angle: float = Field(..., description="Tithi end angle in degrees.")
    current_angle: float = Field(..., description="Current Moon-Sun angle.")
    degrees_completed: float = Field(
        ...,
        description="Degrees completed within the current Tithi.",
    )
    degrees_remaining: float = Field(
        ...,
        description="Degrees remaining in the current Tithi.",
    )
    end_time_local: Optional[str] = Field(
        None,
        description="Local datetime when the current Tithi ends.",
    )
    end_time_utc: Optional[str] = Field(
        None,
        description="UTC datetime when the current Tithi ends.",
    )


class NakshatraInfo(BaseModel):
    """Nakshatra section of a Panchang response."""

    index: int = Field(..., description="Zero-based Nakshatra index.")
    name_en: str = Field(..., description="English Nakshatra name.")
    name_hi: str = Field(..., description="Hindi Nakshatra name.")
    name_sa: str = Field(
        ...,
        description="Sanskrit/transliteration Nakshatra name.",
    )
    pada: int = Field(..., description="Pada number from 1 to 4.")
    ruling_planet: str = Field(..., description="Nakshatra ruling planet.")
    start_degree: float = Field(..., description="Nakshatra start degree.")
    end_degree: float = Field(..., description="Nakshatra end degree.")
    degree_within_nakshatra: float = Field(
        ...,
        description="Degree completed within the Nakshatra.",
    )
    current_degree: Optional[float] = Field(
        None,
        description="Current Moon sidereal degree used for Nakshatra.",
    )
    degrees_remaining: Optional[float] = Field(
        None,
        description="Degrees remaining in the current Nakshatra.",
    )
    end_time_local: Optional[str] = Field(
        None,
        description="Local datetime when the current Nakshatra ends.",
    )
    end_time_utc: Optional[str] = Field(
        None,
        description="UTC datetime when the current Nakshatra ends.",
    )


class YogaInfo(BaseModel):
    """Panchang Yoga section of a Panchang response."""

    yoga_index: int = Field(..., description="Yoga index from 1 to 27.")
    name_en: str = Field(..., description="English Yoga name.")
    name_hi: str = Field(..., description="Hindi Yoga name.")
    name_sa: str = Field(..., description="Sanskrit/transliteration Yoga name.")
    start_degree: float = Field(..., description="Yoga start degree.")
    end_degree: float = Field(..., description="Yoga end degree.")
    current_degree: float = Field(..., description="Current Sun-Moon sum degree.")
    degrees_completed: float = Field(
        ...,
        description="Degrees completed within the current Yoga.",
    )
    degrees_remaining: float = Field(
        ...,
        description="Degrees remaining in the current Yoga.",
    )


class KaranaInfo(BaseModel):
    """Karana section of a Panchang response."""

    karana_index: int = Field(..., description="Karana constants index.")
    name_en: str = Field(..., description="English Karana name.")
    name_hi: str = Field(..., description="Hindi Karana name.")
    name_sa: str = Field(..., description="Sanskrit/transliteration Karana name.")
    type: str = Field(..., description="Karana type: Repeating or Fixed.")
    half_tithi_index: int = Field(..., description="Half-tithi index from 0 to 59.")
    current_angle: float = Field(..., description="Current Moon-Sun angle.")
    start_angle: float = Field(..., description="Karana start angle in degrees.")
    end_angle: float = Field(..., description="Karana end angle in degrees.")
    degrees_completed: float = Field(
        ...,
        description="Degrees completed within the current Karana.",
    )
    degrees_remaining: float = Field(
        ...,
        description="Degrees remaining in the current Karana.",
    )


class VaraInfo(BaseModel):
    """Vara section of a Panchang response."""

    index: int = Field(..., description="Vara index from 1 to 7.")
    name_en: str = Field(..., description="English Vara name.")
    name_hi: str = Field(..., description="Hindi Vara name.")
    name_sa: str = Field(..., description="Sanskrit/transliteration Vara name.")
    ruling_planet: str = Field(..., description="Vara ruling planet.")


class RiseSetInfo(BaseModel):
    """Rise/set section of a Panchang response."""

    event: str = Field(..., description="Rise/set event name.")
    local_time: Optional[str] = Field(
        None,
        description="Local event time as HH:MM:SS, or null if not found.",
    )
    utc_datetime: Optional[str] = Field(
        None,
        description="UTC event datetime, or null if not found.",
    )
    timezone_offset: float = Field(
        ...,
        description="Local UTC offset in decimal hours.",
    )


class PanchangResponse(BaseModel):
    """Response schema matching calculate_basic_panchang output."""

    julian_day: JulianDayInfo = Field(..., description="Julian Day information.")
    ayanamsa: AyanamsaInfo = Field(..., description="Ayanamsa information.")
    sun: PlanetSummary = Field(..., description="Sun position summary.")
    moon: PlanetSummary = Field(..., description="Moon position summary.")
    tithi: TithiInfo = Field(..., description="Tithi information.")
    nakshatra: NakshatraInfo = Field(..., description="Nakshatra information.")
    yoga: YogaInfo = Field(..., description="Panchang Yoga information.")
    karana: KaranaInfo = Field(..., description="Karana information.")
    vara: VaraInfo = Field(..., description="Vara information.")
    sunrise: RiseSetInfo = Field(..., description="Sunrise information.")
    sunset: RiseSetInfo = Field(..., description="Sunset information.")
    moonrise: RiseSetInfo = Field(..., description="Moonrise information.")
    moonset: RiseSetInfo = Field(..., description="Moonset information.")
