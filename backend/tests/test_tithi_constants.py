"""Tests for Tithi constants."""

from __future__ import annotations

import math
import unittest

from backend.app.constants.tithi import (
    FULL_CIRCLE_DEGREES,
    KRISHNA_PAKSHA,
    SHUKLA_PAKSHA,
    TITHI_COUNT,
    TITHI_LIST,
    TITHI_SPAN_DEGREES,
)


class TithiConstantsTest(unittest.TestCase):
    """Validate immutable Tithi metadata."""

    def test_total_tithis_is_30(self) -> None:
        self.assertEqual(len(TITHI_LIST), TITHI_COUNT)
        self.assertEqual(len(TITHI_LIST), 30)

    def test_tithi_one_is_shukla_pratipada(self) -> None:
        first = TITHI_LIST[0]

        self.assertEqual(first.number, 1)
        self.assertEqual(first.name_en, "Pratipada")
        self.assertEqual(first.name_hi, "प्रतिपदा")
        self.assertEqual(first.name_sa, "Pratipada")
        self.assertEqual(first.paksha, SHUKLA_PAKSHA)
        self.assertEqual(first.start_angle, 0.0)
        self.assertEqual(first.end_angle, 12.0)

    def test_tithi_fifteen_is_purnima(self) -> None:
        purnima = TITHI_LIST[14]

        self.assertEqual(purnima.number, 15)
        self.assertEqual(purnima.name_en, "Purnima")
        self.assertEqual(purnima.name_hi, "पूर्णिमा")
        self.assertEqual(purnima.name_sa, "Purnima")
        self.assertEqual(purnima.paksha, SHUKLA_PAKSHA)

    def test_tithi_sixteen_is_krishna_pratipada(self) -> None:
        first_krishna = TITHI_LIST[15]

        self.assertEqual(first_krishna.number, 16)
        self.assertEqual(first_krishna.name_en, "Pratipada")
        self.assertEqual(first_krishna.name_hi, "प्रतिपदा")
        self.assertEqual(first_krishna.name_sa, "Pratipada")
        self.assertEqual(first_krishna.paksha, KRISHNA_PAKSHA)

    def test_tithi_thirty_is_amavasya(self) -> None:
        amavasya = TITHI_LIST[29]

        self.assertEqual(amavasya.number, 30)
        self.assertEqual(amavasya.name_en, "Amavasya")
        self.assertEqual(amavasya.name_hi, "अमावस्या")
        self.assertEqual(amavasya.name_sa, "Amavasya")
        self.assertEqual(amavasya.paksha, KRISHNA_PAKSHA)
        self.assertTrue(math.isclose(amavasya.end_angle, FULL_CIRCLE_DEGREES))

    def test_each_span_is_12_degrees(self) -> None:
        self.assertEqual(TITHI_SPAN_DEGREES, 12.0)

        for tithi in TITHI_LIST:
            span = tithi.end_angle - tithi.start_angle
            self.assertTrue(math.isclose(span, TITHI_SPAN_DEGREES))

    def test_total_coverage_is_360_degrees(self) -> None:
        total_coverage = sum(
            tithi.end_angle - tithi.start_angle for tithi in TITHI_LIST
        )

        self.assertTrue(math.isclose(total_coverage, FULL_CIRCLE_DEGREES))

    def test_no_overlap_and_no_gap(self) -> None:
        self.assertEqual(TITHI_LIST[0].start_angle, 0.0)

        for previous, current in zip(TITHI_LIST, TITHI_LIST[1:]):
            self.assertTrue(math.isclose(previous.end_angle, current.start_angle))
            self.assertLess(previous.start_angle, previous.end_angle)
            self.assertEqual(current.number, previous.number + 1)

        self.assertTrue(math.isclose(TITHI_LIST[-1].end_angle, FULL_CIRCLE_DEGREES))


if __name__ == "__main__":
    unittest.main()
