"""Tests for deterministic Vara lookup."""

from __future__ import annotations

import unittest
from datetime import date

from backend.app.astrology.vara import get_vara


class VaraLookupTest(unittest.TestCase):
    """Validate civil weekday Vara lookup."""

    def test_2026_06_29_is_monday(self) -> None:
        result = get_vara("2026-06-29")

        self.assertEqual(result["index"], 2)
        self.assertEqual(result["name_en"], "Monday")
        self.assertEqual(result["name_hi"], "सोमवार")
        self.assertEqual(result["name_sa"], "Somavara")
        self.assertEqual(result["ruling_planet"], "moon")

    def test_2026_06_28_is_sunday(self) -> None:
        result = get_vara("2026-06-28")

        self.assertEqual(result["index"], 1)
        self.assertEqual(result["name_en"], "Sunday")
        self.assertEqual(result["name_hi"], "रविवार")
        self.assertEqual(result["name_sa"], "Ravivara")
        self.assertEqual(result["ruling_planet"], "sun")

    def test_iso_string_input_works(self) -> None:
        result = get_vara("2026-07-04")

        self.assertEqual(result["index"], 7)
        self.assertEqual(result["name_en"], "Saturday")
        self.assertEqual(result["name_sa"], "Shanivara")

    def test_python_date_input_works(self) -> None:
        result = get_vara(date(2026, 7, 3))

        self.assertEqual(result["index"], 6)
        self.assertEqual(result["name_en"], "Friday")
        self.assertEqual(result["name_sa"], "Shukravara")

    def test_invalid_string_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            get_vara("2026/06/29")

    def test_invalid_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            get_vara(20260629)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
