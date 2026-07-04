"""Integration tests for the Kundali API route."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
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
            for route in _iter_app_routes()
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

    def test_kundali_request_defaults_to_excluding_vargas(self) -> None:
        request = _jaipur_request()
        response = get_kundali(request)
        data = response.model_dump(mode="json")

        self.assertFalse(request.include_vargas)
        self.assertFalse(request.include_strength)
        self.assertFalse(request.include_ashtakavarga)
        self.assertFalse(request.include_special_lagnas)
        self.assertEqual(set(data.keys()), {"lagna", "planets", "houses"})
        self.assertNotIn("vargas", data)
        self.assertNotIn("strength", data)
        self.assertNotIn("ashtakavarga", data)
        self.assertNotIn("special_lagna", data)

    def test_kundali_route_without_include_strength_remains_unchanged(self) -> None:
        response = get_kundali(_jaipur_request())
        data = response.model_dump(mode="json")

        self.assertEqual(set(data.keys()), {"lagna", "planets", "houses"})
        self.assertNotIn("strength", data)

    def test_kundali_route_without_include_ashtakavarga_remains_unchanged(
        self,
    ) -> None:
        response = get_kundali(_jaipur_request())
        data = response.model_dump(mode="json")

        self.assertEqual(set(data.keys()), {"lagna", "planets", "houses"})
        self.assertNotIn("ashtakavarga", data)

    def test_kundali_route_without_include_special_lagnas_remains_unchanged(
        self,
    ) -> None:
        response = get_kundali(_jaipur_request())
        data = response.model_dump(mode="json")

        self.assertEqual(set(data.keys()), {"lagna", "planets", "houses"})
        self.assertNotIn("special_lagna", data)

    def test_kundali_route_can_include_supported_vargas(self) -> None:
        response = get_kundali(_jaipur_request(include_vargas=True))
        data = response.model_dump(mode="json")

        self.assertEqual(
            set(data["vargas"]),
            {
                "D2",
                "D3",
                "D7",
                "D9",
                "D10",
                "D12",
                "D16",
                "D20",
                "D24",
                "D27",
                "D30",
                "D40",
                "D45",
                "D60",
            },
        )
        self.assertEqual(data["vargas"]["D9"]["varga_name"], "Navamsa")
        self.assertEqual(len(data["vargas"]["D9"]["planets"]), 9)

    def test_kundali_route_includes_d9_when_vargas_enabled(self) -> None:
        response = get_kundali(_jaipur_request(include_vargas=True))
        data = response.model_dump(mode="json")

        self.assertIn("D9", data["vargas"])
        self.assertEqual(data["vargas"]["D9"]["varga_code"], "D9")
        self.assertIn("lagna", data["vargas"]["D9"])

    def test_kundali_route_can_include_strength_summary(self) -> None:
        response = get_kundali(_jaipur_request(include_strength=True))
        data = response.model_dump(mode="json")

        self.assertIn("strength", data)
        self.assertIn("planets", data["strength"])
        self.assertIn("ranking", data["strength"])
        self.assertEqual(data["strength"]["metadata"]["planet_count"], 9)

    def test_strength_summary_contains_planets(self) -> None:
        response = get_kundali(_jaipur_request(include_strength=True))
        data = response.model_dump(mode="json")

        self.assertEqual(len(data["strength"]["planets"]), 9)
        self.assertTrue(
            all(
                {"planet", "shadbala", "ishta_kashta", "summary_status"}
                <= set(planet)
                for planet in data["strength"]["planets"]
            )
        )

    def test_strength_summary_includes_strongest_and_weakest_planets(self) -> None:
        response = get_kundali(_jaipur_request(include_strength=True))
        data = response.model_dump(mode="json")

        self.assertIn("strongest_planet", data["strength"])
        self.assertIn("weakest_planet", data["strength"])
        self.assertIsNotNone(data["strength"]["strongest_planet"])
        self.assertIsNotNone(data["strength"]["weakest_planet"])

    def test_kundali_route_can_include_ashtakavarga_summary(self) -> None:
        response = get_kundali(_jaipur_request(include_ashtakavarga=True))
        data = response.model_dump(mode="json")

        self.assertIn("ashtakavarga", data)
        self.assertIn("sarvashtakavarga", data["ashtakavarga"])
        self.assertIn("bhinnashtakavarga", data["ashtakavarga"])
        self.assertIn("house_ranking", data["ashtakavarga"])

    def test_ashtakavarga_summary_contains_sarvashtakavarga(self) -> None:
        response = get_kundali(_jaipur_request(include_ashtakavarga=True))
        data = response.model_dump(mode="json")

        sarvashtakavarga = data["ashtakavarga"]["sarvashtakavarga"]

        self.assertEqual(len(sarvashtakavarga["houses"]), 12)
        self.assertEqual(
            sarvashtakavarga["total_bindus"],
            sum(sarvashtakavarga["houses"].values()),
        )

    def test_ashtakavarga_summary_contains_bhinnashtakavarga(self) -> None:
        response = get_kundali(_jaipur_request(include_ashtakavarga=True))
        data = response.model_dump(mode="json")

        self.assertEqual(
            set(data["ashtakavarga"]["bhinnashtakavarga"]),
            {
                "sun",
                "moon",
                "mars",
                "mercury",
                "jupiter",
                "venus",
                "saturn",
            },
        )

    def test_kundali_route_can_include_special_lagna_summary(self) -> None:
        response = get_kundali(_jaipur_request(include_special_lagnas=True))
        data = response.model_dump(mode="json")

        self.assertIn("special_lagna", data)
        self.assertIn("arudha_lagna", data["special_lagna"])
        self.assertIn("upapada_lagna", data["special_lagna"])
        self.assertIn("hora_lagna", data["special_lagna"])
        self.assertIn("ghati_lagna", data["special_lagna"])
        self.assertIn("bhava_cusps", data["special_lagna"])

    def test_special_lagna_summary_contains_bhava_cusps(self) -> None:
        response = get_kundali(_jaipur_request(include_special_lagnas=True))
        data = response.model_dump(mode="json")

        bhava_cusps = data["special_lagna"]["bhava_cusps"]

        self.assertEqual(bhava_cusps["house_system"], "equal_foundation")
        self.assertEqual(len(bhava_cusps["house_cusps"]), 12)

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
                include_vargas=True,
                include_ashtakavarga=True,
                include_special_lagnas=True,
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


def _jaipur_request(
    include_vargas: bool = False,
    include_strength: bool = False,
    include_ashtakavarga: bool = False,
    include_special_lagnas: bool = False,
) -> KundaliRequest:
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
        include_vargas=include_vargas,
        include_strength=include_strength,
        include_ashtakavarga=include_ashtakavarga,
        include_special_lagnas=include_special_lagnas,
    )


if __name__ == "__main__":
    unittest.main()
