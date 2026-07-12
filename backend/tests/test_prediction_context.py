"""Tests for flat Prediction Context Builder foundation."""

from __future__ import annotations

from copy import deepcopy
import json

from backend.app.prediction.context import build_prediction_context


def test_context_contains_lagna_keys() -> None:
    context = build_prediction_context(_sample_chart())

    assert context["lagna.house"] == 1
    assert context["lagna.rashi"] == "Mesha"
    assert context["lagna.rashi_index"] == 1
    assert context["lagna.degree"] == 12.5
    assert context["lagna.longitude"] == 12.5


def test_context_contains_planet_keys() -> None:
    context = build_prediction_context(_sample_chart())

    assert context["mars.house"] == 10
    assert context["mars.rashi"] == "Makara"
    assert context["mars.rashi_index"] == 10
    assert context["mars.degree"] == 8.25
    assert context["mars.motion_status"] == "direct"
    assert context["mars.is_retrograde"] is False
    assert context["mars.dignity.status"] == "exalted"
    assert context["mars.combustion.is_combust"] is False


def test_context_includes_optional_strength_when_present() -> None:
    context = build_prediction_context(
        _sample_chart(),
        {"strength": _sample_strength()},
    )

    assert context["jupiter.strength.percentage"] == 72.5
    assert context["jupiter.strength.status"] == "strong"
    assert context["jupiter.strength.summary_status"] == "favorable"
    assert "strength" not in context["metadata.missing_optional_components"]


def test_context_includes_optional_dasha_when_provided() -> None:
    context = build_prediction_context(
        _sample_chart(),
        {"dasha": _sample_dasha()},
    )

    assert context["dasha.mahadasha.lord"] == "Saturn"
    assert context["dasha.antardasha.lord"] == "Mercury"
    assert context["dasha.pratyantardasha.lord"] == "Venus"
    assert "dasha" not in context["metadata.missing_optional_components"]


def test_missing_fields_are_handled_safely() -> None:
    context = build_prediction_context({"planets": [{}, "bad"], "houses": [{}]})

    assert context["metadata.chart_data_available"] is True
    assert context["metadata.planet_count"] == 0
    assert context["metadata.house_count"] == 0
    assert "lagna.rashi" not in context
    assert "mars.house" not in context


def test_input_chart_data_is_not_mutated() -> None:
    chart_data = _sample_chart()
    original = deepcopy(chart_data)

    build_prediction_context(chart_data, {"strength": _sample_strength()})

    assert chart_data == original


def test_context_output_is_json_safe() -> None:
    context = build_prediction_context(
        {
            **_sample_chart(),
            "planets": [
                {
                    "planet": "Moon",
                    "sidereal_longitude": float("nan"),
                    "rashi": {"sanskrit": "Vrishabha", "index": 2},
                    "house_number": 2,
                }
            ],
        }
    )

    assert context["moon.longitude"] is None
    json.dumps(context)


def test_context_includes_yoga_presence_when_present() -> None:
    context = build_prediction_context(
        _sample_chart(),
        {
            "yogas": [
                {
                    "yoga_name": "Gajakesari Yoga",
                    "is_present": True,
                    "strength": "not_evaluated",
                }
            ]
        },
    )

    assert context["yoga.gajakesari_yoga.is_present"] is True
    assert context["yoga.gajakesari_yoga.strength"] == "not_evaluated"
    assert context["metadata.yoga_count"] == 1


def _sample_chart() -> dict[str, object]:
    mars = {
        "planet": "Mars",
        "sidereal_longitude": 278.25,
        "rashi": {"sanskrit": "Makara", "english": "Capricorn", "index": 10},
        "rashi_index": 10,
        "rashi_degree": 8.25,
        "house_number": 10,
        "motion_status": "direct",
        "is_retrograde": False,
        "dignity": {"status": "exalted", "is_exalted": True},
        "combustion": {"is_combust": False, "status": "not_combust"},
    }
    jupiter = {
        "planet": "Jupiter",
        "sidereal_longitude": 102.0,
        "rashi": {"sanskrit": "Karka", "english": "Cancer", "index": 4},
        "rashi_index": 4,
        "rashi_degree": 12.0,
        "house_number": 4,
    }

    return {
        "lagna": {
            "rashi": {"sanskrit": "Mesha", "english": "Aries", "index": 1},
            "rashi_index": 1,
            "rashi_degree": 12.5,
            "sidereal_longitude": 12.5,
        },
        "planets": [mars, jupiter],
        "houses": [
            {"house_number": 10, "planets": [mars]},
            {"house_number": 4, "planets": [jupiter]},
        ],
    }


def _sample_strength() -> dict[str, object]:
    return {
        "planets": [
            {
                "planet": "Jupiter",
                "shadbala": {
                    "strength_percentage": 72.5,
                    "status": "strong",
                },
                "summary_status": "favorable",
            }
        ]
    }


def _sample_dasha() -> dict[str, object]:
    return {
        "mahadasha": {
            "lord": "Saturn",
            "start_datetime": "2026-01-01T00:00:00",
            "end_datetime": "2045-01-01T00:00:00",
        },
        "antardasha": {
            "planet": "Mercury",
            "start_datetime": "2026-01-01T00:00:00",
            "end_datetime": "2028-01-01T00:00:00",
        },
        "pratyantardasha": {
            "dasha_lord": "Venus",
            "start_datetime": "2026-01-01T00:00:00",
            "end_datetime": "2026-06-01T00:00:00",
        },
    }
