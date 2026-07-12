"""Flat Prediction Context Builder foundation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Any


def build_prediction_context(
    chart_data: dict[str, Any],
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a flat JSON-safe rule-evaluation context from existing outputs.

    This helper only normalizes already-calculated Kundali and optional engine
    data. It does not calculate astrology, evaluate rules, or generate
    interpretation text.
    """

    source_chart = chart_data if isinstance(chart_data, Mapping) else {}
    source_extras = extras if isinstance(extras, Mapping) else {}
    context: dict[str, Any] = {}

    _add_lagna_context(context, source_chart.get("lagna"))
    planet_count = _add_planet_context(context, source_chart.get("planets"))
    house_count = _add_house_context(context, source_chart.get("houses"))
    yoga_count = _add_yoga_context(context, _get_optional_data(source_chart, source_extras, "yogas"))
    _add_strength_context(
        context,
        _get_optional_data(source_chart, source_extras, "strength"),
    )
    _add_dasha_context(context, _get_optional_data(source_chart, source_extras, "dasha"))

    optional_components = {
        "vargas": isinstance(_get_optional_data(source_chart, source_extras, "vargas"), Mapping),
        "dasha": isinstance(_get_optional_data(source_chart, source_extras, "dasha"), Mapping),
        "strength": isinstance(_get_optional_data(source_chart, source_extras, "strength"), Mapping),
        "ashtakavarga": isinstance(
            _get_optional_data(source_chart, source_extras, "ashtakavarga"),
            Mapping,
        ),
        "special_lagnas": isinstance(
            _get_optional_data(source_chart, source_extras, "special_lagnas"),
            Mapping,
        )
        or isinstance(_get_optional_data(source_chart, source_extras, "special_lagna"), Mapping),
        "yogas": yoga_count > 0,
    }

    context.update(
        {
            "metadata.component": "prediction_context",
            "metadata.calculation_status": "foundation",
            "metadata.chart_data_available": isinstance(chart_data, Mapping),
            "metadata.planet_count": planet_count,
            "metadata.house_count": house_count,
            "metadata.yoga_count": yoga_count,
            "metadata.missing_optional_components": [
                name for name, available in optional_components.items() if not available
            ],
        }
    )
    _add_legacy_context_fields(
        context,
        source_chart,
        chart_data_available=isinstance(chart_data, Mapping),
        planet_count=planet_count,
        house_count=house_count,
    )

    return {key: _make_json_safe(value) for key, value in context.items()}


def _add_lagna_context(context: dict[str, Any], lagna_data: object) -> None:
    """Add flat Lagna values when available."""

    if not isinstance(lagna_data, Mapping):
        return

    context["lagna.house"] = 1
    _set_if_present(context, "lagna.rashi", _extract_rashi_name(lagna_data.get("rashi")))
    _set_if_present(context, "lagna.rashi_index", _extract_rashi_index(lagna_data))
    _set_if_present(context, "lagna.degree", _extract_degree(lagna_data))
    _set_if_present(
        context,
        "lagna.longitude",
        _first_present(
            lagna_data,
            "sidereal_longitude",
            "ascendant_longitude",
            "longitude",
        ),
    )


def _add_planet_context(context: dict[str, Any], planets_data: object) -> int:
    """Add flat planet values and return the usable planet count."""

    if not isinstance(planets_data, Sequence) or isinstance(planets_data, (str, bytes)):
        return 0

    planet_count = 0
    for planet_data in planets_data:
        if not isinstance(planet_data, Mapping):
            continue

        planet_key = _normalize_key(planet_data.get("planet"))
        if not planet_key:
            continue

        planet_count += 1
        _set_if_present(context, f"{planet_key}.house", planet_data.get("house_number"))
        _set_if_present(context, f"{planet_key}.house_index", planet_data.get("house_index"))
        _set_if_present(context, f"{planet_key}.rashi", _extract_rashi_name(planet_data.get("rashi")))
        _set_if_present(context, f"{planet_key}.rashi_index", _extract_rashi_index(planet_data))
        _set_if_present(context, f"{planet_key}.degree", _extract_degree(planet_data))
        _set_if_present(
            context,
            f"{planet_key}.longitude",
            planet_data.get("sidereal_longitude", planet_data.get("longitude")),
        )
        _set_if_present(context, f"{planet_key}.motion_status", planet_data.get("motion_status"))
        _set_if_present(context, f"{planet_key}.is_retrograde", planet_data.get("is_retrograde"))
        _add_optional_mapping_value(
            context,
            f"{planet_key}.dignity",
            planet_data.get("dignity"),
            ("status", "dignity_status", "is_exalted", "is_debilitated"),
        )
        _add_optional_mapping_value(
            context,
            f"{planet_key}.combustion",
            planet_data.get("combustion"),
            ("status", "is_combust", "combustion_status"),
        )

    return planet_count


