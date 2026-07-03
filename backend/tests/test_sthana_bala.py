"""Tests for Sthana Bala foundation scoring."""

from __future__ import annotations

import json

from backend.app.strength.sthana_bala import (
    STHANA_BALA_COMPONENT,
    STHANA_BALA_MAX_SCORE,
    calculate_sthana_bala,
)


def test_exalted_planet_returns_highest_score() -> None:
    result = calculate_sthana_bala("sun", "Mesha")

    assert result == {
        "planet": "sun",
        "rashi": "mesha",
        "component": STHANA_BALA_COMPONENT,
        "status": "exalted",
        "score": 60,
        "max_score": STHANA_BALA_MAX_SCORE,
        "reason": "Planet is in its exaltation sign.",
    }


def test_debilitated_planet_returns_lowest_score() -> None:
    result = calculate_sthana_bala("mars", "Karka")

    assert result["status"] == "debilitated"
    assert result["score"] == 0
    assert result["max_score"] == 60


def test_own_sign_returns_own_sign_status() -> None:
    result = calculate_sthana_bala("venus", "Vrishabha")

    assert result["status"] == "own_sign"
    assert result["score"] == 30


def test_mooltrikona_returns_mooltrikona_status() -> None:
    result = calculate_sthana_bala("jupiter", "Dhanu")

    assert result["status"] == "mooltrikona"
    assert result["score"] == 45


def test_neutral_supported_sign_returns_neutral_score() -> None:
    result = calculate_sthana_bala("jupiter", "Tula")

    assert result["status"] == "neutral"
    assert result["score"] == 15


def test_invalid_planet_is_handled_safely() -> None:
    result = calculate_sthana_bala("rahu", "Mesha")

    assert result["planet"] == "rahu"
    assert result["rashi"] == "mesha"
    assert result["status"] == "invalid_input"
    assert result["score"] is None
    assert result["component"] == "sthana_bala"


def test_invalid_rashi_is_handled_safely() -> None:
    result = calculate_sthana_bala("sun", "Atlantis")

    assert result["planet"] == "sun"
    assert result["rashi"] == "atlantis"
    assert result["status"] == "invalid_input"
    assert result["score"] is None


def test_sthana_bala_result_is_json_safe() -> None:
    result = calculate_sthana_bala(" Venus ", " Vrishabha ")

    json.dumps(result)
