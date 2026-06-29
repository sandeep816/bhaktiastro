"""Tests for Nakshatra constants."""

from __future__ import annotations

import math
import unittest

from backend.app.constants.nakshatra import (
    FULL_CIRCLE_DEGREES,
    NAKSHATRA_COUNT,
    NAKSHATRA_LIST,
    NAKSHATRA_SPAN_DEGREES,
)


class NakshatraConstantsTest(unittest.TestCase):
    """Validate immutable Nakshatra metadata."""

    def test_total_nakshatras_is_27(self) -> None:
        self.assertEqual(len(NAKSHATRA_LIST), NAKSHATRA_COUNT)
        self.assertEqual(len(NAKSHATRA_LIST), 27)

    def test_first_nakshatra_is_ashwini(self) -> None:
        first = NAKSHATRA_LIST[0]

        self.assertEqual(first.index, 0)
        self.assertEqual(first.name_en, "Ashwini")
        self.assertEqual(first.name_hi, "अश्विनी")
        self.assertEqual(first.ruling_planet, "ketu")
        self.assertEqual(first.start_degree, 0.0)

    def test_last_nakshatra_is_revati(self) -> None:
        last = NAKSHATRA_LIST[-1]

        self.assertEqual(last.index, 26)
        self.assertEqual(last.name_en, "Revati")
        self.assertEqual(last.name_hi, "रेवती")
        self.assertEqual(last.ruling_planet, "mercury")
        self.assertTrue(math.isclose(last.end_degree, FULL_CIRCLE_DEGREES))

    def test_each_span_is_13_degrees_20_minutes(self) -> None:
        expected_span = 13.3333333333

        for nakshatra in NAKSHATRA_LIST:
            span = nakshatra.end_degree - nakshatra.start_degree
            self.assertTrue(math.isclose(span, expected_span, abs_tol=1e-10))
            self.assertTrue(
                math.isclose(span, NAKSHATRA_SPAN_DEGREES, abs_tol=1e-12)
            )

    def test_total_coverage_is_360_degrees(self) -> None:
        total_coverage = sum(
            nakshatra.end_degree - nakshatra.start_degree
            for nakshatra in NAKSHATRA_LIST
        )

        self.assertTrue(math.isclose(total_coverage, FULL_CIRCLE_DEGREES))

    def test_no_overlap_and_no_gap(self) -> None:
        self.assertEqual(NAKSHATRA_LIST[0].start_degree, 0.0)

        for previous, current in zip(NAKSHATRA_LIST, NAKSHATRA_LIST[1:]):
            self.assertTrue(
                math.isclose(previous.end_degree, current.start_degree)
            )
            self.assertLess(previous.start_degree, previous.end_degree)
            self.assertEqual(current.index, previous.index + 1)

        self.assertTrue(
            math.isclose(NAKSHATRA_LIST[-1].end_degree, FULL_CIRCLE_DEGREES)
        )


if __name__ == "__main__":
    unittest.main()
