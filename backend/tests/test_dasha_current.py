"""Tests for current Dasha lookup helpers."""

from __future__ import annotations

from datetime import datetime
import unittest

from backend.app.dasha.current import (
    find_period_at_datetime,
    get_current_dasha,
)


class CurrentDashaLookupTest(unittest.TestCase):
    """Validate current Dasha lookup behavior."""

    def test_target_inside_mahadasha_returns_correct_mahadasha(self) -> None:
        result = get_current_dasha(
            mahadasha_timeline=_nested_timeline(),
            target_datetime=datetime(2005, 1, 1),
        )

        self.assertEqual(result["target_datetime"], "2005-01-01T00:00:00")
        self.assertIsNotNone(result["mahadasha"])
        self.assertEqual(result["mahadasha"]["dasha_lord"], "venus")
        self.assertIsNotNone(result["antardasha"])
        self.assertEqual(result["antardasha"]["antardasha_lord"], "venus")
        self.assertIsNotNone(result["pratyantardasha"])
        self.assertEqual(
            result["pratyantardasha"]["pratyantardasha_lord"],
            "venus",
        )

    def test_target_on_start_boundary_works(self) -> None:
        period = find_period_at_datetime(
            periods=_simple_timeline(),
            target_datetime="2000-01-01T00:00:00",
        )

        self.assertIsNotNone(period)
        self.assertEqual(period["dasha_lord"], "venus")

    def test_target_on_end_boundary_moves_to_next_period(self) -> None:
        period = find_period_at_datetime(
            periods=_simple_timeline(),
            target_datetime="2020-01-01T00:00:00",
        )

        self.assertIsNotNone(period)
        self.assertEqual(period["dasha_lord"], "sun")

    def test_missing_antardasha_data_is_handled_safely(self) -> None:
        result = get_current_dasha(
            mahadasha_timeline=_simple_timeline(),
            target_datetime=datetime(2005, 1, 1),
        )

        self.assertIsNotNone(result["mahadasha"])
        self.assertEqual(result["mahadasha"]["dasha_lord"], "venus")
        self.assertIsNone(result["antardasha"])
        self.assertIsNone(result["pratyantardasha"])

    def test_target_outside_timeline_is_handled_safely(self) -> None:
        result = get_current_dasha(
            mahadasha_timeline=_simple_timeline(),
            target_datetime=datetime(1999, 12, 31, 23, 59, 59),
        )

        self.assertEqual(result["target_datetime"], "1999-12-31T23:59:59")
        self.assertIsNone(result["mahadasha"])
        self.assertIsNone(result["antardasha"])
        self.assertIsNone(result["pratyantardasha"])

    def test_include_flags_skip_nested_lookup(self) -> None:
        result = get_current_dasha(
            mahadasha_timeline=_nested_timeline(),
            target_datetime=datetime(2005, 1, 1),
            include_antardasha=False,
            include_pratyantardasha=True,
        )

        self.assertIsNotNone(result["mahadasha"])
        self.assertIsNone(result["antardasha"])
        self.assertIsNone(result["pratyantardasha"])


def _simple_timeline() -> list[dict[str, object]]:
    return [
        {
            "dasha_lord": "venus",
            "start_datetime": "2000-01-01T00:00:00",
            "end_datetime": "2020-01-01T00:00:00",
            "duration_years": 20.0,
            "is_birth_dasha": False,
        },
        {
            "dasha_lord": "sun",
            "start_datetime": "2020-01-01T00:00:00",
            "end_datetime": "2026-01-01T00:00:00",
            "duration_years": 6.0,
            "is_birth_dasha": False,
        },
    ]


def _nested_timeline() -> list[dict[str, object]]:
    timeline = _simple_timeline()
    timeline[0]["antardashas"] = [
        {
            "mahadasha_lord": "venus",
            "antardasha_lord": "venus",
            "start_datetime": "2000-01-01T00:00:00",
            "end_datetime": "2010-01-01T00:00:00",
            "duration_years": 10.0,
            "pratyantardashas": [
                {
                    "mahadasha_lord": "venus",
                    "antardasha_lord": "venus",
                    "pratyantardasha_lord": "venus",
                    "start_datetime": "2000-01-01T00:00:00",
                    "end_datetime": "2006-01-01T00:00:00",
                    "duration_years": 6.0,
                },
                {
                    "mahadasha_lord": "venus",
                    "antardasha_lord": "venus",
                    "pratyantardasha_lord": "sun",
                    "start_datetime": "2006-01-01T00:00:00",
                    "end_datetime": "2010-01-01T00:00:00",
                    "duration_years": 4.0,
                },
            ],
        },
        {
            "mahadasha_lord": "venus",
            "antardasha_lord": "sun",
            "start_datetime": "2010-01-01T00:00:00",
            "end_datetime": "2020-01-01T00:00:00",
            "duration_years": 10.0,
        },
    ]
    return timeline


if __name__ == "__main__":
    unittest.main()
