"""Internal Prediction Framework assembly helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any, TypedDict

from backend.app.prediction.composer import PredictionComposition
from backend.app.prediction.composer import compose_predictions


class PredictionFrameworkOutput(TypedDict):
    """JSON-safe internal Prediction Framework output."""

    context: dict[str, Any]
    rule_results: list[dict[str, Any]]
    predictions: PredictionComposition
    metadata: dict[str, Any]


def build_prediction_framework_output(
    chart_data: Mapping[str, Any],
    rules: Sequence[Mapping[str, Any]] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> PredictionFrameworkOutput:
    """Build internal Prediction Framework output without real prediction rules."""

    context = build_prediction_context(chart_data)
    rule_results = evaluate_prediction_rules(rules or [], context)
    predictions = compose_predictions(
        rule_results,
        metadata={
            "calculation_status": "foundation",
            "component": "prediction_composer",
            "rules_evaluated": len(rule_results),
        },
    )

    return {
        "context": context,
        "rule_results": rule_results,
        "predictions": predictions,
        "metadata": _create_metadata(chart_data, rules, metadata),
    }


def build_prediction_context(chart_data: Mapping[str, Any]) -> dict[str, Any]:
    """Build a JSON-safe prediction context from existing Kundali chart data."""

    source_chart = chart_data if isinstance(chart_data, Mapping) else {}
    planets = _extract_planets(source_chart.get("planets"))
    houses = _extract_houses(source_chart.get("houses"))
    optional_components = {
        "vargas": isinstance(source_chart.get("vargas"), Mapping),
        "strength": isinstance(source_chart.get("strength"), Mapping),
        "ashtakavarga": isinstance(source_chart.get("ashtakavarga"), Mapping),
        "special_lagna": isinstance(source_chart.get("special_lagna"), Mapping),
    }

    return {
        "lagna": _extract_lagna(source_chart.get("lagna")),
        "planets": planets,
        "houses": houses,
        "optional_components": optional_components,
        "metadata": {
            "calculation_status": "foundation",
            "component": "prediction_context",
            "chart_data_available": isinstance(chart_data, Mapping),
            "planet_count": len(planets),
            "house_count": len(houses),
            "missing_optional_components": [
                name for name, available in optional_components.items() if not available
            ],
        },
    }


def evaluate_prediction_rules(
    rules: Sequence[Mapping[str, Any]],
    context: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Evaluate prediction rules.

    Sprint 10A.8 intentionally keeps the rule list empty. The helper exists as
    the internal integration boundary for a future Rule Engine and returns a
    JSON-safe empty result set until real rules are introduced.
    """

    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)):
        return []

    if not isinstance(context, Mapping):
        return []

    return []


def _extract_lagna(lagna_data: object) -> dict[str, Any]:
    """Extract JSON-safe Lagna context."""

    if not isinstance(lagna_data, Mapping):
        return {
            "available": False,
            "rashi_index": None,
            "rashi": None,
            "sidereal_longitude": None,
        }

    rashi = lagna_data.get("rashi")
    return {
        "available": True,
        "rashi_index": _make_json_safe(lagna_data.get("rashi_index")),
        "rashi": _extract_rashi_name(rashi),
        "sidereal_longitude": _make_json_safe(
            lagna_data.get(
                "sidereal_longitude",
                lagna_data.get("ascendant_longitude"),
            )
        ),
    }


def _extract_planets(planets_data: object) -> list[dict[str, Any]]:
    """Extract JSON-safe planet context from chart planet data."""

    if not isinstance(planets_data, Sequence) or isinstance(planets_data, (str, bytes)):
        return []

    planets: list[dict[str, Any]] = []
    for planet_data in planets_data:
        if not isinstance(planet_data, Mapping):
            continue
        planets.append(
            {
                "planet": _normalize_text(planet_data.get("planet")),
                "house_number": _make_json_safe(planet_data.get("house_number")),
                "rashi": _extract_rashi_name(planet_data.get("rashi")),
                "rashi_index": _make_json_safe(planet_data.get("rashi_index")),
                "sidereal_longitude": _make_json_safe(
                    planet_data.get("sidereal_longitude")
                ),
                "motion_status": _normalize_optional_text(
                    planet_data.get("motion_status")
                ),
            }
        )

    return planets


def _extract_houses(houses_data: object) -> list[dict[str, Any]]:
    """Extract JSON-safe house context from chart house data."""

    if not isinstance(houses_data, Sequence) or isinstance(houses_data, (str, bytes)):
        return []

    houses: list[dict[str, Any]] = []
    for house_data in houses_data:
        if not isinstance(house_data, Mapping):
            continue
        planets = house_data.get("planets")
        houses.append(
            {
                "house_number": _make_json_safe(house_data.get("house_number")),
                "planet_names": _extract_planet_names(planets),
            }
        )

    return houses


def _extract_planet_names(planets_data: object) -> list[str]:
    """Extract planet names from a house planet list."""

    if not isinstance(planets_data, Sequence) or isinstance(planets_data, (str, bytes)):
        return []

    names: list[str] = []
    for planet_data in planets_data:
        if not isinstance(planet_data, Mapping):
            continue
        planet_name = _normalize_text(planet_data.get("planet"))
        if planet_name:
            names.append(planet_name)

    return names


def _extract_rashi_name(rashi_data: object) -> str | None:
    """Extract a normalized Rashi name when available."""

    if not isinstance(rashi_data, Mapping):
        return None

    for key in ("english", "sanskrit", "hindi"):
        rashi_name = _normalize_optional_text(rashi_data.get(key))
        if rashi_name:
            return rashi_name

    return None


def _create_metadata(
    chart_data: object,
    rules: object,
    metadata: object,
) -> dict[str, Any]:
    """Create JSON-safe Prediction Framework metadata."""

    source_metadata = metadata if isinstance(metadata, Mapping) else {}
    normalized_metadata = {
        str(key): _make_json_safe(value) for key, value in source_metadata.items()
    }
    normalized_metadata.setdefault("calculation_status", "foundation")
    normalized_metadata.setdefault("component", "prediction_framework")
    normalized_metadata["chart_data_available"] = isinstance(chart_data, Mapping)
    normalized_metadata["rules_count"] = (
        len(rules)
        if isinstance(rules, Sequence) and not isinstance(rules, (str, bytes))
        else 0
    )
    normalized_metadata["real_prediction_rules_enabled"] = False
    return normalized_metadata


def _normalize_text(value: object) -> str:
    """Normalize a text value into a lowercase key."""

    return str(value or "").strip().casefold()


def _normalize_optional_text(value: object) -> str | None:
    """Normalize optional text into a JSON-safe string or None."""

    if value is None:
        return None

    normalized = _normalize_text(value)
    return normalized or None


def _make_json_safe(value: object) -> Any:
    """Return a JSON-safe scalar or nested value."""

    if value is None or isinstance(value, (str, bool)):
        return value

    if isinstance(value, Real):
        if isinstance(value, bool):
            return value
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            return None
        if isinstance(value, Integral):
            return int(value)
        return numeric_value

    if isinstance(value, Mapping):
        return {str(key): _make_json_safe(nested) for key, nested in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_make_json_safe(item) for item in value]

    return str(value)
