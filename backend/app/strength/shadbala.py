"""Reusable Shadbala foundation constants and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

ShadbalaComponentName = Literal[
    "sthana_bala",
    "dig_bala",
    "kala_bala",
    "chesta_bala",
    "naisargika_bala",
    "drik_bala",
]

SHADBALA_STATUS_NOT_EVALUATED = "not_evaluated"


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
