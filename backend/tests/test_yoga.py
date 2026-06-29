"""Tests for deterministic Panchang Yoga lookup."""

from __future__ import annotations

import unittest

from backend.app.astrology.yoga import get_panchang_yoga


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


if __name__ == "__main__":
    unittest.main()
