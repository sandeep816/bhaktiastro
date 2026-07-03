"""Integration tests for the Dasha API route."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

try:
    from pydantic import ValidationError

    from backend.app.api.v1.dasha import get_dasha, router
    from backend.app.main import app
    from backend.app.schemas.dasha import DashaRequest
except ModuleNotFoundError:
    ValidationError = None  # type: ignore[assignment]
    get_dasha = None  # type: ignore[assignment]
    router = None  # type: ignore[assignment]
    app = None  # type: ignore[assignment]
    DashaRequest = None  # type: ignore[assignment]


@unittest.skipIf(DashaRequest is None, "fastapi or pydantic is not installed")
class DashaApiTest(unittest.TestCase):
    """Validate Dasha API behavior."""

    def test_router_exposes_post_dasha(self) -> None:
        routes = [
            route
            for route in router.routes
            if getattr(route, "path", None) == "/dasha"
        ]

        self.assertEqual(len(routes), 1)
        self.assertIn("POST", routes[0].methods)

    def test_app_includes_dasha_route(self) -> None:
        routes = [
            route
            for route in _iter_app_routes()
            if getattr(route, "path", None) == "/api/v1/dasha"
        ]

        self.assertEqual(len(routes), 1)
        self.assertIn("POST", routes[0].methods)

    def test_dasha_route_returns_response_for_valid_jaipur_input(self) -> None:
        with patch(
            "backend.app.api.v1.dasha.calculate_basic_panchang",
            return_value=_panchang_birth_payload(),
        ):
            response = get_dasha(_jaipur_request())

        data = response.model_dump(mode="json")

        self.assertEqual(data["metadata"]["engine"], "dasha")
        self.assertEqual(data["metadata"]["system"], "vimshottari")
        self.assertGreater(len(data["mahadasha_timeline"]), 0)
        self.assertEqual(data["mahadasha_timeline"][0]["dasha_lord"], "ketu")

    def test_dasha_response_contains_metadata_and_mahadasha_timeline(self) -> None:
        with patch(
            "backend.app.api.v1.dasha.calculate_basic_panchang",
            return_value=_panchang_birth_payload(),
        ):
            response = get_dasha(_jaipur_request())

        data = response.model_dump(mode="json")

        self.assertIn("metadata", data)
        self.assertIn("mahadasha_timeline", data)
        self.assertEqual(data["metadata"]["engine"], "dasha")
        self.assertIsInstance(data["mahadasha_timeline"], list)

    def test_dasha_response_contains_current_dasha_when_target_provided(self) -> None:
        with patch(
            "backend.app.api.v1.dasha.calculate_basic_panchang",
            return_value=_panchang_birth_payload(),
        ):
            response = get_dasha(_jaipur_request(target_datetime="2026-07-03T12:00:00"))

        data = response.model_dump(mode="json")

        self.assertEqual(data["target_datetime"], "2026-07-03T12:00:00+05:30")
        self.assertIsNotNone(data["current_dasha"])
        self.assertIsNotNone(data["current_dasha"]["mahadasha"])
        self.assertIsNotNone(data["current_dasha"]["antardasha"])

    def test_invalid_request_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest(
                date="1990-01-01",
                time="12:00:00",
                timezone_offset=5.5,
                latitude=91.0,
                longitude=75.7873,
            )


def _iter_app_routes() -> list[object]:
    routes: list[object] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        if path is not None:
            routes.append(route)
            continue

        include_context = getattr(route, "include_context", None)
        included_router = getattr(include_context, "included_router", None)
        prefix = getattr(include_context, "prefix", "")
        for included_route in getattr(included_router, "routes", []):
            included_path = getattr(included_route, "path", None)
            if included_path is not None:
                routes.append(
                    SimpleNamespace(
                        path=f"{prefix}{included_path}",
                        methods=getattr(included_route, "methods", None),
                    )
                )

    return routes


def _jaipur_request(target_datetime: str | None = None) -> DashaRequest:
    return DashaRequest(
        date="1990-01-01",
        time="12:00:00",
        timezone_offset=5.5,
        latitude=26.9124,
        longitude=75.7873,
        target_datetime=target_datetime,
    )


def _panchang_birth_payload() -> dict[str, object]:
    return {
        "moon": {
            "sidereal_longitude": 0.0,
        },
        "nakshatra": {
            "index": 0,
        },
    }


if __name__ == "__main__":
    unittest.main()