def _add_house_context(context: dict[str, Any], houses_data: object) -> int:
    """Add minimal flat house occupancy values."""

    if not isinstance(houses_data, Sequence) or isinstance(houses_data, (str, bytes)):
        return 0

    house_count = 0
    for house_data in houses_data:
        if not isinstance(house_data, Mapping):
            continue
        house_number = house_data.get("house_number")
        if not isinstance(house_number, Integral) or isinstance(house_number, bool):
            continue

        house_count += 1
        prefix = f"house.{int(house_number)}"
        context[f"{prefix}.planet_count"] = len(_extract_house_planets(house_data))
        context[f"{prefix}.planets"] = _extract_house_planets(house_data)

    return house_count


def _add_strength_context(context: dict[str, Any], strength_data: object) -> None:
    """Add planet strength percentages from optional strength summary output."""

    if not isinstance(strength_data, Mapping):
        return

    planets = strength_data.get("planets")
    if not isinstance(planets, Sequence) or isinstance(planets, (str, bytes)):
        return

    for planet_entry in planets:
        if not isinstance(planet_entry, Mapping):
            continue

        planet_key = _normalize_key(planet_entry.get("planet"))
        if not planet_key:
            continue

        shadbala = planet_entry.get("shadbala")
        if isinstance(shadbala, Mapping):
            _set_if_present(
                context,
                f"{planet_key}.strength.percentage",
                shadbala.get("strength_percentage"),
            )
            _set_if_present(
                context,
                f"{planet_key}.strength.status",
                shadbala.get("status"),
            )
        _set_if_present(
            context,
            f"{planet_key}.strength.summary_status",
            planet_entry.get("summary_status"),
        )


def _add_dasha_context(context: dict[str, Any], dasha_data: object) -> None:
    """Add current Dasha lords from optional Dasha output."""

    if not isinstance(dasha_data, Mapping):
        return

    for key, prefix in (
        ("mahadasha", "dasha.mahadasha"),
        ("antardasha", "dasha.antardasha"),
        ("pratyantardasha", "dasha.pratyantardasha"),
    ):
        period = dasha_data.get(key)
        if not isinstance(period, Mapping):
            continue

        _set_if_present(
            context,
            f"{prefix}.lord",
            _first_present(period, "lord", "planet", "dasha_lord"),
        )
        _set_if_present(context, f"{prefix}.start_datetime", period.get("start_datetime"))
        _set_if_present(context, f"{prefix}.end_datetime", period.get("end_datetime"))


def _add_yoga_context(context: dict[str, Any], yogas_data: object) -> int:
    """Add key yoga presence flags when yoga results are present."""

    if not isinstance(yogas_data, Sequence) or isinstance(yogas_data, (str, bytes)):
        return 0

    yoga_count = 0
    for yoga in yogas_data:
        if not isinstance(yoga, Mapping):
            continue
        yoga_key = _normalize_key(yoga.get("yoga_name") or yoga.get("name"))
        if not yoga_key:
            continue

        yoga_count += 1
        _set_if_present(context, f"yoga.{yoga_key}.is_present", yoga.get("is_present"))
        _set_if_present(context, f"yoga.{yoga_key}.strength", yoga.get("strength"))

    return yoga_count


def _add_legacy_context_fields(
    context: dict[str, Any],
    chart_data: Mapping[str, Any],
    *,
    chart_data_available: bool,
    planet_count: int,
    house_count: int,
) -> None:
    """Preserve the internal nested context fields used before flat keys."""

    optional_components = {
        "vargas": isinstance(chart_data.get("vargas"), Mapping),
        "strength": isinstance(chart_data.get("strength"), Mapping),
        "ashtakavarga": isinstance(chart_data.get("ashtakavarga"), Mapping),
        "special_lagna": isinstance(chart_data.get("special_lagna"), Mapping),
    }
    context["planets"] = _extract_legacy_planets(chart_data.get("planets"))
    context["houses"] = _extract_legacy_houses(chart_data.get("houses"))
    context["optional_components"] = optional_components
    context["metadata"] = {
        "calculation_status": "foundation",
        "component": "prediction_context",
        "chart_data_available": chart_data_available,
        "planet_count": planet_count,
        "house_count": house_count,
        "missing_optional_components": [
            name for name, available in optional_components.items() if not available
        ],
    }


