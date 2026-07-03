"""Pydantic schemas for Dasha requests and responses."""

from __future__ import annotations

from datetime import date as Date
from datetime import datetime as DateTime
from datetime import time as Time
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING


class DashaRequest(BaseModel):
    """Request schema for Dasha calculation."""

    date: Date = Field(
        ...,
        description="Local calendar date for Dasha calculation.",
    )
    time: Time = Field(
        Time(hour=12),
        description="Local time for Dasha calculation.",
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
    target_date: Optional[Date] = Field(
        None,
        description="Optional local target date for current Dasha lookup.",
    )
    target_datetime: Optional[DateTime] = Field(
        None,
        description="Optional target datetime for current Dasha lookup.",
    )
    include_antardasha: bool = Field(
        True,
        description="Whether to include Antardasha periods.",
    )
    include_pratyantardasha: bool = Field(
        False,
        description="Whether to include Pratyantardasha periods.",
    )


class StrictResponseModel(BaseModel):
    """Base model for response sections with stable, explicit keys."""

    model_config = ConfigDict(extra="forbid")


class DashaPeriod(StrictResponseModel):
    """Base Dasha period response fields."""

    start_datetime: str = Field(..., description="Period start datetime.")
    end_datetime: str = Field(..., description="Period end datetime.")
    duration_years: float = Field(..., description="Period duration in Dasha years.")


class PratyantardashaPeriod(DashaPeriod):
    """Pratyantardasha period response section."""

    mahadasha_lord: str = Field(..., description="Parent Mahadasha lord.")
    antardasha_lord: str = Field(..., description="Parent Antardasha lord.")
    pratyantardasha_lord: str = Field(..., description="Pratyantardasha lord.")


class AntardashaPeriod(DashaPeriod):
    """Antardasha period response section."""

    mahadasha_lord: str = Field(..., description="Parent Mahadasha lord.")
    antardasha_lord: str = Field(..., description="Antardasha lord.")
    pratyantardashas: Optional[list[PratyantardashaPeriod]] = Field(
        MISSING,
        description="Optional Pratyantardasha periods.",
    )


class MahadashaPeriod(DashaPeriod):
    """Mahadasha period response section."""

    dasha_lord: str = Field(..., description="Mahadasha lord.")
    is_birth_dasha: bool = Field(
        ...,
        description="Whether this is the balance period active at birth.",
    )
    antardashas: Optional[list[AntardashaPeriod]] = Field(
        MISSING,
        description="Optional Antardasha periods.",
    )


class CurrentDasha(StrictResponseModel):
    """Current Dasha lookup response section."""

    target_datetime: str = Field(..., description="Target datetime for lookup.")
    mahadasha: Optional[MahadashaPeriod] = Field(
        None,
        description="Active Mahadasha period, or null when outside timeline.",
    )
    antardasha: Optional[AntardashaPeriod] = Field(
        None,
        description="Active Antardasha period, or null when unavailable.",
    )
    pratyantardasha: Optional[PratyantardashaPeriod] = Field(
        None,
        description="Active Pratyantardasha period, or null when unavailable.",
    )


class DashaMetadata(StrictResponseModel):
    """Dasha response metadata."""

    engine: Literal["dasha"] = Field(..., description="Calculation engine key.")
    system: Literal["vimshottari"] = Field(..., description="Dasha system key.")


class DashaResponse(StrictResponseModel):
    """Response schema matching built Dasha timeline output."""

    birth_datetime: str = Field(..., description="Birth datetime used.")
    target_datetime: Optional[str] = Field(
        None,
        description="Target datetime used for current Dasha lookup.",
    )
    mahadasha_timeline: list[MahadashaPeriod] = Field(
        ...,
        description="Generated Mahadasha timeline.",
    )
    current_dasha: Optional[CurrentDasha] = Field(
        None,
        description="Optional current Dasha lookup result.",
    )
    metadata: DashaMetadata = Field(..., description="Dasha response metadata.")
