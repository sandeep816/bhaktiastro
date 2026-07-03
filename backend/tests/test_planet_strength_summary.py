"""Tests for Planet Strength Summary builder."""

from __future__ import annotations

import json
from typing import Any

from backend.app.strength.summary import build_planet_strength_summary


def test_summary_contains_planets() -> None:
    result = build_planet_strength_summary(_sample_chart())

    assert len(result["planets"]) == 3
    assert all(
        {"planet", "shadbala", "ishta_kashta", "summary_status"} <= set(entry)
        for entry in result["planets"]
    )
    assert result["metadata"]["planet_count"] == 3


def test_ranking_is_generated_by_strength_percentage_descending() -> None:
    result = build_planet_strength_summary(_sample_chart())

    ranking = result["ranking"]
    percentages = [entry["strength_percentage"] for entry in ranking]

    assert [entry["planet"] for entry in ranking] == ["sun", "venus", "saturn"]
    assert percentages == sorted(percentages, reverse=True)


def test_strongest_planet_is_detected() -> None:
    result = build_planet_strength_summary(_sample_chart())

    assert result["strongest_planet"] == "sun"


def test_weakest_planet_is_detected() -> None:
    result = build_planet_strength_summary(_sample_chart())

    assert result["weakest_planet"] == "saturn"


def test_missing_data_is_handled_safely() -> None:
    result = build_planet_strength_summary({})

    assert result["planets"] == []
    assert result["ranking"] == []
    assert result["strongest_planet"] is None
    assert result["weakest_planet"] is None
    assert result["metadata"]["planet_count"] == 0
    assert result["metadata"]["source_planet_count"] == 0


def test_invalid_planet_entries_are_skipped_safely() -> None:
    result = build_planet_strength_summary({"planets": ["not-a-planet"]})

    assert result["planets"] == []
    assert result["metadata"]["source_planet_count"] == 1
    assert result["metadata"]["skipped_entries"] == 1


def test_output_is_json_safe() -> None:
    result = build_planet_strength_summary(_sample_chart())

    json.dumps(result)


def _sample_chart() -> dict[str, list[dict[str, Any]]]:
    return {
        "planets": [
            {
                "planet": "sun",
                "rashi": {"sanskrit": "Mesha", "english": "Aries", "index": 1},
                "house_number": 10,
                "aspects": {"aspected_houses": [4]},
            },
            {
                "planet": "venus",
                "rashi": {"sanskrit": "Vrishabha", "english": "Taurus", "index": 2},
                "house_number": 4,
                "motion_status": "direct",
                "aspects": {"aspected_houses": [10]},
            },
            {
                "planet": "saturn",
                "rashi": {"sanskrit": "Mesha", "english": "Aries", "index": 1},
                "house_number": 1,
                "motion_status": "retrograde",
                "aspects": {"aspected_houses": [3, 7, 10]},
            },
        ]
    }
