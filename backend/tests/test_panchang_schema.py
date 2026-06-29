"""Tests for Panchang Pydantic schemas."""

from __future__ import annotations

import unittest

try:
    from pydantic import ValidationError

    from backend.app.schemas.panchang import PanchangRequest, PanchangResponse
except ModuleNotFoundError:
    ValidationError = None  # type: ignore[assignment]
    PanchangRequest = None  # type: ignore[assignment]
    PanchangResponse = None  # type: ignore[assignment]


@unittest.skipIf(PanchangRequest is None, "pydantic is not installed")
class PanchangRequestSchemaTest(unittest.TestCase):
    """Validate Panchang request schema constraints."""

    def test_valid_request_passes(self) -> None:
        request = PanchangRequest(
            year=2026,
            month=6,
            day=29,
            hour=10,
            minute=30,
            second=15,
            timezone_offset=5.5,
            latitude=26.2389,
            longitude=73.0243,
            language="hi",
            ayanamsa="lahiri",
        )

        self.assertEqual(request.year, 2026)
        self.assertEqual(request.latitude, 26.2389)
        self.assertEqual(request.longitude, 73.0243)
        self.assertEqual(request.language, "hi")
        self.assertEqual(request.ayanamsa, "lahiri")

    def test_invalid_month_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=13,
                day=29,
                latitude=26.2389,
                longitude=73.0243,
            )

    def test_invalid_hour_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=6,
                day=29,
                hour=24,
                latitude=26.2389,
                longitude=73.0243,
            )

    def test_invalid_timezone_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=6,
                day=29,
                timezone_offset=-13,
                latitude=26.2389,
                longitude=73.0243,
            )

    def test_invalid_latitude_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=6,
                day=29,
                latitude=91.0,
                longitude=73.0243,
            )

    def test_invalid_longitude_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=6,
                day=29,
                latitude=26.2389,
                longitude=181.0,
            )

    def test_default_values_work(self) -> None:
        request = PanchangRequest(
            year=2026,
            month=6,
            day=29,
            latitude=26.2389,
            longitude=73.0243,
        )

        self.assertEqual(request.hour, 12)
        self.assertEqual(request.minute, 0)
        self.assertEqual(request.second, 0)
        self.assertEqual(request.timezone_offset, 5.5)
        self.assertEqual(request.language, "hi")
        self.assertEqual(request.ayanamsa, "lahiri")

    def test_invalid_language_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=6,
                day=29,
                latitude=26.2389,
                longitude=73.0243,
                language="sa",
            )

    def test_invalid_ayanamsa_fails(self) -> None:
        with self.assertRaises(ValidationError):
            PanchangRequest(
                year=2026,
                month=6,
                day=29,
                latitude=26.2389,
                longitude=73.0243,
                ayanamsa="raman",
            )


@unittest.skipIf(PanchangResponse is None, "pydantic is not installed")
class PanchangResponseSchemaTest(unittest.TestCase):
    """Validate Panchang response schema compatibility."""

    def test_response_model_accepts_aggregator_output(self) -> None:
        response = PanchangResponse(**_aggregator_output())

        self.assertEqual(response.julian_day.julian_day_ut, 2460123.5)
        self.assertEqual(response.sun.planet, "sun")
        self.assertEqual(response.moon.sidereal_longitude, 40.0)
        self.assertEqual(response.tithi.tithi_number, 3)
        self.assertEqual(response.nakshatra.name_en, "Rohini")
        self.assertEqual(response.yoga.yoga_index, 4)
        self.assertEqual(response.karana.name_en, "Gara")
        self.assertEqual(response.vara.name_en, "Monday")
        self.assertEqual(response.sunrise.event, "sunrise")
        self.assertEqual(response.sunset.event, "sunset")


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


def _aggregator_output() -> dict[str, object]:
    return {
        "julian_day": {
            "utc_datetime": "2026-06-29T06:30:00+00:00",
            "julian_day_ut": 2460123.5,
        },
        "ayanamsa": {"value": 24.1234},
        "sun": _planet_summary("sun", 10.0),
        "moon": _planet_summary("moon", 40.0),
        "tithi": {
            "tithi_number": 3,
            "name_en": "Tritiya",
            "name_hi": "तृतीया",
            "name_sa": "Tritiya",
            "paksha": "Shukla",
            "start_angle": 24.0,
            "end_angle": 36.0,
            "current_angle": 30.0,
            "degrees_completed": 6.0,
            "degrees_remaining": 6.0,
        },
        "nakshatra": {
            "index": 3,
            "name_en": "Rohini",
            "name_hi": "रोहिणी",
            "name_sa": "Rohini",
            "pada": 1,
            "ruling_planet": "moon",
            "start_degree": 40.0,
            "end_degree": 53.3333333333,
            "degree_within_nakshatra": 0.0,
        },
        "yoga": {
            "yoga_index": 4,
            "name_en": "Saubhagya",
            "name_hi": "सौभाग्य",
            "name_sa": "Saubhagya",
            "start_degree": 40.0,
            "end_degree": 53.3333333333,
            "current_degree": 50.0,
            "degrees_completed": 10.0,
            "degrees_remaining": 3.333333,
        },
        "karana": {
            "karana_index": 5,
            "name_en": "Gara",
            "name_hi": "गर",
            "name_sa": "Gara",
            "type": "Repeating",
            "half_tithi_index": 5,
            "current_angle": 30.0,
            "start_angle": 30.0,
            "end_angle": 36.0,
            "degrees_completed": 0.0,
            "degrees_remaining": 6.0,
        },
        "vara": {
            "index": 2,
            "name_en": "Monday",
            "name_hi": "सोमवार",
            "name_sa": "Somavara",
            "ruling_planet": "moon",
        },
        "sunrise": {
            "event": "sunrise",
            "local_time": "05:49:24",
            "utc_datetime": "2026-06-29T00:19:24Z",
            "timezone_offset": 5.5,
        },
        "sunset": {
            "event": "sunset",
            "local_time": "19:31:49",
            "utc_datetime": "2026-06-29T14:01:49Z",
            "timezone_offset": 5.5,
        },
    }


if __name__ == "__main__":
    unittest.main()
