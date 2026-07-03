"""Reusable Shadbala foundation constants and helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Real
from typing import Any, Literal, TypedDict

from backend.app.strength.chesta_bala import calculate_chesta_bala
from backend.app.strength.dig_bala import calculate_dig_bala
from backend.app.strength.drik_bala import calculate_drik_bala
from backend.app.strength.kala_bala import calculate_kala_bala
from backend.app.strength.naisargika_bala import calculate_naisargika_bala
from backend.app.strength.sthana_bala import calculate_sthana_bala

ShadbalaComponentName = Literal[
    "sthana_bala",
    "dig_bala",
    "kala_bala",
    "chesta_bala",
    "naisargika_bala",
    "drik_bala",
]

SHADBALA_STATUS_NOT_EVALUATED = "not_evaluated"
SHADBALA_STATUS_STRONG = "strong"
SHADBALA_STATUS_AVERAGE = "average"
SHADBALA_STATUS_WEAK = "weak"
SHADBALA_STRONG_THRESHOLD_PERCENT = 70.0
SHADBALA_AVERAGE_THRESHOLD_PERCENT = 40.0
SHADBALA_SCORE_PRECISION = 2


@dataclass(frozen=True)
class ShadbalaComponentDefinition:
    """Immutable top-level Shadbala component definition."""

    name: ShadbalaComponentName
    label: str
    formula_status: str = SHADBALA_STATUS_NOT_EVALUATED


class ShadbalaComponentResult(TypedDict):
    """JSON-safe placeholder result for a single Shadbala component."""

    component: str
    label: str
    strength: float | None
    status: str
    subcomponents: dict[str, float | int | str | bool | None]
    metadata: dict[str, str]


class ShadbalaResult(TypedDict):
    """JSON-safe placeholder result for a planet's Shadbala summary."""

    planet: str
    total_strength: float | None
    components: dict[str, ShadbalaComponentResult]
    metadata: dict[str, str]


class ShadbalaAggregateResult(TypedDict):
    """JSON-safe aggregate result for foundation-level Shadbala."""

    planet: str
    total_strength: float
    max_strength: float
    strength_percentage: float
    components: dict[str, dict[str, Any]]
    status: str
    metadata: dict[str, Any]


SHADBALA_COMPONENTS: tuple[ShadbalaComponentDefinition, ...] = (
    ShadbalaComponentDefinition("sthana_bala", "Sthana Bala"),
    ShadbalaComponentDefinition("dig_bala", "Dig Bala"),
    ShadbalaComponentDefinition("kala_bala", "Kala Bala"),
    ShadbalaComponentDefinition("chesta_bala", "Chesta Bala"),
    ShadbalaComponentDefinition("naisargika_bala", "Naisargika Bala"),
    ShadbalaComponentDefinition("drik_bala", "Drik Bala"),
)


def _normalize_component_name(component_name: str) -> str:
    """Normalize a Shadbala component key or display label."""

    return "_".join(component_name.strip().casefold().replace("-", " ").split())


_SHADBALA_COMPONENTS_BY_NAME: dict[str, ShadbalaComponentDefinition] = {
    component.name: component for component in SHADBALA_COMPONENTS
}
_SHADBALA_COMPONENT_ALIASES: dict[str, str] = {
    component.name: component.name for component in SHADBALA_COMPONENTS
}
_SHADBALA_COMPONENT_ALIASES.update(
    {
        _normalize_component_name(component.label): component.name
        for component in SHADBALA_COMPONENTS
    }
)


def get_shadbala_components() -> tuple[ShadbalaComponentDefinition, ...]:
    """Return the supported top-level Shadbala component definitions."""

    return SHADBALA_COMPONENTS


def is_valid_shadbala_component(component_name: str) -> bool:
    """Return whether a component name is a supported Shadbala component."""

    if not isinstance(component_name, str):
        return False

    return _normalize_component_name(component_name) in _SHADBALA_COMPONENT_ALIASES


def create_empty_shadbala_result(planet: str) -> ShadbalaResult:
    """Create a JSON-safe Shadbala result without calculating strength."""

    return {
        "planet": str(planet).strip().casefold(),
        "total_strength": None,
        "components": {
            component.name: _create_empty_component_result(component)
            for component in SHADBALA_COMPONENTS
        },
        "metadata": {
            "status": SHADBALA_STATUS_NOT_EVALUATED,
            "calculation_status": "placeholder",
        },
    }


