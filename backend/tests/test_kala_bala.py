"""Tests for Kala Bala foundation scoring."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from backend.app.strength.kala_bala import (
    KALA_BALA_COMPONENT,
    KALA_BALA_MAX_SCORE,
    calculate_kala_bala,
)


def test_sun_during_daytime_gets_strong_score() -> None:
    result = calculate_kala_bala(
        "sun",
        datetime(2026, 6, 29, 12, 0),
        sunrise_datetime=datetime(2026, 6, 29, 6, 0),
        sunset_datetime=datetime(2026, 6, 29, 18, 0),
    )

    assert result == {
        "planet": "sun",
        "component": KALA_BALA_COMPONENT,
        "time_period": "daytime",
        "status": "preferred_period",
        "score": 60,
        "max_score": KALA_BALA_MAX_SCORE,
        "reason": "Planet is in its preferred day/night period.",
    }


def test_moon_during_nighttime_gets_strong_score() -> None:
    result = calculate_kala_bala(
        "moon",
        datetime(2026, 6, 29, 22, 0),
        sunrise_datetime=datetime(2026, 6, 29, 6, 0),
        sunset_datetime=datetime(2026, 6, 29, 18, 0),
    )

    assert result["time_period"] == "nighttime"
    assert result["status"] == "preferred_period"
    assert result["score"] == 60


def test_mercury_returns_neutral_for_day_or_night() -> None:
    daytime_result = calculate_kala_bala(
        "mercury",
        datetime(2026, 6, 29, 12, 0),
        sunrise_datetime=datetime(2026, 6, 29, 6, 0),
        sunset_datetime=datetime(2026, 6, 29, 18, 0),
    )
    nighttime_result = calculate_kala_bala(
        "mercury",
        datetime(2026, 6, 29, 22, 0),
        sunrise_datetime=datetime(2026, 6, 29, 6, 0),
        sunset_datetime=datetime(2026, 6, 29, 18, 0),
    )

    assert daytime_result["time_period"] == "daytime"
    assert nighttime_result["time_period"] == "nighttime"
    assert daytime_result["status"] == nighttime_result["status"] == "neutral"
    assert daytime_result["score"] == nighttime_result["score"] == 30


def test_missing_sunrise_or_sunset_returns_neutral_placeholder() -> None:
    result = calculate_kala_bala("sun", datetime(2026, 6, 29, 12, 0))

    assert result["planet"] == "sun"
    assert result["time_period"] == "unknown"
    assert result["status"] == "neutral"
    assert result["score"] == 30


def test_non_preferred_period_gets_lower_score() -> None:
    result = calculate_kala_bala(
        "venus",
        datetime(2026, 6, 29, 22, 0),
        sunrise_datetime=datetime(2026, 6, 29, 6, 0),
        sunset_datetime=datetime(2026, 6, 29, 18, 0),
    )

    assert result["time_period"] == "nighttime"
    assert result["status"] == "non_preferred_period"
    assert result["score"] == 15


def test_invalid_planet_is_handled_safely() -> None:
    result = calculate_kala_bala(
        "rahu",
        datetime(2026, 6, 29, 12, 0),
        sunrise_datetime=datetime(2026, 6, 29, 6, 0),
        sunset_datetime=datetime(2026, 6, 29, 18, 0),
    )

    assert result["planet"] == "rahu"
    assert result["component"] == "kala_bala"
    assert result["time_period"] == "unknown"
    assert result["status"] == "invalid_input"
    assert result["score"] is None


def test_rise_set_utc_datetime_strings_are_supported() -> None:
    result = calculate_kala_bala(
        "jupiter",
        "2026-06-29T08:00:00Z",
        sunrise_datetime="2026-06-29T00:30:00Z",
        sunset_datetime="2026-06-29T13:30:00Z",
    )

    assert result["time_period"] == "daytime"
    assert result["status"] == "preferred_period"
    assert result["score"] == 60


def test_invalid_datetime_is_handled_safely() -> None:
    result = calculate_kala_bala(
        "sun",
        "not-a-datetime",
        sunrise_datetime="2026-06-29T00:30:00Z",
        sunset_datetime="2026-06-29T13:30:00Z",
    )

    assert result["time_period"] == "unknown"
    assert result["status"] == "invalid_input"
    assert result["score"] is None


def test_kala_bala_result_is_json_safe() -> None:
    result = calculate_kala_bala(
        " Moon ",
        datetime(2026, 6, 29, 22, 0, tzinfo=timezone.utc),
        sunrise_datetime=datetime(2026, 6, 29, 0, 30, tzinfo=timezone.utc),
        sunset_datetime=datetime(2026, 6, 29, 13, 30, tzinfo=timezone.utc),
    )

    json.dumps(result)
