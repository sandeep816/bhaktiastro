"""Integration tests for the Panchang API route."""

from __future__ import annotations

import unittest
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient

    from backend.app.main import app
except ModuleNotFoundError:
    TestClient = None  # type: ignore[assignment]
    app = None  # type: ignore[assignment]


@unittest.skipIf(TestClient is None, "fastapi is not installed")
class PanchangApiTest(unittest.TestCase):
    """Validate Panchang API behavior."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_post_panchang_returns_200_for_valid_jodhpur_ist_input(self) -> None:
        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            return_value=_panchang_response_payload(),
        ) as calculate_basic_panchang:
            response = self.client.post(
                "/api/v1/panchang",
                json={
                    "year": 1985,
                    "month": 4,
                    "day": 20,
                    "hour": 18,
                    "minute": 10,
                    "second": 0,
                    "timezone_offset": 5.5,
                    "language": "hi",
                    "ayanamsa": "lahiri",
                },
            )

        self.assertEqual(response.status_code, 200)
        calculate_basic_panchang.assert_called_once_with(
            year=1985,
            month=4,
            day=20,
            hour=18,
            minute=10,
            second=0,
            timezone_offset=5.5,
        )

    def test_response_contains_panchang_sections(self) -> None:
        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            return_value=_panchang_response_payload(),
        ):
            response = self.client.post(
                "/api/v1/panchang",
                json={"year": 1985, "month": 4, "day": 20},
            )

        data = response.json()
        for key in ("tithi", "nakshatra", "yoga", "karana", "vara"):
            self.assertIn(key, data)

    def test_invalid_month_returns_validation_error(self) -> None:
        response = self.client.post(
            "/api/v1/panchang",
            json={"year": 1985, "month": 13, "day": 20},
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_timezone_returns_validation_error(self) -> None:
        response = self.client.post(
            "/api/v1/panchang",
            json={"year": 1985, "month": 4, "day": 20, "timezone_offset": -13},
        )

        self.assertEqual(response.status_code, 422)

    def test_health_endpoint_still_works(self) -> None:
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_calculation_value_error_returns_clear_error_response(self) -> None:
        with patch(
            "backend.app.api.v1.panchang.calculate_basic_panchang",
            side_effect=ValueError("Invalid local date components"),
        ):
            response = self.client.post(
                "/api/v1/panchang",
                json={"year": 1985, "month": 4, "day": 20},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid local date components")


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
    }


if __name__ == "__main__":
    unittest.main()
