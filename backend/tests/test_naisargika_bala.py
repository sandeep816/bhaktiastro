"""Tests for Naisargika Bala foundation scoring."""

from __future__ import annotations

import json

from backend.app.strength.naisargika_bala import (
    NAISARGIKA_BALA_COMPONENT,
    NAISARGIKA_BALA_MAX_SCORE,
    calculate_naisargika_bala,
)


def test_sun_returns_sixty() -> None:
    result = calculate_naisargika_bala("sun")

    assert result == {
        "planet": "sun",
        "component": NAISARGIKA_BALA_COMPONENT,
        "status": "supported",
        "score": 60.0,
        "max_score": NAISARGIKA_BALA_MAX_SCORE,
        "reason": "Planet has a natural strength mapping.",
    }


def test_moon_returns_fifty_one_point_four_three() -> None:
    result = calculate_naisargika_bala("Moon")

    assert result["planet"] == "moon"
    assert result["status"] == "supported"
    assert result["score"] == 51.43


def test_saturn_returns_eight_point_five_seven() -> None:
    result = calculate_naisargika_bala(" Saturn ")

    assert result["planet"] == "saturn"
    assert result["status"] == "supported"
    assert result["score"] == 8.57


def test_unsupported_rahu_and_ketu_are_handled_safely() -> None:
    rahu_result = calculate_naisargika_bala("rahu")
    ketu_result = calculate_naisargika_bala("ketu")

    assert rahu_result["status"] == ketu_result["status"] == "unsupported"
    assert rahu_result["score"] == ketu_result["score"] == 0.0
    assert rahu_result["component"] == ketu_result["component"] == "naisargika_bala"


def test_invalid_planet_is_handled_safely() -> None:
    result = calculate_naisargika_bala("pluto")

    assert result["planet"] == "pluto"
    assert result["status"] == "unsupported"
    assert result["score"] == 0.0
    assert result["max_score"] == 60.0


def test_naisargika_bala_result_is_json_safe() -> None:
    result = calculate_naisargika_bala("venus")

    json.dumps(result)
