"""Tests for reusable astronomy boundary search helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from backend.app.astronomy.search import find_next_longitude_boundary


class LongitudeBoundarySearchTest(unittest.TestCase):
    """Validate binary search over continuously changing angular values."""

    def test_finds_next_boundary_for_increasing_value(self) -> None:
        start = datetime(2026, 6, 29, 0, 0, tzinfo=timezone.utc)

        def value_at(moment: datetime) -> float:
            hours = (moment - start).total_seconds() / 3600
            return 10.0 + hours

        result = find_next_longitude_boundary(
            start,
            value_at,
            15.0,
            tolerance=timedelta(minutes=1),
        )

        expected = start + timedelta(hours=5)
        self.assertLessEqual(abs((result - expected).total_seconds()), 60)

    def test_finds_boundary_across_zero_degrees(self) -> None:
        start = datetime(2026, 6, 29, 0, 0, tzinfo=timezone.utc)

        def value_at(moment: datetime) -> float:
            hours = (moment - start).total_seconds() / 3600
            return 350.0 + (hours * 2.0)

        result = find_next_longitude_boundary(
            start,
            value_at,
            0.0,
            tolerance=timedelta(minutes=1),
        )

        expected = start + timedelta(hours=5)
        self.assertLessEqual(abs((result - expected).total_seconds()), 60)

    def test_raises_when_boundary_is_not_found(self) -> None:
        start = datetime(2026, 6, 29, 0, 0, tzinfo=timezone.utc)

        def value_at(moment: datetime) -> float:
            return 10.0

        with self.assertRaisesRegex(RuntimeError, "not found"):
            find_next_longitude_boundary(
                start,
                value_at,
                12.0,
                max_search=timedelta(hours=1),
                search_step=timedelta(minutes=15),
            )

    def test_naive_start_datetime_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            find_next_longitude_boundary(
                datetime(2026, 6, 29, 0, 0),
                lambda moment: 0.0,
                12.0,
            )


if __name__ == "__main__":
    unittest.main()
