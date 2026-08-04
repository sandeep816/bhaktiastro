"""Stable technical HTTP error schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

HTTP_ERROR_SCHEMA_VERSION = "1.0"

TechnicalErrorCode = Literal[
    "panchang_input_invalid",
    "panchang_calculation_failed",
    "panchang_response_invalid",
    "internal_server_error",
]

TechnicalErrorDetailCode = Literal[
    "invalid_response_value",
    "non_finite_number",
]


class StrictTechnicalErrorModel(BaseModel):
    """Base model for exact, finite technical error payloads."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class TechnicalErrorDetail(StrictTechnicalErrorModel):
    """One deterministic, non-sensitive technical error detail."""

    code: TechnicalErrorDetailCode
    path: list[str | int] = Field(default_factory=list)


class TechnicalErrorResponse(StrictTechnicalErrorModel):
    """Versioned application-generated HTTP error envelope."""

    schema_version: Literal["1.0"] = HTTP_ERROR_SCHEMA_VERSION
    error: TechnicalErrorCode
    message: str
    details: list[TechnicalErrorDetail] = Field(default_factory=list)
