"""Tests for deterministic Nakshatra lookup."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from backend.app.astrology import nakshatra
from backend.app.astrology.nakshatra import get_nakshatra, get_nakshatra_with_boundary


class NakshatraLookupTest(unittest.TestCase):
    """Validate Nakshatra and Pada lookup boundaries."""

    def test_zero_degrees_is_ashwini_pada_one(self) -> None:
        result = get_nakshatra(0.0)

        self.assertEqual(result["index"], 0)
        self.assertEqual(result["name_en"], "Ashwini")
        self.assertEqual(result["name_hi"], "अश्विनी")
        self.assertEqual(result["name_sa"], "Ashvini")
        self.assertEqual(result["pada"], 1)
        self.assertEqual(result["ruling_planet"], "ketu")
        self.assertEqual(result["degree_within_nakshatra"], 0.0)

    def test_nakshatra_boundary_starts_bharani_pada_one(self) -> None:
        result = get_nakshatra(13.333333)

        self.assertEqual(result["index"], 1)
        self.assertEqual(result["name_en"], "Bharani")
        self.assertEqual(result["pada"], 1)
        self.assertEqual(result["degree_within_nakshatra"], 0.0)

    def test_end_of_circle_is_revati_pada_four(self) -> None:
        result = get_nakshatra(359.999)

        self.assertEqual(result["index"], 26)
        self.assertEqual(result["name_en"], "Revati")
        self.assertEqual(result["pada"], 4)

    def test_pada_boundaries_are_correct(self) -> None:
        self.assertEqual(get_nakshatra(0.0)["pada"], 1)
        self.assertEqual(get_nakshatra(3.333333)["pada"], 2)
        self.assertEqual(get_nakshatra(6.666666)["pada"], 3)
        self.assertEqual(get_nakshatra(9.999999)["pada"], 4)
        self.assertEqual(get_nakshatra(13.333332)["pada"], 4)

    def test_negative_longitude_normalizes_correctly(self) -> None:
        result = get_nakshatra(-1.0)

        self.assertEqual(result["index"], 26)
        self.assertEqual(result["name_en"], "Revati")
        self.assertEqual(result["pada"], 4)

    def test_longitude_greater_than_360_normalizes_correctly(self) -> None:
        result = get_nakshatra(370.0)

        self.assertEqual(result["index"], 0)
        self.assertEqual(result["name_en"], "Ashwini")
        self.assertEqual(result["pada"], 4)
        self.assertEqual(result["degree_within_nakshatra"], 10.0)

    def test_invalid_longitude_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_nakshatra("0.0")  # type: ignore[arg-type]

    def test_non_finite_longitude_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            get_nakshatra(float("nan"))

    def test_get_nakshatra_with_boundary_returns_end_time(self) -> None:
        fake_julian_result = SimpleNamespace(
            utc_datetime=datetime(2026, 6, 29, 6, 30, tzinfo=timezone.utc),
            julian_day_ut=2461220.7708333335,
        )
        boundary_utc = datetime(2026, 6, 29, 12, 30, tzinfo=timezone.utc)

        with _patch_boundary_dependencies(fake_julian_result, boundary_utc) as mocks:
            result = get_nakshatra_with_boundary(2026, 6, 29, 12, 0, 0, 5.5)

        self.assertEqual(result["index"], 0)
        self.assertEqual(result["name_en"], "Ashwini")
        self.assertEqual(result["current_degree"], 10.0)
        self.assertAlmostEqual(result["end_degree"], 13.333333333333334)
        self.assertAlmostEqual(result["end_degree"] % (360.0 / 27), 0.0)
        self.assertEqual(result["degrees_remaining"], 3.333333)
        self.assertEqual(result["end_time_utc"], "2026-06-29T12:30:00Z")
        self.assertEqual(result["end_time_local"], "2026-06-29T18:00:00+05:30")
        self.assertGreater(
            datetime.fromisoformat(result["end_time_local"]),
            datetime.fromisoformat("2026-06-29T12:00:00+05:30"),
        )
        mocks["find_next_longitude_boundary"].assert_called_once()
        self.assertAlmostEqual(
            mocks["find_next_longitude_boundary"].call_args.args[2],
            13.333333333333334,
        )


class _patch_boundary_dependencies:
    """Context manager for Nakshatra boundary dependency patches."""

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
                nakshatra.julian,
                "calculate_julian_day",
                return_value=self.fake_julian_result,
            ),
            "get_ayanamsa": patch.object(
                nakshatra.ayanamsa,
                "get_ayanamsa",
                return_value=24.0,
            ),
            "get_planet_positions": patch.object(
                nakshatra.planet_positions,
                "get_planet_positions",
                return_value=[
                    {"planet": "moon", "sidereal_longitude": 10.0},
                ],
            ),
            "find_next_longitude_boundary": patch.object(
                nakshatra.search,
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
