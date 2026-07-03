"""Tests for Shadbala aggregator foundation."""

from __future__ import annotations

import json
from datetime import datetime

from backend.app.strength.shadbala import calculate_shadbala


def test_aggregation_includes_all_six_components() -> None:
    result = calculate_shadbala(
        {
            "planet": "sun",
            "rashi": "Mesha",
            "house_number": 10,
            "received_aspects": [{"from_planet": "jupiter"}],
        }
    )

    assert set(result["components"]) == {
        "sthana_bala",
        "dig_bala",
        "kala_bala",
        "chesta_bala",
        "naisargika_bala",
        "drik_bala",
    }


def test_total_strength_and_percentage_are_calculated() -> None:
    result = calculate_shadbala(
        {
            "planet": "sun",
            "rashi": "Mesha",
            "house_number": 10,
            "received_aspects": [
                {"from_planet": "jupiter"},
                {"from_planet": "venus"},
                {"from_planet": "mercury"},
                {"from_planet": "moon"},
            ],
        },
        {
            "birth_datetime": datetime(2026, 6, 29, 12, 0),
            "sunrise_datetime": datetime(2026, 6, 29, 6, 0),
            "sunset_datetime": datetime(2026, 6, 29, 18, 0),
        },
    )

    assert result["total_strength"] == 300.0
    assert result["max_strength"] == 360.0
    assert result["strength_percentage"] == 83.33
    assert result["status"] == "strong"


def test_missing_optional_data_is_handled_safely() -> None:
    result = calculate_shadbala({"planet": "venus"})

    assert result["components"]["sthana_bala"]["status"] == "invalid_input"
    assert result["components"]["dig_bala"]["status"] == "invalid_input"
    assert result["components"]["kala_bala"]["status"] == "neutral"
    assert result["components"]["chesta_bala"]["status"] == "unknown"
    assert result["components"]["drik_bala"]["status"] == "neutral"
    assert result["total_strength"] == 72.86
    assert result["strength_percentage"] == 20.24
    assert result["status"] == "weak"


def test_average_status_threshold_works() -> None:
    result = calculate_shadbala(
        {
            "planet": "venus",
            "rashi": "Vrishabha",
            "house_number": 4,
            "motion_status": "direct",
        },
        {
            "birth_datetime": datetime(2026, 6, 29, 12, 0),
            "sunrise_datetime": datetime(2026, 6, 29, 6, 0),
            "sunset_datetime": datetime(2026, 6, 29, 18, 0),
        },
    )

    assert result["total_strength"] == 222.86
    assert result["strength_percentage"] == 61.91
    assert result["status"] == "average"


def test_unsupported_planet_returns_weak_safe_aggregate() -> None:
    result = calculate_shadbala({"planet": "rahu"})

    assert result["planet"] == "rahu"
    assert result["total_strength"] == 0.0
    assert result["strength_percentage"] == 0.0
    assert result["status"] == "weak"
    assert result["metadata"]["component_count"] == 6


def test_shadbala_aggregate_output_is_json_safe() -> None:
    result = calculate_shadbala(
        {
            "planet": " Moon ",
            "rashi": "Vrishabha",
            "house_number": 4,
            "received_aspects": [{"from_planet": "jupiter", "strength": True}],
        }
    )

    json.dumps(result)
