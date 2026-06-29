"""Tests for Panchang Yoga constants."""

from __future__ import annotations

import math
import unittest

from backend.app.constants.yoga import (
    FULL_CIRCLE_DEGREES,
    YOGA_COUNT,
    YOGA_LIST,
    YOGA_SPAN_DEGREES,
)


class YogaConstantsTest(unittest.TestCase):
    """Validate immutable Panchang Yoga metadata."""

    def test_total_yogas_is_27(self) -> None:
        self.assertEqual(len(YOGA_LIST), YOGA_COUNT)
        self.assertEqual(len(YOGA_LIST), 27)

    def test_first_yoga_is_vishkambha(self) -> None:
        first = YOGA_LIST[0]

        self.assertEqual(first.index, 1)
        self.assertEqual(first.name_en, "Vishkambha")
        self.assertEqual(first.name_hi, "विष्कम्भ")
        self.assertEqual(first.name_sa, "Vishkambha")
        self.assertEqual(first.start_degree, 0.0)

    def test_last_yoga_is_vaidhriti(self) -> None:
        last = YOGA_LIST[-1]

        self.assertEqual(last.index, 27)
        self.assertEqual(last.name_en, "Vaidhriti")
        self.assertEqual(last.name_hi, "वैधृति")
        self.assertEqual(last.name_sa, "Vaidhriti")
        self.assertTrue(math.isclose(last.end_degree, FULL_CIRCLE_DEGREES))

    def test_each_span_is_13_degrees_20_minutes(self) -> None:
        expected_span = 13.3333333333

        for yoga in YOGA_LIST:
            span = yoga.end_degree - yoga.start_degree
            self.assertTrue(math.isclose(span, expected_span, abs_tol=1e-10))
            self.assertTrue(math.isclose(span, YOGA_SPAN_DEGREES, abs_tol=1e-12))

    def test_total_coverage_is_360_degrees(self) -> None:
        total_coverage = sum(yoga.end_degree - yoga.start_degree for yoga in YOGA_LIST)

        self.assertTrue(math.isclose(total_coverage, FULL_CIRCLE_DEGREES))

    def test_no_overlap_and_no_gap(self) -> None:
        self.assertEqual(YOGA_LIST[0].start_degree, 0.0)

        for previous, current in zip(YOGA_LIST, YOGA_LIST[1:]):
            self.assertTrue(math.isclose(previous.end_degree, current.start_degree))
            self.assertLess(previous.start_degree, previous.end_degree)
            self.assertEqual(current.index, previous.index + 1)

        self.assertTrue(math.isclose(YOGA_LIST[-1].end_degree, FULL_CIRCLE_DEGREES))


if __name__ == "__main__":
    unittest.main()
