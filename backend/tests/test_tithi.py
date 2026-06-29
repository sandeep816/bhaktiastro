"""Tests for deterministic Tithi lookup."""

from __future__ import annotations

import unittest

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from backend.app.astrology import tithi
from backend.app.astrology.tithi import get_tithi, get_tithi_with_boundary
from backend.app.constants.tithi import KRISHNA_PAKSHA, SHUKLA_PAKSHA


class TithiLookupTest(unittest.TestCase):
    """Validate Tithi lookup and angle boundaries."""

    def test_zero_degree_angle_is_tithi_one(self) -> None:
        result = get_tithi(0.0, 0.0)

        self.assertEqual(result["tithi_number"], 1)
        self.assertEqual(result["name_en"], "Pratipada")
        self.assertEqual(result["name_hi"], "प्रतिपदा")
        self.assertEqual(result["name_sa"], "Pratipada")
        self.assertEqual(result["paksha"], SHUKLA_PAKSHA)
        self.assertEqual(result["current_angle"], 0.0)
        self.assertEqual(result["degrees_completed"], 0.0)
        self.assertEqual(result["degrees_remaining"], 12.0)

    def test_angle_before_first_boundary_is_tithi_one(self) -> None:
        result = get_tithi(0.0, 11.999)

        self.assertEqual(result["tithi_number"], 1)
        self.assertEqual(result["current_angle"], 11.999)
        self.assertEqual(result["degrees_completed"], 11.999)
        self.assertEqual(result["degrees_remaining"], 0.001)

    def test_twelve_degree_angle_is_tithi_two(self) -> None:
        result = get_tithi(0.0, 12.0)

        self.assertEqual(result["tithi_number"], 2)
        self.assertEqual(result["name_en"], "Dwitiya")
        self.assertEqual(result["start_angle"], 12.0)
        self.assertEqual(result["end_angle"], 24.0)
        self.assertEqual(result["degrees_completed"], 0.0)

    def test_one_hundred_eighty_degree_angle_is_tithi_sixteen(self) -> None:
        result = get_tithi(0.0, 180.0)

        self.assertEqual(result["tithi_number"], 16)
        self.assertEqual(result["name_en"], "Pratipada")
        self.assertEqual(result["paksha"], KRISHNA_PAKSHA)
        self.assertEqual(result["start_angle"], 180.0)
        self.assertEqual(result["degrees_completed"], 0.0)

    def test_three_hundred_forty_eight_degree_angle_is_tithi_thirty(
        self,
    ) -> None:
        result = get_tithi(0.0, 348.0)

        self.assertEqual(result["tithi_number"], 30)
        self.assertEqual(result["name_en"], "Amavasya")
        self.assertEqual(result["paksha"], KRISHNA_PAKSHA)
        self.assertEqual(result["start_angle"], 348.0)
        self.assertEqual(result["end_angle"], 360.0)

    def test_wrapping_works_when_moon_is_less_than_sun(self) -> None:
        result = get_tithi(20.0, 10.0)

        self.assertEqual(result["current_angle"], 350.0)
        self.assertEqual(result["tithi_number"], 30)
        self.assertEqual(result["degrees_completed"], 2.0)
        self.assertEqual(result["degrees_remaining"], 10.0)

    def test_negative_and_over_360_inputs_normalize_correctly(self) -> None:
        result = get_tithi(390.0, -330.0)

        self.assertEqual(result["current_angle"], 0.0)
        self.assertEqual(result["tithi_number"], 1)

        wrapped_result = get_tithi(-10.0, 365.0)
        self.assertEqual(wrapped_result["current_angle"], 15.0)
        self.assertEqual(wrapped_result["tithi_number"], 2)
        self.assertEqual(wrapped_result["degrees_completed"], 3.0)

    def test_invalid_longitude_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_tithi("0.0", 0.0)  # type: ignore[arg-type]

    def test_non_finite_longitude_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            get_tithi(0.0, float("inf"))

    def test_get_tithi_with_boundary_returns_end_time(self) -> None:
        fake_julian_result = SimpleNamespace(
            utc_datetime=datetime(2026, 6, 29, 6, 30, tzinfo=timezone.utc),
            julian_day_ut=2461220.7708333335,
        )
        boundary_utc = datetime(2026, 6, 29, 8, 30, tzinfo=timezone.utc)

        with _patch_boundary_dependencies(fake_julian_result, boundary_utc) as mocks:
            result = get_tithi_with_boundary(2026, 6, 29, 12, 0, 0, 5.5)

        self.assertEqual(result["tithi_number"], 1)
        self.assertEqual(result["end_angle"], 12.0)
        self.assertEqual(result["end_angle"] % 12.0, 0.0)
        self.assertEqual(result["end_time_utc"], "2026-06-29T08:30:00Z")
        self.assertEqual(result["end_time_local"], "2026-06-29T14:00:00+05:30")
        self.assertGreater(
            datetime.fromisoformat(result["end_time_local"]),
            datetime.fromisoformat("2026-06-29T12:00:00+05:30"),
        )
        mocks["find_next_longitude_boundary"].assert_called_once()
        self.assertEqual(
            mocks["find_next_longitude_boundary"].call_args.args[2],
            12.0,
        )


class _patch_boundary_dependencies:
    """Context manager for Tithi boundary dependency patches."""

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
                tithi.julian,
                "calculate_julian_day",
                return_value=self.fake_julian_result,
            ),
            "get_ayanamsa": patch.object(
                tithi.ayanamsa,
                "get_ayanamsa",
                return_value=24.0,
            ),
            "get_planet_positions": patch.object(
                tithi.planet_positions,
                "get_planet_positions",
                return_value=[
                    {"planet": "sun", "sidereal_longitude": 0.0},
                    {"planet": "moon", "sidereal_longitude": 11.0},
                ],
            ),
            "find_next_longitude_boundary": patch.object(
                tithi.search,
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
