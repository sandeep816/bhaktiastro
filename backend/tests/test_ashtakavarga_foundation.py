"""Tests for Ashtakavarga foundation constants and helpers."""

from __future__ import annotations

import json

import pytest

from backend.app.ashtakavarga.constants import (
    ASHTAKAVARGA_BINDU_VALUE,
    ASHTAKAVARGA_HOUSE_COUNT,
    ASHTAKAVARGA_HOUSES,
    ASHTAKAVARGA_REKHA_VALUE,
    ASHTAKAVARGA_STATUS_NOT_EVALUATED,
    create_empty_bindu_row,
    get_ashtakavarga_planets,
    is_ashtakavarga_planet,
    normalize_ashtakavarga_house,
)


def test_supported_planet_list_contains_classical_seven_planets() -> None:
    assert get_ashtakavarga_planets() == (
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    )
    assert ASHTAKAVARGA_HOUSE_COUNT == 12
    assert ASHTAKAVARGA_HOUSES == tuple(range(1, 13))
    assert ASHTAKAVARGA_BINDU_VALUE == 1
    assert ASHTAKAVARGA_REKHA_VALUE == 0


def test_valid_planet_lookup_works() -> None:
    assert is_ashtakavarga_planet("sun") is True
    assert is_ashtakavarga_planet(" Moon ") is True
    assert is_ashtakavarga_planet("SATURN") is True


def test_unsupported_rahu_ketu_are_handled_safely() -> None:
    assert is_ashtakavarga_planet("rahu") is False
    assert is_ashtakavarga_planet("ketu") is False
    assert create_empty_bindu_row("rahu")["metadata"]["supported_planet"] is False
    assert create_empty_bindu_row("ketu")["metadata"]["supported_planet"] is False


def test_invalid_planet_lookup_is_handled_safely() -> None:
    assert is_ashtakavarga_planet("pluto") is False
    assert is_ashtakavarga_planet("") is False
    assert is_ashtakavarga_planet(None) is False  # type: ignore[arg-type]


def test_house_normalization_wraps_into_one_to_twelve() -> None:
    assert normalize_ashtakavarga_house(1) == 1
    assert normalize_ashtakavarga_house(12) == 12
    assert normalize_ashtakavarga_house(13) == 1
    assert normalize_ashtakavarga_house(0) == 12
    assert normalize_ashtakavarga_house(-1) == 11
    assert normalize_ashtakavarga_house(25) == 1


def test_invalid_house_normalization_raises_safely() -> None:
    with pytest.raises(TypeError):
        normalize_ashtakavarga_house("1")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        normalize_ashtakavarga_house(True)  # type: ignore[arg-type]


def test_empty_bindu_row_is_json_safe() -> None:
    result = create_empty_bindu_row(" Sun ")

    assert result["planet"] == "sun"
    assert set(result) == {"planet", "houses", "total_bindus", "metadata"}
    assert result["houses"] == {
        house_number: ASHTAKAVARGA_REKHA_VALUE
        for house_number in ASHTAKAVARGA_HOUSES
    }
    assert result["total_bindus"] == 0
    assert result["metadata"] == {
        "calculation_status": "placeholder",
        "formula_status": ASHTAKAVARGA_STATUS_NOT_EVALUATED,
        "supported_planet": True,
        "house_count": ASHTAKAVARGA_HOUSE_COUNT,
    }

    json.dumps(result)
