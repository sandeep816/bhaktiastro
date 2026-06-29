"""Tests for deterministic Nakshatra lookup."""

from __future__ import annotations

import unittest

from backend.app.astrology.nakshatra import get_nakshatra


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


if __name__ == "__main__":
    unittest.main()
