"""Tests for Pratyantardasha generation."""

from __future__ import annotations

from datetime import datetime
import unittest

from backend.app.dasha.pratyantardasha import generate_pratyantardasha_periods


class PratyantardashaPeriodTest(unittest.TestCase):
    """Validate Pratyantardasha period generation."""

    def test_pratyantardasha_starts_from_antardasha_lord(self) -> None:
        periods = _venus_sun_pratyantardasha_periods()

        self.assertEqual(periods[0]["mahadasha_lord"], "venus")
        self.assertEqual(periods[0]["antardasha_lord"], "sun")
        self.assertEqual(periods[0]["pratyantardasha_lord"], "sun")
        self.assertEqual(periods[0]["start_datetime"], "2000-01-01T00:00:00")

    def test_pratyantardasha_sequence_follows_vimshottari_order(self) -> None:
        periods = _venus_sun_pratyantardasha_periods()

        self.assertEqual(
            tuple(period["pratyantardasha_lord"] for period in periods),
            (
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
                "ketu",
                "venus",
            ),
        )

    def test_pratyantardasha_durations_use_vimshottari_formula(self) -> None:
        periods = _venus_sun_pratyantardasha_periods()

        self.assertEqual(periods[0]["duration_years"], 0.05)
        self.assertEqual(periods[1]["duration_years"], 0.083333)
        self.assertEqual(periods[2]["duration_years"], 0.058333)

    def test_pratyantardasha_periods_stay_within_antardasha_bounds(self) -> None:
        periods = _venus_sun_pratyantardasha_periods()

        self.assertEqual(periods[0]["start_datetime"], "2000-01-01T00:00:00")
        self.assertEqual(periods[-1]["end_datetime"], "2001-01-01T00:00:00")
        for previous, current in zip(periods, periods[1:]):
            self.assertEqual(previous["end_datetime"], current["start_datetime"])

    def test_pratyantardasha_preserves_timezone_offset(self) -> None:
        periods = generate_pratyantardasha_periods(
            mahadasha_lord="venus",
            antardasha_lord="sun",
            antardasha_start="2000-01-01T00:00:00+05:30",
            antardasha_end="2001-01-01T00:00:00+05:30",
            antardasha_duration_years=1.0,
        )

        self.assertTrue(periods[0]["start_datetime"].endswith("+05:30"))
        self.assertTrue(periods[-1]["end_datetime"].endswith("+05:30"))

    def test_invalid_pratyantardasha_input_fails_safely(self) -> None:
        with self.assertRaises(ValueError):
            generate_pratyantardasha_periods(
                mahadasha_lord="earth",
                antardasha_lord="sun",
                antardasha_start=datetime(2000, 1, 1),
                antardasha_end=datetime(2001, 1, 1),
                antardasha_duration_years=1.0,
            )

        with self.assertRaises(ValueError):
            generate_pratyantardasha_periods(
                mahadasha_lord="venus",
                antardasha_lord="earth",
                antardasha_start=datetime(2000, 1, 1),
                antardasha_end=datetime(2001, 1, 1),
                antardasha_duration_years=1.0,
            )

        with self.assertRaises(ValueError):
            generate_pratyantardasha_periods(
                mahadasha_lord="venus",
                antardasha_lord="sun",
                antardasha_start=datetime(2001, 1, 1),
                antardasha_end=datetime(2000, 1, 1),
                antardasha_duration_years=1.0,
            )

        with self.assertRaises(ValueError):
            generate_pratyantardasha_periods(
                mahadasha_lord="venus",
                antardasha_lord="sun",
                antardasha_start=datetime(2000, 1, 1),
                antardasha_end=datetime(2001, 1, 1),
                antardasha_duration_years=0.0,
            )

        with self.assertRaises(TypeError):
            generate_pratyantardasha_periods(
                mahadasha_lord="venus",
                antardasha_lord="sun",
                antardasha_start=123,  # type: ignore[arg-type]
                antardasha_end=datetime(2001, 1, 1),
                antardasha_duration_years=1.0,
            )


def _venus_sun_pratyantardasha_periods() -> list[dict[str, object]]:
    return generate_pratyantardasha_periods(
        mahadasha_lord="Venus",
        antardasha_lord="Sun",
        antardasha_start=datetime(2000, 1, 1),
        antardasha_end=datetime(2001, 1, 1),
        antardasha_duration_years=1.0,
    )


if __name__ == "__main__":
    unittest.main()
