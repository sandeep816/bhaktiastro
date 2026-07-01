"""Integration tests for the Kundali API route."""

from __future__ import annotations

import unittest
from unittest.mock import patch

try:
    from fastapi import HTTPException
    from pydantic import ValidationError

    from backend.app.api.v1.kundali import get_kundali, router
    from backend.app.main import app
    from backend.app.schemas.kundali import KundaliRequest
except ModuleNotFoundError:
    HTTPException = None  # type: ignore[assignment]
    ValidationError = None  # type: ignore[assignment]
    get_kundali = None  # type: ignore[assignment]
    router = None  # type: ignore[assignment]
    app = None  # type: ignore[assignment]
    KundaliRequest = None  # type: ignore[assignment]


@unittest.skipIf(KundaliRequest is None, "fastapi or pydantic is not installed")
class KundaliApiTest(unittest.TestCase):
    """Validate Kundali API behavior."""

    def test_router_exposes_post_kundali(self) -> None:
        routes = [
            route
            for route in router.routes
            if getattr(route, "path", None) == "/kundali"
        ]

        self.assertEqual(len(routes), 1)
        self.assertIn("POST", routes[0].methods)

    def test_app_includes_kundali_route(self) -> None:
        routes = [
            route
            for route in app.routes
            if getattr(route, "path", None) == "/api/v1/kundali"
        ]

        self.assertEqual(len(routes), 1)
        self.assertIn("POST", routes[0].methods)

    def test_kundali_route_returns_response_for_valid_jaipur_input(self) -> None:
        response = get_kundali(_jaipur_request())
        data = response.model_dump(mode="json")

        self.assertEqual(set(data.keys()), {"lagna", "planets", "houses"})
        self.assertIn("ascendant_longitude", data["lagna"])
        self.assertIn("rashi", data["lagna"])
        self.assertEqual(data["lagna"]["rashi_index"], data["lagna"]["rashi"]["index"])
        self.assertEqual(len(data["planets"]), 9)
        self.assertEqual(len(data["houses"]), 12)

    def test_response_contains_planet_rashi_metadata(self) -> None:
        response = get_kundali(_jaipur_request())
        data = response.model_dump(mode="json")

        for planet in data["planets"]:
            self.assertIn("rashi", planet)
            self.assertIn("rashi_degree", planet)
            self.assertIn("english", planet["rashi"])
            self.assertIn("hindi", planet["rashi"])

    def test_invalid_latitude_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            KundaliRequest(
                year=1990,
                month=1,
                day=1,
                hour=12,
                minute=0,
                second=0,
                timezone_offset=5.5,
                latitude=91.0,
                longitude=75.7873,
            )

    def test_invalid_timezone_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            KundaliRequest(
                year=1990,
                month=1,
                day=1,
                hour=12,
                minute=0,
                second=0,
                timezone_offset=-13.0,
                latitude=26.9124,
                longitude=75.7873,
            )

    def test_calculation_value_error_returns_clear_error_response(self) -> None:
        with patch(
            "backend.app.api.v1.kundali.assemble_kundali_chart",
            side_effect=ValueError("Invalid local date/time components"),
        ):
            with self.assertRaises(HTTPException) as exc_info:
                get_kundali(_jaipur_request())

        self.assertEqual(exc_info.exception.status_code, 400)
        self.assertEqual(
            exc_info.exception.detail,
            "Invalid local date/time components",
        )


def _jaipur_request() -> KundaliRequest:
    return KundaliRequest(
        year=1990,
        month=1,
        day=1,
        hour=12,
        minute=0,
        second=0,
        timezone_offset=5.5,
        latitude=26.9124,
        longitude=75.7873,
        ayanamsa="lahiri",
    )


if __name__ == "__main__":
    unittest.main()