def _extract_legacy_planets(planets_data: object) -> list[dict[str, Any]]:
    """Return the pre-flat planet context list for internal compatibility."""

    if not isinstance(planets_data, Sequence) or isinstance(planets_data, (str, bytes)):
        return []

    planets: list[dict[str, Any]] = []
    for planet_data in planets_data:
        if not isinstance(planet_data, Mapping):
            continue
        planet_key = _normalize_key(planet_data.get("planet"))
        if not planet_key:
            continue
        planets.append(
            {
                "planet": planet_key,
                "house_number": planet_data.get("house_number"),
                "rashi": _extract_rashi_name(planet_data.get("rashi")),
                "rashi_index": _extract_rashi_index(planet_data),
                "sidereal_longitude": planet_data.get("sidereal_longitude"),
                "motion_status": planet_data.get("motion_status"),
            }
        )

    return planets


def _extract_legacy_houses(houses_data: object) -> list[dict[str, Any]]:
    """Return the pre-flat house context list for internal compatibility."""

    if not isinstance(houses_data, Sequence) or isinstance(houses_data, (str, bytes)):
        return []

    houses: list[dict[str, Any]] = []
    for house_data in houses_data:
        if not isinstance(house_data, Mapping):
            continue
        houses.append(
            {
                "house_number": house_data.get("house_number"),
                "planet_names": _extract_house_planets(house_data),
            }
        )

    return houses


def _add_optional_mapping_value(
    context: dict[str, Any],
    prefix: str,
    source: object,
    keys: tuple[str, ...],
) -> None:
    """Copy selected scalar values from optional nested mapping metadata."""

    if not isinstance(source, Mapping):
        return

    for key in keys:
        _set_if_present(context, f"{prefix}.{key}", source.get(key))


def _get_optional_data(
    chart_data: Mapping[str, Any],
    extras: Mapping[str, Any],
    key: str,
) -> object:
    """Read optional data from extras first, then chart data."""

    if key in extras:
        return extras[key]
    return chart_data.get(key)


def _extract_house_planets(house_data: Mapping[str, Any]) -> list[str]:
    """Extract normalized planet names from a house entry."""

    planets = house_data.get("planets")
    if not isinstance(planets, Sequence) or isinstance(planets, (str, bytes)):
        return []

    names: list[str] = []
    for planet_data in planets:
        if not isinstance(planet_data, Mapping):
            continue
        planet_name = _normalize_key(planet_data.get("planet"))
        if planet_name:
            names.append(planet_name)

    return names


def _extract_rashi_name(rashi_data: object) -> str | None:
    """Extract a stable Rashi name from chart-style metadata."""

    if isinstance(rashi_data, str) and rashi_data.strip():
        return rashi_data.strip()

    if not isinstance(rashi_data, Mapping):
        return None

    for key in ("sanskrit", "english", "hindi", "name"):
        value = rashi_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _extract_rashi_index(source: Mapping[str, Any]) -> object:
    """Extract Rashi index from direct or nested chart metadata."""

    if "rashi_index" in source:
        return source.get("rashi_index")

    rashi = source.get("rashi")
    if isinstance(rashi, Mapping):
        return rashi.get("index", rashi.get("rashi_index"))

    return None


def _extract_degree(source: Mapping[str, Any]) -> object:
    """Extract Rashi degree from direct metadata or longitude fallback."""

    for key in ("rashi_degree", "degree"):
        if key in source:
            return source.get(key)

    longitude = _first_present(source, "sidereal_longitude", "ascendant_longitude")
    if isinstance(longitude, Real) and not isinstance(longitude, bool):
        return round(float(longitude) % 30.0, 6)

    return None


def _first_present(source: Mapping[str, Any], *keys: str) -> object:
    """Return the first non-None value for the given keys."""

    for key in keys:
        value = source.get(key)
        if value is not None:
            return value
    return None


def _set_if_present(context: dict[str, Any], key: str, value: object) -> None:
    """Set a context key only when the value is present."""

    if value is not None:
        context[key] = value


def _normalize_key(value: object) -> str:
    """Normalize free-form names into dot-key-safe lowercase identifiers."""

    return str(value or "").strip().casefold().replace(" ", "_")


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
