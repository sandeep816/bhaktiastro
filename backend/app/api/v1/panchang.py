"""Panchang API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.astrology.panchang import calculate_basic_panchang
from backend.app.schemas.panchang import PanchangRequest, PanchangResponse

router = APIRouter()


@router.post("/panchang", response_model=PanchangResponse)
def get_panchang(request: PanchangRequest) -> PanchangResponse:
    """Return basic Panchang data for a validated request."""

    try:
        result = calculate_basic_panchang(
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            second=request.second,
            timezone_offset=request.timezone_offset,
            latitude=request.latitude,
            longitude=request.longitude,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PanchangResponse.model_validate(result)
