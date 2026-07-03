"""Tests for Shadbala foundation constants and helpers."""

from __future__ import annotations

import json

from backend.app.strength.shadbala import (
    SHADBALA_STATUS_NOT_EVALUATED,
    create_empty_shadbala_result,
    get_shadbala_components,
    is_valid_shadbala_component,
)


def test_component_list_contains_six_components() -> None:
    components = get_shadbala_components()

    assert len(components) == 6
    assert [component.name for component in components] == [
        "sthana_bala",
        "dig_bala",
        "kala_bala",
        "chesta_bala",
        "naisargika_bala",
        "drik_bala",
    ]


def test_valid_component_lookup_works() -> None:
    assert is_valid_shadbala_component("sthana_bala") is True
    assert is_valid_shadbala_component("Sthana Bala") is True
    assert is_valid_shadbala_component("naisargika-bala") is True


def test_invalid_component_lookup_is_handled_safely() -> None:
    assert is_valid_shadbala_component("unknown_bala") is False
    assert is_valid_shadbala_component("") is False
    assert is_valid_shadbala_component(None) is False  # type: ignore[arg-type]


def test_empty_shadbala_result_is_json_safe() -> None:
    result = create_empty_shadbala_result(" Sun ")

    assert result["planet"] == "sun"
    assert result["total_strength"] is None
    assert set(result) == {"planet", "total_strength", "components", "metadata"}
    assert set(result["components"]) == {
        "sthana_bala",
        "dig_bala",
        "kala_bala",
        "chesta_bala",
        "naisargika_bala",
        "drik_bala",
    }
    assert all(
        component["status"] == SHADBALA_STATUS_NOT_EVALUATED
        and component["strength"] is None
        and component["subcomponents"] == {}
        for component in result["components"].values()
    )

    json.dumps(result)
