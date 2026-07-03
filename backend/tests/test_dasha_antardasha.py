"""Tests for Antardasha generation."""

from __future__ import annotations

from datetime import datetime
import unittest

from backend.app.dasha.antardasha import generate_antardasha_periods


class AntardashaPeriodTest(unittest.TestCase):
    """Validate Antardasha period generation."""

    def test_antardasha_starts_from_mahadasha_lord(self) -> None:
        periods = _venus_antardasha_periods()

        self.assertEqual(periods[0]["mahadasha_lord"], "venus")
        self.assertEqual(periods[0]["antardasha_lord"], "venus")
        self.assertEqual(periods[0]["start_datetime"], "2000-01-01T00:00:00")

    def test_antardasha_sequence_follows_vimshottari_order(self) -> None:
        periods = _venus_antardasha_periods()

        self.assertEqual(
            tuple(period["antardasha_lord"] for period in periods),
            (
                "venus",
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
                "ketu",
            ),
        )

    def test_antardasha_durations_use_vimshottari_formula(self) -> None:
        periods = _venus_antardasha_periods()

        self.assertEqual(periods[0]["duration_years"], 3.333333)
        self.assertEqual(periods[1]["duration_years"], 1.0)
        self.assertEqual(periods[2]["duration_years"], 1.666667)

    def test_antardasha_periods_stay_within_mahadasha_bounds(self) -> None:
        periods = _venus_antardasha_periods()

        self.assertEqual(periods[0]["start_datetime"], "2000-01-01T00:00:00")
        self.assertEqual(periods[-1]["end_datetime"], "2020-01-01T00:00:00")
        for previous, current in zip(periods, periods[1:]):
            self.assertEqual(previous["end_datetime"], current["start_datetime"])

    def test_antardasha_preserves_timezone_offset(self) -> None:
        periods = generate_antardasha_periods(
            mahadasha_lord="venus",
            mahadasha_start="2000-01-01T00:00:00+05:30",
            mahadasha_end="2020-01-01T00:00:00+05:30",
            mahadasha_duration_years=20.0,
        )

        self.assertTrue(periods[0]["start_datetime"].endswith("+05:30"))
        self.assertTrue(periods[-1]["end_datetime"].endswith("+05:30"))

    def test_invalid_antardasha_input_fails_safely(self) -> None:
        with self.assertRaises(ValueError):
            generate_antardasha_periods(
                mahadasha_lord="earth",
                mahadasha_start=datetime(2000, 1, 1),
                mahadasha_end=datetime(2020, 1, 1),
                mahadasha_duration_years=20.0,
            )

        with self.assertRaises(ValueError):
            generate_antardasha_periods(
                mahadasha_lord="venus",
                mahadasha_start=datetime(2020, 1, 1),
                mahadasha_end=datetime(2000, 1, 1),
                mahadasha_duration_years=20.0,
            )

        with self.assertRaises(ValueError):
            generate_antardasha_periods(
                mahadasha_lord="venus",
                mahadasha_start=datetime(2000, 1, 1),
                mahadasha_end=datetime(2020, 1, 1),
                mahadasha_duration_years=0.0,
            )

        with self.assertRaises(TypeError):
            generate_antardasha_periods(
                mahadasha_lord="venus",
                mahadasha_start=123,  # type: ignore[arg-type]
                mahadasha_end=datetime(2020, 1, 1),
                mahadasha_duration_years=20.0,
            )


def _venus_antardasha_periods() -> list[dict[str, object]]:
    return generate_antardasha_periods(
        mahadasha_lord="Venus",
        mahadasha_start=datetime(2000, 1, 1),
        mahadasha_end=datetime(2020, 1, 1),
        mahadasha_duration_years=20.0,
    )


if __name__ == "__main__":
    unittest.main()
