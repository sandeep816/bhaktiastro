"""Tests for placeholder Bhava house foundation helpers."""

from __future__ import annotations

import unittest

from backend.app.kundali.bhava import (
    HOUSE_COUNT,
    HOUSE_NUMBERS,
    HOUSE_SPAN_DEGREES,
    get_house_degree,
    get_house_index_from_degree,
    get_house_number_from_degree,
    normalize_house_number,
)


class BhavaFoundationTest(unittest.TestCase):
    """Validate generic 30-degree placeholder house helpers."""

    def test_house_constants_define_twelve_thirty_degree_houses(self) -> None:
        self.assertEqual(HOUSE_COUNT, 12)
        self.assertEqual(HOUSE_NUMBERS, tuple(range(1, 13)))
        self.assertEqual(HOUSE_SPAN_DEGREES, 30.0)

    def test_normalize_house_number_wraps_into_one_to_twelve(self) -> None:
        self.assertEqual(normalize_house_number(1), 1)
        self.assertEqual(normalize_house_number(12), 12)
        self.assertEqual(normalize_house_number(13), 1)
        self.assertEqual(normalize_house_number(0), 12)
        self.assertEqual(normalize_house_number(-1), 11)
        self.assertEqual(normalize_house_number(25), 1)

    def test_boundary_degrees_map_to_placeholder_houses(self) -> None:
        self.assertEqual(get_house_index_from_degree(0.0), 0)
        self.assertEqual(get_house_number_from_degree(0.0), 1)
        self.assertEqual(get_house_number_from_degree(29.999), 1)
        self.assertEqual(get_house_number_from_degree(30.0), 2)
        self.assertEqual(get_house_number_from_degree(359.999), 12)
        self.assertEqual(get_house_number_from_degree(360.0), 1)

    def test_negative_degree_normalizes_correctly(self) -> None:
        self.assertEqual(get_house_index_from_degree(-1.0), 11)
        self.assertEqual(get_house_number_from_degree(-1.0), 12)
        self.assertEqual(get_house_degree(-1.0), 29.0)

    def test_degree_above_360_normalizes_correctly(self) -> None:
        self.assertEqual(get_house_index_from_degree(375.25), 0)
        self.assertEqual(get_house_number_from_degree(375.25), 1)
        self.assertEqual(get_house_degree(375.25), 15.25)

    def test_get_house_degree_returns_degree_inside_house(self) -> None:
        self.assertEqual(get_house_degree(0.0), 0.0)
        self.assertEqual(get_house_degree(29.999), 29.999)
        self.assertEqual(get_house_degree(30.0), 0.0)
        self.assertEqual(get_house_degree(44.5), 14.5)
        self.assertEqual(get_house_degree(359.999), 29.999)

    def test_invalid_house_number_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            normalize_house_number("1")  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            normalize_house_number(True)  # type: ignore[arg-type]

    def test_invalid_degree_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_house_number_from_degree("0.0")  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            get_house_degree(False)  # type: ignore[arg-type]

    def test_non_finite_degree_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            get_house_index_from_degree(float("nan"))

        with self.assertRaises(ValueError):
            get_house_degree(float("inf"))


if __name__ == "__main__":
    unittest.main()
