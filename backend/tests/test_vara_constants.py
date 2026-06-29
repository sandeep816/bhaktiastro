"""Tests for Vara constants."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from backend.app.constants.vara import VARA_COUNT, VARA_LIST


class VaraConstantsTest(unittest.TestCase):
    """Validate immutable Vara metadata."""

    def test_total_varas_is_7(self) -> None:
        self.assertEqual(len(VARA_LIST), VARA_COUNT)
        self.assertEqual(len(VARA_LIST), 7)

    def test_vara_order_and_names_are_correct(self) -> None:
        expected = (
            (1, "Sunday", "रविवार", "Ravivara", "sun"),
            (2, "Monday", "सोमवार", "Somavara", "moon"),
            (3, "Tuesday", "मंगलवार", "Mangalavara", "mars"),
            (4, "Wednesday", "बुधवार", "Budhavara", "mercury"),
            (5, "Thursday", "गुरुवार", "Guruvara", "jupiter"),
            (6, "Friday", "शुक्रवार", "Shukravara", "venus"),
            (7, "Saturday", "शनिवार", "Shanivara", "saturn"),
        )
        actual = tuple(
            (
                vara.index,
                vara.name_en,
                vara.name_hi,
                vara.name_sa,
                vara.ruling_planet,
            )
            for vara in VARA_LIST
        )

        self.assertEqual(actual, expected)

    def test_vara_definitions_are_frozen(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            VARA_LIST[0].name_en = "Changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
