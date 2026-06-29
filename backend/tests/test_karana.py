"""Tests for deterministic Karana lookup."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from backend.app.astrology import karana
from backend.app.astrology.karana import get_karana, get_karana_with_boundary
from backend.app.constants.karana import FIXED_KARANA_TYPE, REPEATING_KARANA_TYPE


class KaranaLookupTest(unittest.TestCase):
    """Validate Karana lookup and six-degree boundaries."""

    def test_zero_degree_angle_is_kimstughna(self) -> None:
        result = get_karana(0.0, 0.0)

        self.assertEqual(result["half_tithi_index"], 0)
        self.assertEqual(result["karana_index"], 11)
        self.assertEqual(result["name_en"], "Kimstughna")
        self.assertEqual(result["name_hi"], "किंस्तुघ्न")
        self.assertEqual(result["name_sa"], "Kimstughna")
        self.assertEqual(result["type"], FIXED_KARANA_TYPE)
        self.assertEqual(result["current_angle"], 0.0)
        self.assertEqual(result["degrees_completed"], 0.0)
        self.assertEqual(result["degrees_remaining"], 6.0)

    def test_six_degree_angle_is_bava(self) -> None:
        result = get_karana(0.0, 6.0)

        self.assertEqual(result["half_tithi_index"], 1)
        self.assertEqual(result["name_en"], "Bava")
        self.assertEqual(result["type"], REPEATING_KARANA_TYPE)
        self.assertEqual(result["start_angle"], 6.0)
        self.assertEqual(result["end_angle"], 12.0)

    def test_twelve_degree_angle_is_balava(self) -> None:
        result = get_karana(0.0, 12.0)

        self.assertEqual(result["half_tithi_index"], 2)
        self.assertEqual(result["name_en"], "Balava")
        self.assertEqual(result["type"], REPEATING_KARANA_TYPE)

    def test_fixed_karana_positions_follow_mapping_rule(self) -> None:
        shakuni = get_karana(0.0, 342.0)
        chatushpada = get_karana(0.0, 348.0)
        naga = get_karana(0.0, 354.0)

        self.assertEqual(shakuni["half_tithi_index"], 57)
        self.assertEqual(shakuni["name_en"], "Shakuni")
        self.assertEqual(chatushpada["half_tithi_index"], 58)
        self.assertEqual(chatushpada["name_en"], "Chatushpada")
        self.assertEqual(naga["half_tithi_index"], 59)
        self.assertEqual(naga["name_en"], "Naga")

    def test_three_hundred_fifty_eight_degree_angle_is_naga(self) -> None:
        result = get_karana(0.0, 358.0)

        self.assertEqual(result["half_tithi_index"], 59)
        self.assertEqual(result["name_en"], "Naga")
        self.assertEqual(result["type"], FIXED_KARANA_TYPE)
        self.assertEqual(result["degrees_completed"], 4.0)
        self.assertEqual(result["degrees_remaining"], 2.0)

    def test_wrapping_works_when_moon_is_less_than_sun(self) -> None:
        result = get_karana(20.0, 10.0)

        self.assertEqual(result["current_angle"], 350.0)
        self.assertEqual(result["half_tithi_index"], 58)
        self.assertEqual(result["name_en"], "Chatushpada")
        self.assertEqual(result["degrees_completed"], 2.0)

    def test_negative_and_over_360_inputs_normalize_correctly(self) -> None:
        result = get_karana(390.0, -330.0)

        self.assertEqual(result["current_angle"], 0.0)
        self.assertEqual(result["name_en"], "Kimstughna")

        wrapped_result = get_karana(-10.0, 365.0)
        self.assertEqual(wrapped_result["current_angle"], 15.0)
        self.assertEqual(wrapped_result["half_tithi_index"], 2)
        self.assertEqual(wrapped_result["name_en"], "Balava")
        self.assertEqual(wrapped_result["degrees_completed"], 3.0)

    def test_invalid_longitude_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_karana("0.0", 0.0)  # type: ignore[arg-type]

    def test_non_finite_longitude_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            get_karana(0.0, float("nan"))

    def test_get_karana_with_boundary_returns_end_time(self) -> None:
        fake_julian_result = SimpleNamespace(
            utc_datetime=datetime(2026, 6, 29, 6, 30, tzinfo=timezone.utc),
            julian_day_ut=2461220.7708333335,
        )
        boundary_utc = datetime(2026, 6, 29, 8, 30, tzinfo=timezone.utc)

        with _patch_boundary_dependencies(fake_julian_result, boundary_utc) as mocks:
            result = get_karana_with_boundary(2026, 6, 29, 12, 0, 0, 5.5)

        self.assertEqual(result["half_tithi_index"], 1)
        self.assertEqual(result["name_en"], "Bava")
        self.assertEqual(result["current_angle"], 7.0)
        self.assertEqual(result["end_angle"], 12.0)
        self.assertEqual(result["end_angle"] % 6.0, 0.0)
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
    """Context manager for Karana boundary dependency patches."""

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
                karana.julian,
                "calculate_julian_day",
                return_value=self.fake_julian_result,
            ),
            "get_ayanamsa": patch.object(
                karana.ayanamsa,
                "get_ayanamsa",
                return_value=24.0,
            ),
            "get_planet_positions": patch.object(
                karana.planet_positions,
                "get_planet_positions",
                return_value=[
                    {"planet": "sun", "sidereal_longitude": 3.0},
                    {"planet": "moon", "sidereal_longitude": 10.0},
                ],
            ),
            "find_next_longitude_boundary": patch.object(
                karana.search,
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
