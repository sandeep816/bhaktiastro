"""Panchang API routes."""

from __future__ import annotations

import json

from fastapi import APIRouter
from pydantic import ValidationError

from backend.app.api.errors import TechnicalHTTPException
from backend.app.astrology.panchang import calculate_basic_panchang
from backend.app.schemas.errors import TechnicalErrorDetail, TechnicalErrorResponse
from backend.app.schemas.panchang import PanchangRequest, PanchangResponse

router = APIRouter()


@router.post(
    "/panchang",
    response_model=PanchangResponse,
    responses={
        400: {"model": TechnicalErrorResponse},
        500: {"model": TechnicalErrorResponse},
    },
)
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
            ayanamsa_mode=request.ayanamsa,
        )
    except (TypeError, ValueError) as exc:
        raise TechnicalHTTPException(
            status_code=400,
            error="panchang_input_invalid",
            message="Panchang calculation input was invalid.",
        ) from exc
    except RuntimeError as exc:
        raise TechnicalHTTPException(
            status_code=500,
            error="panchang_calculation_failed",
            message="Panchang calculation could not be completed.",
        ) from exc
    except Exception as exc:
        raise TechnicalHTTPException(
            status_code=500,
            error="internal_server_error",
            message="An unexpected server error occurred.",
        ) from exc

    try:
        response = PanchangResponse.model_validate(result)
        json.dumps(response.model_dump(mode="json"), allow_nan=False)
    except ValidationError as exc:
        raise TechnicalHTTPException(
            status_code=500,
            error="panchang_response_invalid",
            message="Panchang calculation produced an invalid response.",
            details=_response_validation_details(exc),
        ) from exc
    except (TypeError, ValueError) as exc:
        raise TechnicalHTTPException(
            status_code=500,
            error="panchang_response_invalid",
            message="Panchang calculation produced an invalid response.",
            details=[
                TechnicalErrorDetail(
                    code="non_finite_number",
                    path=[],
                )
            ],
        ) from exc

    return response


def _response_validation_details(
    exc: ValidationError,
) -> list[TechnicalErrorDetail]:
    """Return deterministic, non-sensitive response validation details."""

    details = []
    for issue in exc.errors(
        include_url=False,
        include_context=False,
        include_input=False,
    ):
        code = (
            "non_finite_number"
            if issue["type"] == "finite_number"
            else "invalid_response_value"
        )
        details.append(
            TechnicalErrorDetail(
                code=code,
                path=[
                    item if isinstance(item, int) else str(item)
                    for item in issue["loc"]
                ],
            )
        )
    return details
