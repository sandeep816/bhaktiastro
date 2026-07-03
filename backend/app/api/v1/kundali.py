"""Kundali API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.kundali.chart import assemble_kundali_chart
from backend.app.schemas.kundali import KundaliRequest, KundaliResponse

router = APIRouter()


@router.post("/kundali", response_model=KundaliResponse)
def get_kundali(request: KundaliRequest) -> KundaliResponse:
    """Return a basic Kundali chart for a validated request."""

    try:
        result = assemble_kundali_chart(
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            second=request.second,
            timezone_offset=request.timezone_offset,
            latitude=request.latitude,
            longitude=request.longitude,
            ayanamsa_mode=request.ayanamsa,
            include_vargas=request.include_vargas,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return KundaliResponse.model_validate(result)
