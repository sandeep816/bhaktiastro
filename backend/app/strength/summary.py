"""Planet strength summary builder."""

from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral, Real
from typing import Any, TypedDict

from backend.app.strength.ishta_kashta_bala import calculate_ishta_kashta_bala
from backend.app.strength.shadbala import calculate_shadbala

SUMMARY_CALCULATION_STATUS = "foundation"
SUMMARY_RANKING_BASIS = "shadbala.strength_percentage"
SUMMARY_STHANA_DIGNITY_STATUSES = frozenset(
    {"exalted", "mooltrikona", "own_sign", "debilitated"}
)


class PlanetStrengthRankingEntry(TypedDict):
    """JSON-safe ranking entry for one planet."""

    planet: str
    strength_percentage: float
    total_strength: float
    summary_status: str


class PlanetStrengthEntry(TypedDict):
    """JSON-safe planet strength summary entry."""

    planet: str
    shadbala: dict[str, Any]
    ishta_kashta: dict[str, Any]
    summary_status: str


class PlanetStrengthSummary(TypedDict):
    """JSON-safe planet strength summary result."""

    planets: list[PlanetStrengthEntry]
    ranking: list[PlanetStrengthRankingEntry]
    strongest_planet: str | None
    weakest_planet: str | None
    metadata: dict[str, int | str]


