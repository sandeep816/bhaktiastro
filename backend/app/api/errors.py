"""Application-generated technical HTTP errors."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from backend.app.schemas.errors import (
    TechnicalErrorCode,
    TechnicalErrorDetail,
    TechnicalErrorResponse,
)


class TechnicalHTTPException(HTTPException):
    """HTTP exception carrying the stable technical error envelope."""

    def __init__(
        self,
        *,
        status_code: int,
        error: TechnicalErrorCode,
        message: str,
        details: Sequence[TechnicalErrorDetail] = (),
    ) -> None:
        self.payload = TechnicalErrorResponse(
            error=error,
            message=message,
            details=list(details),
        )
        super().__init__(
            status_code=status_code,
            detail=self.payload.model_dump(mode="json"),
        )


async def technical_http_exception_handler(
    _request: Request,
    exc: TechnicalHTTPException,
) -> JSONResponse:
    """Render a technical error without FastAPI's outer ``detail`` wrapper."""

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.payload.model_dump(mode="json"),
        headers=exc.headers,
    )
