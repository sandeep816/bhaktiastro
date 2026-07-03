"""Dasha API routes."""

from __future__ import annotations

from datetime import date as Date
from datetime import datetime, time as Time, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.app.astrology.panchang import calculate_basic_panchang
from backend.app.dasha.builder import build_dasha_timeline
from backend.app.schemas.dasha import DashaRequest, DashaResponse

router = APIRouter()


@router.post("/dasha", response_model=DashaResponse)
def get_dasha(request: DashaRequest) -> DashaResponse:
    """Return Vimshottari Dasha data for a validated request."""

    birth_datetime = _build_local_datetime(
        request.date,
        request.time,
        request.timezone_offset,
    )
    target_datetime = _resolve_target_datetime(request)

    try:
        panchang = calculate_basic_panchang(
            year=request.date.year,
            month=request.date.month,
            day=request.date.day,
            hour=request.time.hour,
            minute=request.time.minute,
            second=request.time.second,
            timezone_offset=request.timezone_offset,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        result = build_dasha_timeline(
            birth_datetime=birth_datetime,
            nakshatra_index=_extract_nakshatra_index(panchang),
            moon_longitude=_extract_moon_longitude(panchang),
            target_datetime=target_datetime,
            include_antardasha=request.include_antardasha,
            include_pratyantardasha=request.include_pratyantardasha,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return DashaResponse.model_validate(result)


def _build_local_datetime(
    local_date: Date,
    local_time: Time,
    timezone_offset: float,
) -> datetime:
    """Build a timezone-aware local datetime from request fields."""

    return datetime.combine(
        local_date,
        local_time,
        tzinfo=_timezone_from_offset(timezone_offset),
    ).replace(microsecond=0)


def _resolve_target_datetime(request: DashaRequest) -> datetime | None:
    """Return the optional target datetime using request timezone style."""

    if request.target_datetime is not None:
        target_datetime = request.target_datetime.replace(microsecond=0)
        if target_datetime.tzinfo is None:
            return target_datetime.replace(
                tzinfo=_timezone_from_offset(request.timezone_offset),
            )
        return target_datetime

    if request.target_date is not None:
        return _build_local_datetime(
            request.target_date,
            request.time,
            request.timezone_offset,
        )

    return None


def _extract_moon_longitude(panchang: dict[str, Any]) -> float:
    """Extract Moon sidereal longitude from Panchang output."""

    try:
        return float(panchang["moon"]["sidereal_longitude"])
    except KeyError as exc:
        raise RuntimeError("Panchang output is missing Moon longitude") from exc


def _extract_nakshatra_index(panchang: dict[str, Any]) -> int:
    """Extract zero-based Nakshatra index from Panchang output."""

    try:
        return int(panchang["nakshatra"]["index"])
    except KeyError as exc:
        raise RuntimeError("Panchang output is missing Nakshatra index") from exc


def _timezone_from_offset(timezone_offset: float) -> timezone:
    """Build a fixed-offset timezone from decimal UTC offset hours."""

    return timezone(timedelta(hours=float(timezone_offset)))
