"""Tests for deterministic Panchang Yoga lookup."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from backend.app.astrology import yoga
from backend.app.astrology.yoga import (
    get_panchang_yoga,
    get_panchang_yoga_with_boundary,
)


class PanchangYogaLookupTest(unittest.TestCase):
    """Validate Panchang Yoga lookup and degree boundaries."""

    def test_zero_degree_total_is_vishkambha(self) -> None:
        result = get_panchang_yoga(0.0, 0.0)

        self.assertEqual(result["yoga_index"], 1)
        self.assertEqual(result["name_en"], "Vishkambha")
        self.assertEqual(result["name_hi"], "विष्कम्भ")
        self.assertEqual(result["name_sa"], "Vishkambha")
        self.assertEqual(result["current_degree"], 0.0)
        self.assertEqual(result["degrees_completed"], 0.0)
        self.assertEqual(result["degrees_remaining"], 13.333333)

    def test_boundary_starts_second_yoga(self) -> None:
        result = get_panchang_yoga(0.0, 13.333333)

        self.assertEqual(result["yoga_index"], 2)
        self.assertEqual(result["name_en"], "Priti")
        self.assertEqual(result["current_degree"], 13.333333)
        self.assertEqual(result["degrees_completed"], 0.0)

    def test_end_of_circle_is_vaidhriti(self) -> None:
        result = get_panchang_yoga(0.0, 359.999)

        self.assertEqual(result["yoga_index"], 27)
        self.assertEqual(result["name_en"], "Vaidhriti")
        self.assertEqual(result["current_degree"], 359.999)

    def test_wrapping_works_when_sun_plus_moon_is_over_360(self) -> None:
        result = get_panchang_yoga(350.0, 20.0)

        self.assertEqual(result["current_degree"], 10.0)
        self.assertEqual(result["yoga_index"], 1)
        self.assertEqual(result["degrees_completed"], 10.0)
        self.assertEqual(result["degrees_remaining"], 3.333333)

    def test_negative_and_over_360_inputs_normalize_correctly(self) -> None:
        result = get_panchang_yoga(-10.0, 25.0)

        self.assertEqual(result["current_degree"], 15.0)
        self.assertEqual(result["yoga_index"], 2)
        self.assertEqual(result["degrees_completed"], 1.666667)

        over_360_result = get_panchang_yoga(370.0, 5.0)
        self.assertEqual(over_360_result["current_degree"], 15.0)
        self.assertEqual(over_360_result["yoga_index"], 2)

    def test_invalid_longitude_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_panchang_yoga("0.0", 0.0)  # type: ignore[arg-type]

    def test_non_finite_longitude_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            get_panchang_yoga(0.0, float("nan"))

    def test_get_panchang_yoga_with_boundary_returns_end_time(self) -> None:
        fake_julian_result = SimpleNamespace(
            utc_datetime=datetime(2026, 6, 29, 6, 30, tzinfo=timezone.utc),
            julian_day_ut=2461220.7708333335,
        )
        boundary_utc = datetime(2026, 6, 29, 10, 30, tzinfo=timezone.utc)

        with _patch_boundary_dependencies(fake_julian_result, boundary_utc) as mocks:
            result = get_panchang_yoga_with_boundary(2026, 6, 29, 12, 0, 0, 5.5)

        self.assertEqual(result["yoga_index"], 2)
        self.assertEqual(result["name_en"], "Priti")
        self.assertEqual(result["current_degree"], 15.0)
        self.assertAlmostEqual(result["end_degree"], 26.666666666666668)
        self.assertAlmostEqual(result["end_degree"] % (360.0 / 27), 0.0)
        self.assertEqual(result["end_time_utc"], "2026-06-29T10:30:00Z")
        self.assertEqual(result["end_time_local"], "2026-06-29T16:00:00+05:30")
        self.assertGreater(
            datetime.fromisoformat(result["end_time_local"]),
            datetime.fromisoformat("2026-06-29T12:00:00+05:30"),
        )
        mocks["find_next_longitude_boundary"].assert_called_once()
        self.assertAlmostEqual(
            mocks["find_next_longitude_boundary"].call_args.args[2],
            26.666666666666668,
        )


class _patch_boundary_dependencies:
    """Context manager for Yoga boundary dependency patches."""

    def __init__(
        self,
        fake_julian_result: SimpleNamespace,
        boundary_utc: datetime,
    ) -> None:
        self.fake_julian_result = fake_julian_result
        self.boundary_utc = boundary_utc

    def __enter__(self) -> dict[str, object]:
        self._patchers = {
            "calculate_julian_day": patch.object(
                yoga.julian,
                "calculate_julian_day",
                return_value=self.fake_julian_result,
            ),
            "get_ayanamsa": patch.object(
                yoga.ayanamsa,
                "get_ayanamsa",
                return_value=24.0,
            ),
            "get_planet_positions": patch.object(
                yoga.planet_positions,
                "get_planet_positions",
                return_value=[
                    {"planet": "sun", "sidereal_longitude": 5.0},
                    {"planet": "moon", "sidereal_longitude": 10.0},
                ],
            ),
            "find_next_longitude_boundary": patch.object(
                yoga.search,
                "find_next_longitude_boundary",
                return_value=self.boundary_utc,
            ),
        }
        self._mocks = {
            name: patcher.start() for name, patcher in self._patchers.items()
        }
        return self._mocks

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        for patcher in reversed(tuple(self._patchers.values())):
            patcher.stop()


if __name__ == "__main__":
    unittest.main()
