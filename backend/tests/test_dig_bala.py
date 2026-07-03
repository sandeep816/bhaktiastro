"""Tests for Dig Bala foundation scoring."""

from __future__ import annotations

import json

from backend.app.strength.dig_bala import (
    DIG_BALA_COMPONENT,
    DIG_BALA_MAX_SCORE,
    calculate_dig_bala,
)


def test_jupiter_in_house_one_gets_strongest_score() -> None:
    result = calculate_dig_bala("jupiter", 1)

    assert result == {
        "planet": "jupiter",
        "house_number": 1,
        "component": DIG_BALA_COMPONENT,
        "status": "strongest_direction",
        "score": 60,
        "max_score": DIG_BALA_MAX_SCORE,
        "reason": "Planet is in its strongest directional house.",
    }


def test_venus_in_house_four_gets_strongest_score() -> None:
    result = calculate_dig_bala("venus", 4)

    assert result["status"] == "strongest_direction"
    assert result["score"] == 60


def test_saturn_in_house_seven_gets_strongest_score() -> None:
    result = calculate_dig_bala("saturn", 7)

    assert result["status"] == "strongest_direction"
    assert result["score"] == 60


def test_sun_in_house_ten_gets_strongest_score() -> None:
    result = calculate_dig_bala("sun", 10)

    assert result["status"] == "strongest_direction"
    assert result["score"] == 60


def test_opposite_house_gives_weakest_score() -> None:
    result = calculate_dig_bala("sun", 4)

    assert result["status"] == "weakest_direction"
    assert result["score"] == 0


def test_other_supported_house_gives_middle_score() -> None:
    result = calculate_dig_bala("mars", 2)

    assert result["status"] == "other_direction"
    assert result["score"] == 30


def test_invalid_planet_is_handled_safely() -> None:
    result = calculate_dig_bala("rahu", 1)

    assert result["planet"] == "rahu"
    assert result["house_number"] == 1
    assert result["component"] == "dig_bala"
    assert result["status"] == "invalid_input"
    assert result["score"] is None


def test_invalid_house_is_handled_safely() -> None:
    result = calculate_dig_bala("jupiter", 13)

    assert result["planet"] == "jupiter"
    assert result["house_number"] is None
    assert result["status"] == "invalid_input"
    assert result["score"] is None


def test_non_integer_house_is_handled_safely() -> None:
    result = calculate_dig_bala("jupiter", "1")  # type: ignore[arg-type]

    assert result["house_number"] is None
    assert result["status"] == "invalid_input"


def test_dig_bala_result_is_json_safe() -> None:
    result = calculate_dig_bala(" Mercury ", 1)

    json.dumps(result)
