"""Tests for Dasha timeline builder."""

from __future__ import annotations

from datetime import datetime
import json
import unittest

from backend.app.dasha.builder import build_dasha_timeline


class DashaTimelineBuilderTest(unittest.TestCase):
    """Validate composed Dasha timeline builder output."""

    def test_builder_returns_mahadasha_timeline(self) -> None:
        result = build_dasha_timeline(
            birth_datetime=datetime(2000, 1, 1),
            nakshatra_index=0,
            moon_longitude=0.0,
            include_antardasha=False,
        )

        self.assertEqual(result["birth_datetime"], "2000-01-01T00:00:00")
        self.assertIsNone(result["target_datetime"])
        self.assertIsNone(result["current_dasha"])
        self.assertGreater(len(result["mahadasha_timeline"]), 0)
        self.assertEqual(result["mahadasha_timeline"][0]["dasha_lord"], "ketu")
        self.assertNotIn("antardashas", result["mahadasha_timeline"][0])

    def test_include_antardasha_attaches_antardashas(self) -> None:
        result = build_dasha_timeline(
            birth_datetime=datetime(2000, 1, 1),
            nakshatra_index=0,
            moon_longitude=0.0,
            include_antardasha=True,
        )

        first_mahadasha = result["mahadasha_timeline"][0]

        self.assertIn("antardashas", first_mahadasha)
        self.assertEqual(len(first_mahadasha["antardashas"]), 9)
        self.assertEqual(first_mahadasha["antardashas"][0]["antardasha_lord"], "ketu")
        self.assertNotIn("pratyantardashas", first_mahadasha["antardashas"][0])

    def test_include_pratyantardasha_attaches_pratyantardashas(self) -> None:
        result = build_dasha_timeline(
            birth_datetime=datetime(2000, 1, 1),
            nakshatra_index=0,
            moon_longitude=0.0,
            include_antardasha=True,
            include_pratyantardasha=True,
        )

        first_antardasha = result["mahadasha_timeline"][0]["antardashas"][0]

        self.assertIn("pratyantardashas", first_antardasha)
        self.assertEqual(len(first_antardasha["pratyantardashas"]), 9)
        self.assertEqual(
            first_antardasha["pratyantardashas"][0]["pratyantardasha_lord"],
            "ketu",
        )

    def test_target_datetime_returns_current_dasha(self) -> None:
        result = build_dasha_timeline(
            birth_datetime=datetime(2000, 1, 1),
            nakshatra_index=0,
            moon_longitude=0.0,
            target_datetime=datetime(2000, 1, 1),
            include_antardasha=True,
            include_pratyantardasha=True,
        )

        self.assertEqual(result["target_datetime"], "2000-01-01T00:00:00")
        self.assertIsNotNone(result["current_dasha"])
        self.assertEqual(result["current_dasha"]["mahadasha"]["dasha_lord"], "ketu")
        self.assertEqual(
            result["current_dasha"]["antardasha"]["antardasha_lord"],
            "ketu",
        )
        self.assertEqual(
            result["current_dasha"]["pratyantardasha"]["pratyantardasha_lord"],
            "ketu",
        )

    def test_metadata_exists_and_output_is_json_safe(self) -> None:
        result = build_dasha_timeline(
            birth_datetime="2000-01-01T00:00:00+05:30",
            nakshatra_index=0,
            moon_longitude=0.0,
            include_antardasha=False,
        )

        self.assertEqual(result["metadata"]["engine"], "dasha")
        self.assertEqual(result["metadata"]["system"], "vimshottari")
        self.assertEqual(result["birth_datetime"], "2000-01-01T00:00:00+05:30")
        json.dumps(result)

    def test_invalid_input_is_handled_safely(self) -> None:
        with self.assertRaises(TypeError):
            build_dasha_timeline(
                birth_datetime=123,  # type: ignore[arg-type]
                nakshatra_index=0,
                moon_longitude=0.0,
            )

        with self.assertRaises(ValueError):
            build_dasha_timeline(
                birth_datetime=datetime(2000, 1, 1),
                nakshatra_index=27,
                moon_longitude=0.0,
            )

        with self.assertRaises(ValueError):
            build_dasha_timeline(
                birth_datetime=datetime(2000, 1, 1),
                nakshatra_index=0,
                moon_longitude=0.0,
                target_datetime="not-a-date",
            )


if __name__ == "__main__":
    unittest.main()
