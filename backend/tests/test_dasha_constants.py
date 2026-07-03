"""Tests for Dasha constants."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from backend.app.constants.dasha import (
    VIMSHOTTARI_DASHA_SEQUENCE,
    VIMSHOTTARI_TOTAL_CYCLE_YEARS,
    get_dasha_duration,
    get_dasha_sequence,
    get_total_cycle_years,
)


class DashaConstantsTest(unittest.TestCase):
    """Validate Vimshottari Dasha constants and helpers."""

    def test_vimshottari_sequence_order_is_classical(self) -> None:
        self.assertEqual(
            get_dasha_sequence(),
            (
                "ketu",
                "venus",
                "sun",
                "moon",
                "mars",
                "rahu",
                "jupiter",
                "saturn",
                "mercury",
            ),
        )

    def test_vimshottari_duration_lookup_returns_years(self) -> None:
        expected = {
            "ketu": 7,
            "venus": 20,
            "sun": 6,
            "moon": 10,
            "mars": 7,
            "rahu": 18,
            "jupiter": 16,
            "saturn": 19,
            "mercury": 17,
        }

        for planet, duration in expected.items():
            self.assertEqual(get_dasha_duration(planet), duration)

    def test_vimshottari_duration_lookup_normalizes_planet_name(self) -> None:
        self.assertEqual(get_dasha_duration(" Venus "), 20)
        self.assertEqual(get_dasha_duration("SATURN"), 19)

    def test_invalid_dasha_duration_lookup_fails_safely(self) -> None:
        with self.assertRaises(ValueError):
            get_dasha_duration("earth")

        with self.assertRaises(ValueError):
            get_dasha_duration("")

        with self.assertRaises(TypeError):
            get_dasha_duration(None)  # type: ignore[arg-type]

    def test_total_vimshottari_cycle_is_120_years(self) -> None:
        self.assertEqual(get_total_cycle_years(), VIMSHOTTARI_TOTAL_CYCLE_YEARS)
        self.assertEqual(get_total_cycle_years(), 120)

    def test_dasha_definitions_are_frozen(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            VIMSHOTTARI_DASHA_SEQUENCE[0].planet = "changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
