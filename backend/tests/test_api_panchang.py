"""Integration tests for the Panchang API route."""

from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from fastapi import HTTPException
    from pydantic import ValidationError

    from backend.app.api.v1.panchang import get_panchang, router
    from backend.app.main import health_check
    from backend.app.schemas.panchang import PanchangRequest
except ModuleNotFoundError:
    HTTPException = None  # type: ignore[assignment]
    ValidationError = None  # type: ignore[assignment]
    get_panchang = None  # type: ignore[assignment]
    health_check = None  # type: ignore[assignment]
    PanchangRequest = None  # type: ignore[assignment]
    router = None  # type: ignore[assignment]


@unittest.skipIf(PanchangRequest is None, "fastapi or pydantic is not installed")
class PanchangApiTest(unittest.TestCase):
    """Validate Panchang API behavior."""

    def test_router_exposes_post_panchang(self) -> None:
        routes = [
            route
            for route in router.routes
            if getattr(route, "path", None) == "/panchang"
        ]

        self.assertEqual(len(routes), 1)
        self.assertIn("POST", routes[0].methods)

    def test_panchang_route_returns_response_for_valid_jodhpur_ist_input(self) -> None:
        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            return_value=_panchang_response_payload(),
        ) as calculate_basic_panchang:
            response = get_panchang(
                PanchangRequest(
                    year=1985,
                    month=4,
                    day=20,
                    hour=18,
                    minute=10,
                    second=0,
                    timezone_offset=5.5,
                    latitude=26.2389,
                    longitude=73.0243,
                    language="hi",
                    ayanamsa="lahiri",
                )
            )

        self.assertEqual(response.vara.name_en, "Saturday")
        calculate_basic_panchang.assert_called_once_with(
            year=1985,
            month=4,
            day=20,
            hour=18,
            minute=10,
            second=0,
            timezone_offset=5.5,
            latitude=26.2389,
            longitude=73.0243,
        )

    def test_response_contains_panchang_sections(self) -> None:
        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            return_value=_panchang_response_payload(),
        ):
            response = get_panchang(
                PanchangRequest(
                    year=1985,
                    month=4,
                    day=20,
                    latitude=26.2389,
                    longitude=73.0243,
                )
            )

        data = response.model_dump()
        self.assertEqual(data["tithi"]["end_time_utc"], "1985-04-20T18:00:00Z")
        self.assertEqual(
            data["nakshatra"]["end_time_utc"],
            "1985-04-20T20:00:00Z",
        )
        for key in (
            "tithi",
            "nakshatra",
            "yoga",
            "karana",
            "vara",
            "sunrise",
            "sunset",
            "moonrise",
            "moonset",
        ):
            self.assertIn(key, data)

    def test_missing_moonrise_and_moonset_response_does_not_crash(self) -> None:
        payload = _panchang_response_payload()
        payload["moonrise"] = {
            "event": "moonrise",
            "local_time": None,
            "utc_datetime": None,
            "timezone_offset": 5.5,
        }
        payload["moonset"] = {
            "event": "moonset",
            "local_time": None,
            "utc_datetime": None,
            "timezone_offset": 5.5,
        }

        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            return_value=payload,
        ):
            response = get_panchang(
                PanchangRequest(
                    year=1985,
                    month=4,
                    day=20,
                    latitude=26.2389,
                    longitude=73.0243,
                )
            )

        self.assertIsNone(response.moonrise.local_time)
        self.assertIsNone(response.moonrise.utc_datetime)
        self.assertIsNone(response.moonset.local_time)
        self.assertIsNone(response.moonset.utc_datetime)

    def test_invalid_month_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=1985,
                month=13,
                day=20,
                latitude=26.2389,
                longitude=73.0243,
            )

    def test_invalid_timezone_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=1985,
                month=4,
                day=20,
                timezone_offset=-13,
                latitude=26.2389,
                longitude=73.0243,
            )

    def test_invalid_latitude_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=1985,
                month=4,
                day=20,
                latitude=91.0,
                longitude=73.0243,
            )

    def test_invalid_longitude_returns_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=1985,
                month=4,
                day=20,
                latitude=26.2389,
                longitude=181.0,
            )

    def test_health_endpoint_still_works(self) -> None:
        self.assertEqual(health_check()["status"], "ok")

    def test_calculation_value_error_returns_clear_error_response(self) -> None:
        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            side_effect=ValueError("Invalid local date components"),
        ):
            with self.assertRaises(HTTPException) as exc_info:
                get_panchang(
                    PanchangRequest(
                        year=1985,
                        month=4,
                        day=20,
                        latitude=26.2389,
                        longitude=73.0243,
                    )
                )

        self.assertEqual(exc_info.exception.status_code, 400)
        self.assertEqual(exc_info.exception.detail, "Invalid local date components")

    def test_jodhpur_example_response_matches_current_route_output(self) -> None:
        request_data = _read_json("docs/examples/panchang_request_jodhpur.json")
        expected_response = _read_json("docs/examples/panchang_response_jodhpur.json")
        request = PanchangRequest(**request_data)

        actual_response = get_panchang(request).model_dump(mode="json")

        self.assertEqual(actual_response, expected_response)


