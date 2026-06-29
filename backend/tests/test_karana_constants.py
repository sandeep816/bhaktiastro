"""Tests for Karana constants."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from backend.app.constants.karana import (
    FIXED_KARANA_TYPE,
    FIXED_KARANAS,
    KARANA_COUNT,
    KARANA_LIST,
    REPEATING_KARANA_TYPE,
    REPEATING_KARANAS,
)


class KaranaConstantsTest(unittest.TestCase):
    """Validate immutable Karana metadata."""

    def test_total_karanas_is_11(self) -> None:
        self.assertEqual(len(KARANA_LIST), KARANA_COUNT)
        self.assertEqual(len(KARANA_LIST), 11)

    def test_repeating_karanas_total_is_7(self) -> None:
        self.assertEqual(len(REPEATING_KARANAS), 7)
        self.assertTrue(
            all(karana.type == REPEATING_KARANA_TYPE for karana in REPEATING_KARANAS)
        )

    def test_fixed_karanas_total_is_4(self) -> None:
        self.assertEqual(len(FIXED_KARANAS), 4)
        self.assertTrue(
            all(karana.type == FIXED_KARANA_TYPE for karana in FIXED_KARANAS)
        )

    def test_names_are_correct(self) -> None:
        expected_names = (
            ("Bava", "बव", "Bava"),
            ("Balava", "बालव", "Balava"),
            ("Kaulava", "कौलव", "Kaulava"),
            ("Taitila", "तैतिल", "Taitila"),
            ("Gara", "गर", "Gara"),
            ("Vanija", "वणिज", "Vanija"),
            ("Vishti (Bhadra)", "विष्टि (भद्रा)", "Vishti"),
            ("Shakuni", "शकुनि", "Shakuni"),
            ("Chatushpada", "चतुष्पाद", "Chatushpada"),
            ("Naga", "नाग", "Naga"),
            ("Kimstughna", "किंस्तुघ्न", "Kimstughna"),
        )

        actual_names = tuple(
            (karana.name_en, karana.name_hi, karana.name_sa)
            for karana in KARANA_LIST
        )

        self.assertEqual(actual_names, expected_names)

    def test_order_matches_traditional_panchang(self) -> None:
        expected_order = (
            "Bava",
            "Balava",
            "Kaulava",
            "Taitila",
            "Gara",
            "Vanija",
            "Vishti (Bhadra)",
            "Shakuni",
            "Chatushpada",
            "Naga",
            "Kimstughna",
        )

        self.assertEqual(
            tuple(karana.name_en for karana in KARANA_LIST),
            expected_order,
        )
        self.assertEqual(tuple(karana.index for karana in KARANA_LIST), tuple(range(1, 12)))

    def test_karana_definitions_are_frozen(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            KARANA_LIST[0].name_en = "Changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
