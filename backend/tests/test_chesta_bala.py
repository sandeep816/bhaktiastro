"""Tests for Chesta Bala foundation scoring."""

from __future__ import annotations

import json

from backend.app.strength.chesta_bala import (
    CHESTA_BALA_COMPONENT,
    CHESTA_BALA_MAX_SCORE,
    calculate_chesta_bala,
)


def test_retrograde_planet_gets_strongest_score() -> None:
    result = calculate_chesta_bala("mars", motion_status="retrograde")

    assert result == {
        "planet": "mars",
        "component": CHESTA_BALA_COMPONENT,
        "motion_status": "retrograde",
        "status": "retrograde",
        "score": 60,
        "max_score": CHESTA_BALA_MAX_SCORE,
        "reason": "Planet has retrograde longitudinal motion.",
    }


def test_stationary_planet_gets_medium_score() -> None:
    result = calculate_chesta_bala("venus", motion_status="stationary")

    assert result["motion_status"] == "stationary"
    assert result["status"] == "stationary"
    assert result["score"] == 45


def test_direct_planet_gets_normal_score() -> None:
    result = calculate_chesta_bala("jupiter", motion_status="direct")

    assert result["motion_status"] == "direct"
    assert result["status"] == "direct"
    assert result["score"] == 30


def test_speed_longitude_derives_retrograde_motion_status() -> None:
    result = calculate_chesta_bala("saturn", speed_longitude=-0.25)

    assert result["motion_status"] == "retrograde"
    assert result["status"] == "retrograde"
    assert result["score"] == 60


def test_speed_longitude_derives_stationary_motion_status() -> None:
    result = calculate_chesta_bala("mercury", speed_longitude=0.0)

    assert result["motion_status"] == "stationary"
    assert result["status"] == "stationary"
    assert result["score"] == 45


def test_motion_status_takes_precedence_over_speed_longitude() -> None:
    result = calculate_chesta_bala(
        "saturn",
        speed_longitude=-0.25,
        motion_status="direct",
    )

    assert result["motion_status"] == "direct"
    assert result["status"] == "direct"
    assert result["score"] == 30


def test_sun_and_moon_are_handled_safely() -> None:
    sun_result = calculate_chesta_bala("sun", motion_status="retrograde")
    moon_result = calculate_chesta_bala("moon", speed_longitude=-0.1)

    assert sun_result["status"] == "unsupported"
    assert moon_result["status"] == "unsupported"
    assert sun_result["score"] == moon_result["score"] == 0
    assert sun_result["motion_status"] == moon_result["motion_status"] == "unknown"


def test_invalid_planet_is_handled_safely() -> None:
    result = calculate_chesta_bala("rahu", motion_status="retrograde")

    assert result["planet"] == "rahu"
    assert result["component"] == "chesta_bala"
    assert result["motion_status"] == "unknown"
    assert result["status"] == "unsupported"
    assert result["score"] == 0


def test_missing_motion_data_is_handled_safely() -> None:
    result = calculate_chesta_bala("mars")

    assert result["planet"] == "mars"
    assert result["motion_status"] == "unknown"
    assert result["status"] == "unknown"
    assert result["score"] == 0


def test_invalid_motion_data_is_handled_safely() -> None:
    result = calculate_chesta_bala("mars", motion_status="slow")

    assert result["motion_status"] == "unknown"
    assert result["status"] == "unknown"
    assert result["score"] == 0


def test_chesta_bala_result_is_json_safe() -> None:
    result = calculate_chesta_bala(" Saturn ", speed_longitude=-0.25)

    json.dumps(result)
