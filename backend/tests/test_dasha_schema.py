"""Tests for Dasha Pydantic schemas."""

from __future__ import annotations

import json
import unittest

try:
    from pydantic import ValidationError

    from backend.app.schemas.dasha import DashaRequest, DashaResponse
except ModuleNotFoundError:
    ValidationError = None  # type: ignore[assignment]
    DashaRequest = None  # type: ignore[assignment]
    DashaResponse = None  # type: ignore[assignment]


@unittest.skipIf(DashaRequest is None, "pydantic is not installed")
class DashaRequestSchemaTest(unittest.TestCase):
    """Validate Dasha request schema constraints."""

    def test_valid_request_passes(self) -> None:
        request = DashaRequest(
            date="2000-01-01",
            time="12:30:15",
            timezone_offset=5.5,
            latitude=26.9124,
            longitude=75.7873,
            ayanamsa="lahiri",
        )

        self.assertEqual(request.date.isoformat(), "2000-01-01")
        self.assertEqual(request.time.isoformat(), "12:30:15")
        self.assertEqual(request.timezone_offset, 5.5)
        self.assertEqual(request.latitude, 26.9124)
        self.assertEqual(request.longitude, 75.7873)
        self.assertEqual(request.ayanamsa, "lahiri")

    def test_default_include_flags_work(self) -> None:
        request = DashaRequest(
            date="2000-01-01",
            latitude=26.9124,
            longitude=75.7873,
        )

        self.assertTrue(request.include_antardasha)
        self.assertFalse(request.include_pratyantardasha)
        self.assertEqual(request.time.isoformat(), "12:00:00")
        self.assertEqual(request.timezone_offset, 5.5)

    def test_optional_target_datetime_passes(self) -> None:
        request = DashaRequest(
            date="2000-01-01",
            time="12:00:00",
            latitude=26.9124,
            longitude=75.7873,
            target_datetime="2026-07-03T10:15:00",
            target_date="2026-07-03",
        )

        self.assertEqual(
            request.target_datetime.isoformat(),
            "2026-07-03T10:15:00",
        )
        self.assertEqual(request.target_date.isoformat(), "2026-07-03")

    def test_invalid_latitude_and_longitude_fail(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=91.0,
                longitude=75.7873,
            )

        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=26.9124,
                longitude=181.0,
            )

    def test_invalid_date_and_time_fail(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest(
                date="not-a-date",
                latitude=26.9124,
                longitude=75.7873,
            )

        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                time="25:00:00",
                latitude=26.9124,
                longitude=75.7873,
            )

    def test_invalid_timezone_fails(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                timezone_offset=-13.0,
                latitude=26.9124,
                longitude=75.7873,
            )

    def test_missing_required_fields_fail(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest()

        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=26.9124,
            )

    def test_invalid_target_date_and_datetime_fail(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=26.9124,
                longitude=75.7873,
                target_date="not-a-date",
            )

        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=26.9124,
                longitude=75.7873,
                target_datetime="not-a-datetime",
            )

    def test_invalid_include_flags_fail_for_unparseable_values(self) -> None:
        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=26.9124,
                longitude=75.7873,
                include_antardasha="not-a-bool",
            )

        with self.assertRaises(ValidationError):
            DashaRequest(
                date="2000-01-01",
                latitude=26.9124,
                longitude=75.7873,
                include_pratyantardasha="not-a-bool",
            )


@unittest.skipIf(DashaResponse is None, "pydantic is not installed")
class DashaResponseSchemaTest(unittest.TestCase):
    """Validate Dasha response schema compatibility."""

    def test_response_model_json_serialization(self) -> None:
        response = DashaResponse(**_dasha_response_payload())
        data = response.model_dump(mode="json")

        self.assertEqual(data["birth_datetime"], "2000-01-01T00:00:00")
        self.assertEqual(data["target_datetime"], "2000-01-01T00:00:00")
        self.assertEqual(data["metadata"]["engine"], "dasha")
        self.assertEqual(data["metadata"]["system"], "vimshottari")
        self.assertEqual(data["mahadasha_timeline"][0]["dasha_lord"], "ketu")
        self.assertEqual(
            data["mahadasha_timeline"][0]["antardashas"][0]["antardasha_lord"],
            "ketu",
        )
        self.assertEqual(
            data["current_dasha"]["pratyantardasha"]["pratyantardasha_lord"],
            "ketu",
        )
        json.dumps(data)

    def test_response_rejects_extra_keys(self) -> None:
        payload = _dasha_response_payload()
        payload["metadata"]["version"] = "v1"

        with self.assertRaises(ValidationError):
            DashaResponse(**payload)


def _dasha_response_payload() -> dict[str, object]:
    pratyantardasha = {
        "mahadasha_lord": "ketu",
        "antardasha_lord": "ketu",
        "pratyantardasha_lord": "ketu",
        "start_datetime": "2000-01-01T00:00:00",
        "end_datetime": "2000-02-01T00:00:00",
        "duration_years": 0.408333,
    }
    antardasha = {
        "mahadasha_lord": "ketu",
        "antardasha_lord": "ketu",
        "start_datetime": "2000-01-01T00:00:00",
        "end_datetime": "2000-06-01T00:00:00",
        "duration_years": 0.408333,
        "pratyantardashas": [pratyantardasha],
    }
    mahadasha = {
        "dasha_lord": "ketu",
        "start_datetime": "2000-01-01T00:00:00",
        "end_datetime": "2007-01-01T00:00:00",
        "duration_years": 7.0,
        "is_birth_dasha": True,
        "antardashas": [antardasha],
    }
    return {
        "birth_datetime": "2000-01-01T00:00:00",
        "target_datetime": "2000-01-01T00:00:00",
        "mahadasha_timeline": [mahadasha],
        "current_dasha": {
            "target_datetime": "2000-01-01T00:00:00",
            "mahadasha": mahadasha,
            "antardasha": antardasha,
            "pratyantardasha": pratyantardasha,
        },
        "metadata": {
            "engine": "dasha",
            "system": "vimshottari",
        },
    }


if __name__ == "__main__":
    unittest.main()
