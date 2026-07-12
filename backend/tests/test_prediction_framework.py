"""Tests for internal Prediction Framework assembly helpers."""

from __future__ import annotations

import json

from backend.app.prediction.framework import build_prediction_context
from backend.app.prediction.framework import build_prediction_framework_output
from backend.app.prediction.framework import evaluate_prediction_rules


def test_prediction_context_is_built_from_chart_data() -> None:
    context = build_prediction_context(_sample_chart())

    assert context["lagna.rashi"] == "Aries"
    assert context["lagna.rashi_index"] == 1
    assert context["sun.house"] == 1
    assert context["moon.rashi"] == "Taurus"
    assert context["metadata.planet_count"] == 2
    assert context["metadata.house_count"] == 2


def test_empty_rule_list_returns_empty_structured_predictions() -> None:
    result = build_prediction_framework_output(_sample_chart(), rules=[])

    assert result["rule_results"] == []
    assert result["predictions"]["categories"] == {}
    assert result["predictions"]["summary"]["total_rules"] == 0
    assert result["predictions"]["summary"]["categories_count"] == 0
    assert result["metadata"]["real_prediction_rules_enabled"] is False


def test_missing_optional_engine_data_is_handled_safely() -> None:
    result = build_prediction_framework_output(_sample_chart())

    assert result["context"]["metadata.missing_optional_components"] == [
        "vargas",
        "dasha",
        "strength",
        "ashtakavarga",
        "special_lagnas",
        "yogas",
    ]


def test_prediction_framework_output_is_json_safe() -> None:
    result = build_prediction_framework_output(_sample_chart())

    json.dumps(result)


def test_evaluate_prediction_rules_is_empty_until_rules_exist() -> None:
    result = evaluate_prediction_rules(
        [{"id": "future_rule"}],
        {"metadata": {"component": "prediction_context"}},
    )

    assert result == []


def _sample_chart() -> dict[str, object]:
    sun = {
        "planet": "sun",
        "sidereal_longitude": 10.0,
        "rashi_index": 1,
        "rashi": {"english": "Aries"},
        "house_number": 1,
    }
    moon = {
        "planet": "moon",
        "sidereal_longitude": 40.0,
        "rashi_index": 2,
        "rashi": {"english": "Taurus"},
        "house_number": 2,
    }

    return {
        "lagna": {
            "rashi_index": 1,
            "rashi": {"english": "Aries"},
            "sidereal_longitude": 23.25,
        },
        "planets": [sun, moon],
        "houses": [
            {"house_number": 1, "planets": [sun]},
            {"house_number": 2, "planets": [moon]},
        ],
    }