def _read_json(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _planet_summary(planet: str, sidereal_longitude: float) -> dict[str, object]:
    return {
        "planet": planet,
        "tropical_longitude": sidereal_longitude + 24.0,
        "sidereal_longitude": sidereal_longitude,
        "rashi_index": 1,
        "rashi_name_hi": "वृषभ",
        "degree_in_rashi": 10.0,
        "dms": {"degrees": 10, "minutes": 0, "seconds": 0.0},
        "speed": 1.0,
        "retrograde": False,
    }


def _panchang_response_payload() -> dict[str, object]:
    return {
        "julian_day": {
            "utc_datetime": "1985-04-20T12:40:00+00:00",
            "julian_day_ut": 2446176.027777,
        },
        "ayanamsa": {"value": 23.72},
        "sun": _planet_summary("sun", 6.73),
        "moon": _planet_summary("moon", 36.28),
        "tithi": {
            "tithi_number": 3,
            "name_en": "Tritiya",
            "name_hi": "तृतीया",
            "name_sa": "Tritiya",
            "paksha": "Shukla",
            "start_angle": 24.0,
            "end_angle": 36.0,
            "current_angle": 29.55,
            "degrees_completed": 5.55,
            "degrees_remaining": 6.45,
            "end_time_local": "1985-04-20T23:30:00+05:30",
            "end_time_utc": "1985-04-20T18:00:00Z",
        },
        "nakshatra": {
            "index": 2,
            "name_en": "Krittika",
            "name_hi": "कृत्तिका",
            "name_sa": "Krittika",
            "pada": 3,
            "ruling_planet": "sun",
            "start_degree": 26.6666666667,
            "end_degree": 40.0,
            "degree_within_nakshatra": 9.613333,
            "current_degree": 36.28,
            "degrees_remaining": 3.72,
            "end_time_local": "1985-04-21T01:30:00+05:30",
            "end_time_utc": "1985-04-20T20:00:00Z",
        },
        "yoga": {
            "yoga_index": 4,
            "name_en": "Saubhagya",
            "name_hi": "सौभाग्य",
            "name_sa": "Saubhagya",
            "start_degree": 40.0,
            "end_degree": 53.3333333333,
            "current_degree": 43.01,
            "degrees_completed": 3.01,
            "degrees_remaining": 10.323333,
        },
        "karana": {
            "karana_index": 5,
            "name_en": "Gara",
            "name_hi": "गर",
            "name_sa": "Gara",
            "type": "Repeating",
            "half_tithi_index": 4,
            "current_angle": 29.55,
            "start_angle": 24.0,
            "end_angle": 30.0,
            "degrees_completed": 5.55,
            "degrees_remaining": 0.45,
        },
        "vara": {
            "index": 7,
            "name_en": "Saturday",
            "name_hi": "शनिवार",
            "name_sa": "Shanivara",
            "ruling_planet": "saturn",
        },
        "sunrise": {
            "event": "sunrise",
            "local_time": "06:12:34",
            "utc_datetime": "1985-04-20T00:42:34Z",
            "timezone_offset": 5.5,
        },
        "sunset": {
            "event": "sunset",
            "local_time": "18:59:01",
            "utc_datetime": "1985-04-20T13:29:01Z",
            "timezone_offset": 5.5,
        },
        "moonrise": {
            "event": "moonrise",
            "local_time": "06:38:42",
            "utc_datetime": "1985-04-20T01:08:42Z",
            "timezone_offset": 5.5,
        },
        "moonset": {
            "event": "moonset",
            "local_time": "19:54:56",
            "utc_datetime": "1985-04-20T14:24:56Z",
            "timezone_offset": 5.5,
        },
    }


if __name__ == "__main__":
    unittest.main()
