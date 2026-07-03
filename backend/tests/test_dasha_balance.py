"""Tests for birth Dasha balance calculations."""

from __future__ import annotations

import unittest

from backend.app.constants.nakshatra import NAKSHATRA_SPAN_DEGREES
from backend.app.dasha.balance import calculate_birth_dasha_balance


class BirthDashaBalanceTest(unittest.TestCase):
    """Validate birth Dasha balance helpers."""

    def test_beginning_of_nakshatra_gives_full_balance(self) -> None:
        result = calculate_birth_dasha_balance(
            nakshatra_index=0,
            moon_longitude=0.0,
        )

        self.assertEqual(result["nakshatra_index"], 0)
        self.assertEqual(result["dasha_lord"], "ketu")
        self.assertEqual(result["full_dasha_years"], 7)
        self.assertEqual(result["nakshatra_elapsed_degrees"], 0.0)
        self.assertEqual(result["balance_ratio"], 1.0)
        self.assertEqual(result["balance_years"], 7.0)

    def test_middle_of_nakshatra_gives_half_balance(self) -> None:
        result = calculate_birth_dasha_balance(
            nakshatra_index=0,
            moon_longitude=NAKSHATRA_SPAN_DEGREES / 2.0,
        )

        self.assertEqual(result["dasha_lord"], "ketu")
        self.assertEqual(result["balance_ratio"], 0.5)
        self.assertEqual(result["balance_years"], 3.5)

    def test_end_of_nakshatra_gives_near_zero_balance(self) -> None:
        result = calculate_birth_dasha_balance(
            nakshatra_index=0,
            moon_longitude=NAKSHATRA_SPAN_DEGREES - 0.000001,
        )

        self.assertEqual(result["dasha_lord"], "ketu")
        self.assertLess(result["balance_ratio"], 0.000001)
        self.assertLess(result["balance_years"], 0.00001)

    def test_longitude_above_360_is_normalized(self) -> None:
        result = calculate_birth_dasha_balance(
            nakshatra_index=1,
            moon_longitude=(
                360.0 + NAKSHATRA_SPAN_DEGREES + (NAKSHATRA_SPAN_DEGREES / 2.0)
            ),
        )

        self.assertEqual(result["nakshatra_index"], 1)
        self.assertEqual(result["dasha_lord"], "venus")
        self.assertEqual(result["full_dasha_years"], 20)
        self.assertEqual(result["balance_ratio"], 0.5)
        self.assertEqual(result["balance_years"], 10.0)

    def test_invalid_nakshatra_index_fails_safely(self) -> None:
        with self.assertRaises(ValueError):
            calculate_birth_dasha_balance(-1, 0.0)

        with self.assertRaises(ValueError):
            calculate_birth_dasha_balance(27, 0.0)

        with self.assertRaises(TypeError):
            calculate_birth_dasha_balance(True, 0.0)  # type: ignore[arg-type]

    def test_mismatched_longitude_and_nakshatra_index_fails_safely(self) -> None:
        with self.assertRaises(ValueError):
            calculate_birth_dasha_balance(0, NAKSHATRA_SPAN_DEGREES)

    def test_invalid_moon_longitude_fails_safely(self) -> None:
        with self.assertRaises(TypeError):
            calculate_birth_dasha_balance(0, False)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            calculate_birth_dasha_balance(0, float("nan"))


if __name__ == "__main__":
    unittest.main()
