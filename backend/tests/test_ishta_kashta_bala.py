"""Tests for Ishta/Kashta Bala foundation."""

from __future__ import annotations

import json

from backend.app.strength.ishta_kashta_bala import calculate_ishta_kashta_bala


def test_high_shadbala_gives_favorable_result() -> None:
    result = calculate_ishta_kashta_bala(
        "sun",
        {"strength_percentage": 80.0, "status": "strong"},
    )

    assert result["planet"] == "sun"
    assert result["ishta_score"] == 80.0
    assert result["kashta_score"] == 20.0
    assert result["total"] == 100.0
    assert result["status"] == "favorable"
    assert result["metadata"]["shadbala_status"] == "strong"


def test_low_shadbala_gives_challenging_result() -> None:
    result = calculate_ishta_kashta_bala(
        "saturn",
        {"strength_percentage": 25.0, "status": "weak"},
    )

    assert result["ishta_score"] == 25.0
    assert result["kashta_score"] == 75.0
    assert result["status"] == "challenging"


def test_exalted_dignity_improves_ishta() -> None:
    result = calculate_ishta_kashta_bala(
        "venus",
        {"strength_percentage": 50.0, "status": "average"},
        dignity_status="exalted",
    )

    assert result["ishta_score"] == 60.0
    assert result["kashta_score"] == 50.0
    assert result["status"] == "favorable"
    assert result["metadata"]["ishta_bonus"] == 10.0


def test_debilitated_dignity_improves_kashta() -> None:
    result = calculate_ishta_kashta_bala(
        "moon",
        {"strength_percentage": 50.0, "status": "average"},
        dignity_status="debilitated",
    )

    assert result["ishta_score"] == 50.0
    assert result["kashta_score"] == 60.0
    assert result["status"] == "challenging"
    assert result["metadata"]["kashta_bonus"] == 10.0


def test_missing_shadbala_returns_neutral_placeholder() -> None:
    result = calculate_ishta_kashta_bala("jupiter")

    assert result["ishta_score"] == 50.0
    assert result["kashta_score"] == 50.0
    assert result["total"] == 100.0
    assert result["status"] == "balanced"
    assert result["metadata"]["shadbala_status"] == "missing"
    assert result["metadata"]["strength_percentage"] == 50.0


def test_invalid_planet_is_handled_safely() -> None:
    result = calculate_ishta_kashta_bala(
        "pluto",
        {"strength_percentage": 80.0, "status": "strong"},
    )

    assert result["planet"] == "pluto"
    assert result["ishta_score"] == 0.0
    assert result["kashta_score"] == 0.0
    assert result["total"] == 0.0
    assert result["status"] == "unsupported"


def test_output_is_json_safe() -> None:
    result = calculate_ishta_kashta_bala(
        " Mercury ",
        {"strength_percentage": 61.91, "status": "average"},
        dignity_status="own_sign",
    )

    json.dumps(result)
