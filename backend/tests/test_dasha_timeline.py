"""Tests for Mahadasha timeline generation."""

from __future__ import annotations

from datetime import datetime
import unittest

from backend.app.constants.nakshatra import NAKSHATRA_SPAN_DEGREES
from backend.app.dasha.timeline import generate_mahadasha_timeline


class MahadashaTimelineTest(unittest.TestCase):
    """Validate Mahadasha timeline generation."""

    def test_timeline_starts_with_birth_dasha_lord(self) -> None:
        timeline = generate_mahadasha_timeline(
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0),
            nakshatra_index=0,
            moon_longitude=NAKSHATRA_SPAN_DEGREES / 2.0,
        )

        first = timeline[0]
        self.assertEqual(first["dasha_lord"], "ketu")
        self.assertEqual(first["start_datetime"], "2000-01-01T12:00:00")
        self.assertTrue(first["is_birth_dasha"])

    def test_first_period_uses_birth_balance_years(self) -> None:
        timeline = generate_mahadasha_timeline(
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0),
            nakshatra_index=0,
            moon_longitude=NAKSHATRA_SPAN_DEGREES / 2.0,
        )

        self.assertEqual(timeline[0]["duration_years"], 3.5)

    def test_subsequent_periods_use_full_mahadasha_durations(self) -> None:
        timeline = generate_mahadasha_timeline(
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0),
            nakshatra_index=0,
            moon_longitude=NAKSHATRA_SPAN_DEGREES / 2.0,
        )

        self.assertEqual(timeline[1]["dasha_lord"], "venus")
        self.assertEqual(timeline[1]["duration_years"], 20.0)
        self.assertFalse(timeline[1]["is_birth_dasha"])
        self.assertEqual(timeline[2]["dasha_lord"], "sun")
        self.assertEqual(timeline[2]["duration_years"], 6.0)

    def test_timeline_covers_at_least_120_years(self) -> None:
        timeline = generate_mahadasha_timeline(
            birth_datetime=datetime(2000, 1, 1, 12, 0, 0),
            nakshatra_index=0,
            moon_longitude=NAKSHATRA_SPAN_DEGREES / 2.0,
        )
        total_years = sum(period["duration_years"] for period in timeline)

        self.assertGreaterEqual(total_years, 120.0)
        self.assertLessEqual(total_years, 127.0)
        self.assertEqual(timeline[-1]["dasha_lord"], "ketu")

    def test_timeline_preserves_timezone_offset_from_birth_datetime(self) -> None:
        timeline = generate_mahadasha_timeline(
            birth_datetime="2000-01-01T12:00:00+05:30",
            nakshatra_index=0,
            moon_longitude=0.0,
        )

        self.assertEqual(timeline[0]["start_datetime"], "2000-01-01T12:00:00+05:30")
        self.assertTrue(timeline[0]["end_datetime"].endswith("+05:30"))

    def test_invalid_input_fails_safely(self) -> None:
        with self.assertRaises(TypeError):
            generate_mahadasha_timeline(
                birth_datetime=123,  # type: ignore[arg-type]
                nakshatra_index=0,
                moon_longitude=0.0,
            )

        with self.assertRaises(ValueError):
            generate_mahadasha_timeline(
                birth_datetime="not-a-date",
                nakshatra_index=0,
                moon_longitude=0.0,
            )

        with self.assertRaises(ValueError):
            generate_mahadasha_timeline(
                birth_datetime=datetime(2000, 1, 1, 12, 0, 0),
                nakshatra_index=27,
                moon_longitude=0.0,
            )

        with self.assertRaises(ValueError):
            generate_mahadasha_timeline(
                birth_datetime=datetime(2000, 1, 1, 12, 0, 0),
                nakshatra_index=0,
                moon_longitude=float("nan"),
            )


if __name__ == "__main__":
    unittest.main()
