"""Tests for Rashi constants."""

from __future__ import annotations

import math
import unittest

from backend.app.constants.rashi import (
    FULL_CIRCLE_DEGREES,
    RASHI_COUNT,
    RASHI_LIST,
    RASHI_SPAN_DEGREES,
)


class RashiConstantsTest(unittest.TestCase):
    """Validate immutable Rashi metadata."""

    def test_total_rashis_is_12(self) -> None:
        self.assertEqual(len(RASHI_LIST), RASHI_COUNT)
        self.assertEqual(len(RASHI_LIST), 12)

    def test_first_rashi_is_aries(self) -> None:
        first = RASHI_LIST[0]

        self.assertEqual(first.index, 1)
        self.assertEqual(first.english, "Aries")
        self.assertEqual(first.hindi, "मेष")
        self.assertEqual(first.sanskrit, "Mesha")
        self.assertEqual(first.lord, "Mars")
        self.assertEqual(first.element, "Fire")
        self.assertEqual(first.modality, "Movable")
        self.assertEqual(first.start_degree, 0.0)
        self.assertEqual(first.end_degree, 30.0)

    def test_last_rashi_is_pisces(self) -> None:
        last = RASHI_LIST[-1]

        self.assertEqual(last.index, 12)
        self.assertEqual(last.english, "Pisces")
        self.assertEqual(last.hindi, "मीन")
        self.assertEqual(last.sanskrit, "Meena")
        self.assertEqual(last.lord, "Jupiter")
        self.assertEqual(last.element, "Water")
        self.assertEqual(last.modality, "Dual")
        self.assertEqual(last.start_degree, 330.0)
        self.assertEqual(last.end_degree, 360.0)

    def test_each_span_is_thirty_degrees(self) -> None:
        for rashi in RASHI_LIST:
            span = rashi.end_degree - rashi.start_degree
            self.assertTrue(math.isclose(span, RASHI_SPAN_DEGREES))
            self.assertEqual(span, 30.0)

    def test_total_coverage_is_360_degrees(self) -> None:
        total_coverage = sum(
            rashi.end_degree - rashi.start_degree for rashi in RASHI_LIST
        )

        self.assertTrue(math.isclose(total_coverage, FULL_CIRCLE_DEGREES))

    def test_no_overlap_and_no_gap(self) -> None:
        self.assertEqual(RASHI_LIST[0].start_degree, 0.0)

        for previous, current in zip(RASHI_LIST, RASHI_LIST[1:]):
            self.assertEqual(previous.end_degree, current.start_degree)
            self.assertLess(previous.start_degree, previous.end_degree)
            self.assertEqual(current.index, previous.index + 1)

        self.assertEqual(RASHI_LIST[-1].end_degree, FULL_CIRCLE_DEGREES)


if __name__ == "__main__":
    unittest.main()