def build_planet_strength_summary(
    chart_data: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> PlanetStrengthSummary:
    """Build a foundation-level strength summary for chart planets.

    This helper composes existing Shadbala and Ishta/Kashta foundations. It
    does not mutate Kundali chart data and does not expose strength through any
    public API surface.
    """

    source_chart = chart_data if isinstance(chart_data, Mapping) else {}
    source_context = context if isinstance(context, Mapping) else {}
    source_planets = _get_chart_planets(source_chart)

    planet_entries: list[PlanetStrengthEntry] = []
    skipped_entries = 0
    for planet_data in source_planets:
        if not isinstance(planet_data, Mapping):
            skipped_entries += 1
            continue

        shadbala_input = _build_shadbala_input(planet_data, source_planets)
        shadbala_result = dict(calculate_shadbala(shadbala_input, dict(source_context)))
        dignity_status = _get_dignity_status(shadbala_result)
        ishta_kashta_result = dict(
            calculate_ishta_kashta_bala(
                shadbala_input["planet"],
                shadbala_result,
                dignity_status=dignity_status,
            )
        )
        summary_status = _get_summary_status(shadbala_result, ishta_kashta_result)

        planet_entries.append(
            {
                "planet": shadbala_input["planet"],
                "shadbala": shadbala_result,
                "ishta_kashta": ishta_kashta_result,
                "summary_status": summary_status,
            }
        )

    ranking = _build_ranking(planet_entries)

    return {
        "planets": planet_entries,
        "ranking": ranking,
        "strongest_planet": ranking[0]["planet"] if ranking else None,
        "weakest_planet": ranking[-1]["planet"] if ranking else None,
        "metadata": {
            "calculation_status": SUMMARY_CALCULATION_STATUS,
            "ranking_basis": SUMMARY_RANKING_BASIS,
            "source_planet_count": len(source_planets),
            "planet_count": len(planet_entries),
            "skipped_entries": skipped_entries,
        },
    }


def _get_chart_planets(chart_data: Mapping[str, Any]) -> list[Any]:
    """Return chart planet entries when present."""

    planets = chart_data.get("planets")
    if not isinstance(planets, list):
        return []

    return planets


def _build_shadbala_input(
    planet_data: Mapping[str, Any],
    chart_planets: list[Any],
) -> dict[str, Any]:
    """Translate chart planet metadata into Shadbala aggregate input."""

    return {
        "planet": _normalize_text(planet_data.get("planet")),
        "rashi": _get_rashi_value(planet_data),
        "house_number": _get_house_number(planet_data.get("house_number")),
        "speed_longitude": _get_speed_longitude(planet_data),
        "motion_status": _normalize_optional_text(planet_data.get("motion_status")),
        "received_aspects": _get_received_aspects(planet_data, chart_planets),
    }


def _get_rashi_value(planet_data: Mapping[str, Any]) -> str:
    """Return a Shadbala-friendly Rashi value from chart planet metadata."""

    rashi = planet_data.get("rashi")
    if isinstance(rashi, Mapping):
        for key in ("sanskrit", "english", "hindi", "name"):
            value = rashi.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        index = rashi.get("index")
        if isinstance(index, Integral) and not isinstance(index, bool):
            return str(int(index))

    if isinstance(rashi, str):
        return rashi.strip()

    for key in ("rashi_name", "rashi_sanskrit", "rashi_english", "rashi_hindi"):
        value = planet_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    rashi_index = planet_data.get("rashi_index")
    if isinstance(rashi_index, Integral) and not isinstance(rashi_index, bool):
        return str(int(rashi_index))

    return ""


def _get_house_number(value: object) -> int | None:
    """Return a safe one-based house number, or None."""

    if isinstance(value, bool) or not isinstance(value, Integral):
        return None

    house_number = int(value)
    if not 1 <= house_number <= 12:
        return None

    return house_number


def _get_speed_longitude(planet_data: Mapping[str, Any]) -> float | None:
    """Return speed metadata from chart or component-style keys."""

    value = planet_data.get("speed_longitude")
    if value is None:
        value = planet_data.get("speed")

    if isinstance(value, bool) or not isinstance(value, Real):
        return None

    return float(value)


def _get_received_aspects(
    target_planet: Mapping[str, Any],
    chart_planets: list[Any],
) -> list[dict[str, Any]]:
    """Return explicit or chart-derived received aspect placeholders."""

    explicit_aspects = target_planet.get("received_aspects")
    if isinstance(explicit_aspects, list):
        return explicit_aspects

    target_house = _get_house_number(target_planet.get("house_number"))
    if target_house is None:
        return []

    received_aspects: list[dict[str, Any]] = []
    for source_planet in chart_planets:
        if source_planet is target_planet or not isinstance(source_planet, Mapping):
            continue

        source_aspects = source_planet.get("aspects")
        if not isinstance(source_aspects, Mapping):
            continue

        aspected_houses = source_aspects.get("aspected_houses")
        if not isinstance(aspected_houses, list):
            continue

        if target_house not in {
            int(house)
            for house in aspected_houses
            if isinstance(house, Integral) and not isinstance(house, bool)
        }:
            continue

        from_planet = _normalize_text(source_planet.get("planet"))
        if not from_planet:
            continue

        received_aspects.append(
            {
                "from_planet": from_planet,
                "aspect_type": "graha_drishti",
                "strength": None,
            }
        )

    return received_aspects


def _get_dignity_status(shadbala_result: Mapping[str, Any]) -> str | None:
    """Use Sthana Bala status as the foundation dignity signal."""

    components = shadbala_result.get("components")
    if not isinstance(components, Mapping):
        return None

    sthana_bala = components.get("sthana_bala")
    if not isinstance(sthana_bala, Mapping):
        return None

    status = _normalize_optional_text(sthana_bala.get("status"))
    if status in SUMMARY_STHANA_DIGNITY_STATUSES:
        return status

    return None


def _get_summary_status(
    shadbala_result: Mapping[str, Any],
    ishta_kashta_result: Mapping[str, Any],
) -> str:
    """Return the planet summary status from composed foundation helpers."""

    ishta_status = _normalize_optional_text(ishta_kashta_result.get("status"))
    if ishta_status == "unsupported":
        return "unsupported"

    return _normalize_text(shadbala_result.get("status") or "weak")


def _build_ranking(
    planet_entries: list[PlanetStrengthEntry],
) -> list[PlanetStrengthRankingEntry]:
    """Return planets ranked by Shadbala strength percentage descending."""

    ranking = [
        {
            "planet": entry["planet"],
            "strength_percentage": _get_numeric(
                entry["shadbala"].get("strength_percentage")
            ),
            "total_strength": _get_numeric(entry["shadbala"].get("total_strength")),
            "summary_status": entry["summary_status"],
        }
        for entry in planet_entries
    ]
    return sorted(
        ranking,
        key=lambda entry: entry["strength_percentage"],
        reverse=True,
    )


def _get_numeric(value: object) -> float:
    """Return a JSON-safe numeric value for ranking fields."""

    if isinstance(value, bool) or not isinstance(value, Real):
        return 0.0

    return float(value)


def _normalize_text(value: object) -> str:
    """Normalize text output without validating astrology metadata."""

    return str(value or "").strip().casefold()


def _normalize_optional_text(value: object) -> str | None:
    """Normalize optional text into a JSON-safe string or None."""

    if value is None:
        return None

    normalized_value = _normalize_text(value)
    return normalized_value or None
