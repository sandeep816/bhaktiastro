"""Regression tests for Dasha JSON safety and stable structure."""

from __future__ import annotations

from datetime import datetime
import json
import unittest
from unittest.mock import patch

from backend.app.api.v1.dasha import get_dasha
from backend.app.dasha.builder import build_dasha_timeline
from backend.app.schemas.dasha import DashaRequest


class DashaRegressionTest(unittest.TestCase):
    """Validate stable Dasha output shape without fragile ephemeris values."""

    def test_dasha_timeline_output_is_json_serializable(self) -> None:
        result = _jaipur_dasha_timeline()

        data = json.loads(json.dumps(result))

        self.assertEqual(data["metadata"]["engine"], "dasha")
        self.assertEqual(data["metadata"]["system"], "vimshottari")
        self.assertGreater(len(data["mahadasha_timeline"]), 0)
        _assert_period_bounds(self, data["mahadasha_timeline"][0])

    def test_dasha_api_response_is_json_serializable(self) -> None:
        response = _jaipur_dasha_api_response()
        data = response.model_dump(mode="json")

        json.dumps(data)

        self.assertEqual(data["metadata"]["engine"], "dasha")
        self.assertEqual(data["metadata"]["system"], "vimshottari")
        self.assertGreater(len(data["mahadasha_timeline"]), 0)
        self.assertIsNotNone(data["current_dasha"])

    def test_mahadasha_timeline_order_remains_stable(self) -> None:
        result = _jaipur_dasha_timeline()
        timeline = result["mahadasha_timeline"]

        self.assertEqual(
            tuple(period["dasha_lord"] for period in timeline[:9]),
            (
                "ketu",
                "venus",
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
            ),
        )
        for previous, current in zip(timeline, timeline[1:]):
            self.assertEqual(previous["end_datetime"], current["start_datetime"])

    def test_antardasha_sequence_remains_stable(self) -> None:
        result = _jaipur_dasha_timeline()
        antardashas = result["mahadasha_timeline"][0]["antardashas"]

        self.assertEqual(
            tuple(period["antardasha_lord"] for period in antardashas),
            (
                "ketu",
                "venus",
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
            ),
        )
        for period in antardashas:
            _assert_period_bounds(self, period)

    def test_pratyantardasha_sequence_remains_stable(self) -> None:
        result = _jaipur_dasha_timeline()
        pratyantardashas = (
            result["mahadasha_timeline"][0]["antardashas"][0]["pratyantardashas"]
        )

        self.assertEqual(
            tuple(period["pratyantardasha_lord"] for period in pratyantardashas),
            (
                "ketu",
                "venus",
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
            ),
        )
        for period in pratyantardashas:
            _assert_period_bounds(self, period)

    def test_current_dasha_lookup_remains_stable_for_fixed_sample(self) -> None:
        result = _jaipur_dasha_timeline()
        current_dasha = result["current_dasha"]

        self.assertIsNotNone(current_dasha)
        self.assertEqual(
            current_dasha["target_datetime"],
            "2026-07-03T12:00:00+05:30",
        )
        self.assertIsNotNone(current_dasha["mahadasha"])
        self.assertIsNotNone(current_dasha["antardasha"])
        self.assertIsNotNone(current_dasha["pratyantardasha"])
        self.assertEqual(current_dasha["mahadasha"]["dasha_lord"], "moon")
        self.assertIn(
            current_dasha["antardasha"]["antardasha_lord"],
            {
                "ketu",
                "venus",
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
            },
        )


def _jaipur_dasha_timeline() -> dict[str, object]:
    return build_dasha_timeline(
        birth_datetime="1990-01-01T12:00:00+05:30",
        nakshatra_index=0,
        moon_longitude=0.0,
        target_datetime="2026-07-03T12:00:00+05:30",
        include_antardasha=True,
        include_pratyantardasha=True,
    )


def _jaipur_dasha_api_response() -> object:
    with patch(
        "backend.app.api.v1.dasha.calculate_basic_panchang",
        return_value=_panchang_birth_payload(),
    ):
        return get_dasha(
            DashaRequest(
                date="1990-01-01",
                time="12:00:00",
                timezone_offset=5.5,
                latitude=26.9124,
                longitude=75.7873,
                target_datetime="2026-07-03T12:00:00",
                include_antardasha=True,
                include_pratyantardasha=True,
            )
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


def _assert_period_bounds(
    test_case: unittest.TestCase,
    period: dict[str, object],
) -> None:
    test_case.assertIn("start_datetime", period)
    test_case.assertIn("end_datetime", period)
    start_datetime = datetime.fromisoformat(str(period["start_datetime"]))
    end_datetime = datetime.fromisoformat(str(period["end_datetime"]))
    test_case.assertLessEqual(start_datetime, end_datetime)


if __name__ == "__main__":
    unittest.main()
