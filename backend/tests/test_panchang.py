"""Tests for basic Panchang assembly."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from backend.app.astrology import panchang


class BasicPanchangTest(unittest.TestCase):
    """Validate basic Panchang orchestration."""

    def test_returns_all_expected_keys(self) -> None:
        result = self._calculate_with_mocks()

        self.assertEqual(
            set(result.keys()),
            {
                "julian_day",
                "ayanamsa",
                "sun",
                "moon",
                "tithi",
                "nakshatra",
                "yoga",
                "karana",
                "vara",
                "sunrise",
                "sunset",
                "moonrise",
                "moonset",
            },
        )

    def test_sun_and_moon_data_exist(self) -> None:
        result = self._calculate_with_mocks()

        self.assertEqual(result["sun"]["planet"], "sun")
        self.assertEqual(result["sun"]["sidereal_longitude"], 10.0)
        self.assertEqual(result["moon"]["planet"], "moon")
        self.assertEqual(result["moon"]["sidereal_longitude"], 40.0)

    def test_sub_calculations_use_sun_and_moon_longitudes(self) -> None:
        with self._patched_dependencies() as mocks:
            panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

        mocks["get_tithi_with_boundary"].assert_called_once_with(
            2026,
            6,
            29,
            12,
            0,
            0,
            5.5,
        )
        mocks["get_nakshatra"].assert_called_once_with(40.0)
        mocks["get_panchang_yoga"].assert_called_once_with(10.0, 40.0)
        mocks["get_karana"].assert_called_once_with(10.0, 40.0)

    def test_vara_is_calculated_from_local_date(self) -> None:
        with self._patched_dependencies() as mocks:
            panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                23,
                30,
                0,
                5.5,
                26.2389,
                73.0243,
            )

        mocks["get_vara"].assert_called_once()
        self.assertEqual(mocks["get_vara"].call_args.args[0].isoformat(), "2026-06-29")

    def test_julian_ayanamsa_and_planet_pipeline_is_used(self) -> None:
        with self._patched_dependencies() as mocks:
            result = panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

        mocks["calculate_julian_day"].assert_called_once_with(
            2026,
            6,
            29,
            12,
            0,
            0,
            5.5,
        )
        mocks["get_ayanamsa"].assert_called_once_with(2460123.5)
        mocks["get_planet_positions"].assert_called_once_with(2460123.5, 24.1234)
        self.assertEqual(result["julian_day"]["julian_day_ut"], 2460123.5)
        self.assertEqual(
            result["julian_day"]["utc_datetime"],
            "2026-06-29T06:30:00+00:00",
        )
        self.assertEqual(result["ayanamsa"], {"value": 24.1234})

    def test_sunrise_and_sunset_are_calculated_from_local_date_and_location(
        self,
    ) -> None:
        with self._patched_dependencies() as mocks:
            result = panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

        mocks["get_sunrise"].assert_called_once_with(
            2026,
            6,
            29,
            26.2389,
            73.0243,
            5.5,
        )
        mocks["get_sunset"].assert_called_once_with(
            2026,
            6,
            29,
            26.2389,
            73.0243,
            5.5,
        )
        self.assertEqual(result["sunrise"]["event"], "sunrise")
        self.assertEqual(result["sunset"]["event"], "sunset")

    def test_moonrise_and_moonset_are_calculated_from_local_date_and_location(
        self,
    ) -> None:
        with self._patched_dependencies() as mocks:
            result = panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

        mocks["get_moonrise"].assert_called_once_with(
            2026,
            6,
            29,
            26.2389,
            73.0243,
            5.5,
        )
        mocks["get_moonset"].assert_called_once_with(
            2026,
            6,
            29,
            26.2389,
            73.0243,
            5.5,
        )
        self.assertEqual(result["moonrise"]["event"], "moonrise")
        self.assertEqual(result["moonset"]["event"], "moonset")

    def test_missing_moonrise_and_moonset_do_not_crash(self) -> None:
        with self._patched_dependencies() as mocks:
            mocks["get_moonrise"].return_value = {
                "event": "moonrise",
                "local_time": None,
                "utc_datetime": None,
                "timezone_offset": 5.5,
            }
            mocks["get_moonset"].return_value = {
                "event": "moonset",
                "local_time": None,
                "utc_datetime": None,
                "timezone_offset": 5.5,
            }

            result = panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

        self.assertIsNone(result["moonrise"]["local_time"])
        self.assertIsNone(result["moonrise"]["utc_datetime"])
        self.assertIsNone(result["moonset"]["local_time"])
        self.assertIsNone(result["moonset"]["utc_datetime"])

    def test_invalid_date_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid local date components"):
            panchang.calculate_basic_panchang(
                2026,
                2,
                30,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

    def _calculate_with_mocks(self) -> panchang.BasicPanchangResult:
        with self._patched_dependencies():
            return panchang.calculate_basic_panchang(
                2026,
                6,
                29,
                12,
                0,
                0,
                5.5,
                26.2389,
                73.0243,
            )

    def _patched_dependencies(self) -> "_PanchangPatchContext":
        return _PanchangPatchContext()


class _PanchangPatchContext:
    """Context manager for patching Panchang dependencies."""

    def __enter__(self) -> dict[str, unittest.mock.Mock]:
        fake_julian_result = SimpleNamespace(
            utc_datetime=datetime(2026, 6, 29, 6, 30, tzinfo=timezone.utc),
            julian_day_ut=2460123.5,
        )
        self._patchers = {
            "calculate_julian_day": patch.object(
                panchang.julian,
                "calculate_julian_day",
                return_value=fake_julian_result,
            ),
            "get_ayanamsa": patch.object(
                panchang.ayanamsa,
                "get_ayanamsa",
                return_value=24.1234,
            ),
            "get_planet_positions": patch.object(
                panchang.planet_positions,
                "get_planet_positions",
                return_value=[
                    {"planet": "sun", "sidereal_longitude": 10.0},
                    {"planet": "moon", "sidereal_longitude": 40.0},
                ],
            ),
            "get_tithi_with_boundary": patch.object(
                panchang.tithi,
                "get_tithi_with_boundary",
                return_value={
                    "tithi_number": 3,
                    "end_time_local": "2026-06-29T14:00:00+05:30",
                    "end_time_utc": "2026-06-29T08:30:00Z",
                },
            ),
            "get_nakshatra": patch.object(
                panchang.nakshatra,
                "get_nakshatra",
                return_value={"index": 3},
            ),
            "get_panchang_yoga": patch.object(
                panchang.yoga,
                "get_panchang_yoga",
                return_value={"yoga_index": 4},
            ),
            "get_karana": patch.object(
                panchang.karana,
                "get_karana",
                return_value={"karana_index": 4},
            ),
            "get_vara": patch.object(
                panchang.vara,
                "get_vara",
                return_value={"index": 2, "name_en": "Monday"},
            ),
            "get_sunrise": patch.object(
                panchang.rise_set,
                "get_sunrise",
                return_value={
                    "event": "sunrise",
                    "local_time": "05:49:24",
                    "utc_datetime": "2026-06-29T00:19:24Z",
                    "timezone_offset": 5.5,
                },
            ),
            "get_sunset": patch.object(
                panchang.rise_set,
                "get_sunset",
                return_value={
                    "event": "sunset",
                    "local_time": "19:31:49",
                    "utc_datetime": "2026-06-29T14:01:49Z",
                    "timezone_offset": 5.5,
                },
            ),
            "get_moonrise": patch.object(
                panchang.rise_set,
                "get_moonrise",
                return_value={
                    "event": "moonrise",
                    "local_time": "20:14:20",
                    "utc_datetime": "2026-06-29T14:44:20Z",
                    "timezone_offset": 5.5,
                },
            ),
            "get_moonset": patch.object(
                panchang.rise_set,
                "get_moonset",
                return_value={
                    "event": "moonset",
                    "local_time": "09:01:05",
                    "utc_datetime": "2026-06-29T03:31:05Z",
                    "timezone_offset": 5.5,
                },
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
