"""Tests for deterministic Tithi lookup."""

from __future__ import annotations

import unittest

from backend.app.astrology.tithi import get_tithi
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


if __name__ == "__main__":
    unittest.main()