def calculate_shadbala(
    planet_data: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> ShadbalaAggregateResult:
    """Aggregate foundation-level Shadbala component scores.

    This helper composes existing Sprint 7 component foundations. It does not
    implement full classical Shadbala formulas.
    """

    source_planet_data = planet_data if isinstance(planet_data, Mapping) else {}
    source_context = context if isinstance(context, Mapping) else {}
    planet = _normalize_output_value(source_planet_data.get("planet"))

    components = {
        "sthana_bala": dict(
            calculate_sthana_bala(
                planet,
                _normalize_output_value(source_planet_data.get("rashi")),
            )
        ),
        "dig_bala": dict(
            calculate_dig_bala(
                planet,
                source_planet_data.get("house_number"),  # type: ignore[arg-type]
            )
        ),
        "kala_bala": dict(_calculate_kala_component(planet, source_context)),
        "chesta_bala": dict(
            calculate_chesta_bala(
                planet,
                speed_longitude=source_planet_data.get("speed_longitude"),
                motion_status=source_planet_data.get("motion_status"),
            )
        ),
        "naisargika_bala": dict(calculate_naisargika_bala(planet)),
        "drik_bala": dict(
            calculate_drik_bala(
                planet,
                source_planet_data.get("received_aspects"),
            )
        ),
    }
    total_strength = round(
        sum(
            _numeric_score(component.get("score")) for component in components.values()
        ),
        SHADBALA_SCORE_PRECISION,
    )
    max_strength = round(
        sum(
            _numeric_score(component.get("max_score"))
            for component in components.values()
        ),
        SHADBALA_SCORE_PRECISION,
    )
    strength_percentage = _calculate_strength_percentage(
        total_strength,
        max_strength,
    )

    return {
        "planet": planet,
        "total_strength": total_strength,
        "max_strength": max_strength,
        "strength_percentage": strength_percentage,
        "components": components,
        "status": _get_strength_status(strength_percentage),
        "metadata": {
            "calculation_status": "foundation",
            "component_count": len(components),
            "missing_scores_treated_as": 0,
        },
    }


def _create_empty_component_result(
    component: ShadbalaComponentDefinition,
) -> ShadbalaComponentResult:
    """Create the placeholder result shape for one Shadbala component."""

    return {
        "component": component.name,
        "label": component.label,
        "strength": None,
        "status": component.formula_status,
        "subcomponents": {},
        "metadata": {
            "calculation_status": "placeholder",
            "formula_status": component.formula_status,
        },
    }


def _calculate_kala_component(
    planet: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    """Return Kala Bala using context only when full time boundaries exist."""

    birth_datetime = context.get("birth_datetime")
    sunrise_datetime = context.get("sunrise_datetime")
    sunset_datetime = context.get("sunset_datetime")
    if birth_datetime is None or sunrise_datetime is None or sunset_datetime is None:
        return dict(calculate_kala_bala(planet, birth_datetime))

    return dict(
        calculate_kala_bala(
            planet,
            birth_datetime,
            sunrise_datetime=sunrise_datetime,
            sunset_datetime=sunset_datetime,
        )
    )


def _calculate_strength_percentage(
    total_strength: float,
    max_strength: float,
) -> float:
    """Return foundation strength percentage for aggregate Shadbala."""

    if max_strength <= 0:
        return 0.0

    return round(
        (total_strength / max_strength) * 100,
        SHADBALA_SCORE_PRECISION,
    )


def _get_strength_status(strength_percentage: float) -> str:
    """Return aggregate strength status from placeholder thresholds."""

    if strength_percentage >= SHADBALA_STRONG_THRESHOLD_PERCENT:
        return SHADBALA_STATUS_STRONG

    if strength_percentage >= SHADBALA_AVERAGE_THRESHOLD_PERCENT:
        return SHADBALA_STATUS_AVERAGE

    return SHADBALA_STATUS_WEAK


def _numeric_score(value: object) -> float:
    """Return numeric component score, treating missing values as zero."""

    if isinstance(value, bool) or not isinstance(value, Real):
        return 0.0

    return float(value)


def _normalize_output_value(value: object) -> str:
    """Normalize result display values without validating astrology metadata."""

    return str(value or "").strip().casefold()
