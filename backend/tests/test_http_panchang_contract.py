"""HTTP contract tests for the first future Playground integration."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient, Response

from backend.app.config import APP_NAME, APP_VERSION
from backend.app.main import app

ROOT_DIR = Path(__file__).resolve().parents[2]
PANCHANG_RESPONSE_FIXTURE = (
    ROOT_DIR / "docs" / "examples" / "panchang_response_jodhpur.json"
)
VALID_REQUEST = {
    "year": 1985,
    "month": 4,
    "day": 20,
    "hour": 18,
    "minute": 10,
    "second": 0,
    "timezone_offset": 5.5,
    "latitude": 26.2389,
    "longitude": 73.0243,
    "language": "hi",
    "ayanamsa": "lahiri",
}


def test_health_is_liveness_only_with_stable_route_and_shape() -> None:
    with patch("backend.app.api.v1.panchang.calculate_basic_panchang") as calculate:
        response = _request("GET", "/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }
    assert set(response.json()) == {"status", "app", "version"}
    calculate.assert_not_called()


def test_valid_panchang_request_forwards_lahiri_and_returns_finite_json() -> None:
    with patch(
        "backend.app.api.v1.panchang.calculate_basic_panchang",
        return_value=_response_payload(),
    ) as calculate:
        response = _request("POST", "/api/v1/panchang", json=VALID_REQUEST)

    assert response.status_code == 200
    json.dumps(response.json(), allow_nan=False)
    calculate.assert_called_once_with(
        year=1985,
        month=4,
        day=20,
        hour=18,
        minute=10,
        second=0,
        timezone_offset=5.5,
        latitude=26.2389,
        longitude=73.0243,
        ayanamsa_mode="lahiri",
    )


def test_unknown_request_field_uses_standard_framework_validation() -> None:
    request = {**VALID_REQUEST, "date": "1985-04-20"}

    with patch("backend.app.api.v1.panchang.calculate_basic_panchang") as calculate:
        response = _request("POST", "/api/v1/panchang", json=request)

    assert response.status_code == 422
    assert set(response.json()) == {"detail"}
    assert response.json()["detail"][0]["type"] == "extra_forbidden"
    assert response.json()["detail"][0]["loc"] == ["body", "date"]
    calculate.assert_not_called()


@pytest.mark.parametrize("language", ["hi", "en"])
def test_deprecated_supported_language_values_preserve_fixed_response(
    language: str,
) -> None:
    request = {**VALID_REQUEST, "language": language}
    with patch(
        "backend.app.api.v1.panchang.calculate_basic_panchang",
        return_value=_response_payload(),
    ):
        response = _request("POST", "/api/v1/panchang", json=request)

    assert response.status_code == 200
    assert response.json()["vara"]["name_en"] == "Saturday"
    assert response.json()["vara"]["name_hi"] == "शनिवार"


def test_unsupported_language_uses_standard_framework_validation() -> None:
    response = _request(
        "POST",
        "/api/v1/panchang",
        json={**VALID_REQUEST, "language": "sa"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "language"]


def test_unsupported_ayanamsa_uses_standard_framework_validation() -> None:
    response = _request(
        "POST",
        "/api/v1/panchang",
        json={**VALID_REQUEST, "ayanamsa": "raman"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "ayanamsa"]


@pytest.mark.parametrize(
    ("failure", "status_code", "error", "message"),
    [
        (
            ValueError("sensitive input detail"),
            400,
            "panchang_input_invalid",
            "Panchang calculation input was invalid.",
        ),
        (
            RuntimeError("/private/path/to/ephemeris"),
            500,
            "panchang_calculation_failed",
            "Panchang calculation could not be completed.",
        ),
        (
            OSError("/private/path/to/runtime"),
            500,
            "internal_server_error",
            "An unexpected server error occurred.",
        ),
    ],
)
def test_application_failures_use_stable_safe_error_envelope(
    failure: Exception,
    status_code: int,
    error: str,
    message: str,
) -> None:
    with patch(
        "backend.app.api.v1.panchang.calculate_basic_panchang",
        side_effect=failure,
    ):
        response = _request("POST", "/api/v1/panchang", json=VALID_REQUEST)

    assert response.status_code == status_code
    assert response.json() == {
        "schema_version": "1.0",
        "error": error,
        "message": message,
        "details": [],
    }
    assert "/private/" not in response.text
    assert "sensitive input detail" not in response.text
    json.dumps(response.json(), allow_nan=False)


@pytest.mark.parametrize(
    "non_finite_value",
    [float("nan"), float("inf"), float("-inf")],
)
def test_non_finite_calculation_output_is_rejected(
    non_finite_value: float,
) -> None:
    payload = _response_payload()
    payload["ayanamsa"]["value"] = non_finite_value

    with patch(
        "backend.app.api.v1.panchang.calculate_basic_panchang",
        return_value=payload,
    ):
        response = _request("POST", "/api/v1/panchang", json=VALID_REQUEST)

    assert response.status_code == 500
    assert response.json() == {
        "schema_version": "1.0",
        "error": "panchang_response_invalid",
        "message": "Panchang calculation produced an invalid response.",
        "details": [
            {
                "code": "non_finite_number",
                "path": ["ayanamsa", "value"],
            }
        ],
    }
    json.dumps(response.json(), allow_nan=False)


def test_invalid_calculation_output_uses_safe_structured_details() -> None:
    payload = _response_payload()
    del payload["vara"]

    with patch(
        "backend.app.api.v1.panchang.calculate_basic_panchang",
        return_value=payload,
    ):
        response = _request("POST", "/api/v1/panchang", json=VALID_REQUEST)

    assert response.status_code == 500
    assert response.json()["error"] == "panchang_response_invalid"
    assert response.json()["details"] == [
        {
            "code": "invalid_response_value",
            "path": ["vara"],
        }
    ]
    assert "input" not in response.text


def test_api_prefix_routes_and_openapi_contract_remain_stable() -> None:
    openapi = _request("GET", "/openapi.json")

    assert openapi.status_code == 200
    schema = openapi.json()
    assert set(schema["paths"]) == {
        "/api/v1/health",
        "/api/v1/panchang",
        "/api/v1/kundali",
        "/api/v1/dasha",
    }
    request_schema = schema["components"]["schemas"]["PanchangRequest"]
    assert request_schema["additionalProperties"] is False
    assert request_schema["properties"]["language"]["deprecated"] is True
    assert request_schema["properties"]["ayanamsa"]["const"] == "lahiri"
    responses = schema["paths"]["/api/v1/panchang"]["post"]["responses"]
    assert responses["400"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/TechnicalErrorResponse"
    }
    assert responses["500"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/TechnicalErrorResponse"
    }


def test_direct_browser_cors_remains_unsupported_for_server_proxy_boundary() -> None:
    response = _request(
        "OPTIONS",
        "/api/v1/panchang",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 405
    assert "access-control-allow-origin" not in response.headers
    assert "access-control-allow-methods" not in response.headers


def _response_payload() -> dict[str, object]:
    return json.loads(PANCHANG_RESPONSE_FIXTURE.read_text(encoding="utf-8"))


def _request(
    method: str,
    path: str,
    **kwargs: object,
) -> Response:
    with patch("fastapi.routing.run_in_threadpool", new=_run_inline):
        return asyncio.run(_async_request(method, path, **kwargs))


async def _async_request(
    method: str,
    path: str,
    **kwargs: object,
) -> Response:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.request(method, path, **kwargs)


async def _run_inline(
    function: Callable[..., object],
    *args: object,
    **kwargs: object,
) -> object:
    """Run sync endpoints inline for deterministic in-process ASGI tests."""

    return function(*args, **kwargs)
