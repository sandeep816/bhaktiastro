"""Tests for deterministic Rashi lookup."""

from __future__ import annotations

import unittest

from backend.app.kundali.rashi import get_rashi


class RashiLookupTest(unittest.TestCase):
    """Validate Rashi lookup boundaries and normalization."""

    def test_zero_degrees_is_aries(self) -> None:
        result = get_rashi(0.0)

        self.assertEqual(
            result,
            {
                "index": 1,
                "english": "Aries",
                "hindi": "मेष",
                "sanskrit": "Mesha",
                "lord": "Mars",
                "element": "Fire",
                "modality": "Movable",
                "start_degree": 0.0,
                "end_degree": 30.0,
                "degree_in_rashi": 0.0,
            },
        )

    def test_degree_before_thirty_is_aries(self) -> None:
        result = get_rashi(29.999)

        self.assertEqual(result["index"], 1)
        self.assertEqual(result["english"], "Aries")
        self.assertEqual(result["degree_in_rashi"], 29.999)

    def test_thirty_degrees_is_taurus(self) -> None:
        result = get_rashi(30.0)

        self.assertEqual(result["index"], 2)
        self.assertEqual(result["english"], "Taurus")
        self.assertEqual(result["hindi"], "वृषभ")
        self.assertEqual(result["sanskrit"], "Vrishabha")
        self.assertEqual(result["lord"], "Venus")
        self.assertEqual(result["element"], "Earth")
        self.assertEqual(result["modality"], "Fixed")
        self.assertEqual(result["start_degree"], 30.0)
        self.assertEqual(result["end_degree"], 60.0)
        self.assertEqual(result["degree_in_rashi"], 0.0)

    def test_end_of_circle_is_pisces(self) -> None:
        result = get_rashi(359.999)

        self.assertEqual(result["index"], 12)
        self.assertEqual(result["english"], "Pisces")
        self.assertEqual(result["hindi"], "मीन")
        self.assertEqual(result["degree_in_rashi"], 29.999)

    def test_negative_longitude_normalizes_correctly(self) -> None:
        result = get_rashi(-1.0)

        self.assertEqual(result["index"], 12)
        self.assertEqual(result["english"], "Pisces")
        self.assertEqual(result["degree_in_rashi"], 29.0)

    def test_longitude_greater_than_360_normalizes_correctly(self) -> None:
        result = get_rashi(375.234)

        self.assertEqual(result["index"], 1)
        self.assertEqual(result["english"], "Aries")
        self.assertEqual(result["degree_in_rashi"], 15.234)

    def test_full_circle_normalizes_to_aries(self) -> None:
        result = get_rashi(360.0)

        self.assertEqual(result["index"], 1)
        self.assertEqual(result["english"], "Aries")
        self.assertEqual(result["degree_in_rashi"], 0.0)

    def test_invalid_longitude_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_rashi("0.0")  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            get_rashi(True)  # type: ignore[arg-type]

    def test_non_finite_longitude_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            get_rashi(float("nan"))

        with self.assertRaises(ValueError):
            get_rashi(float("inf"))


if __name__ == "__main__":
    unittest.main()

