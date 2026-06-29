"""Tests for deterministic Karana lookup."""

from __future__ import annotations

import unittest

from backend.app.astrology.karana import get_karana
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


if __name__ == "__main__":
    unittest.main()
