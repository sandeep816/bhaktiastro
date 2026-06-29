"""Tests for Julian Day calculation."""

from datetime import datetime, timezone

import pytest

from backend.app.astronomy.julian import JulianDayResult, calculate_julian_day


pytest.importorskip("swisseph")


def test_calculate_julian_day_for_jodhpur_known_value() -> None:
    result = calculate_julian_day(
        year=1985,
        month=4,
        day=20,
        hour=18,
        minute=10,
        second=0,
        timezone_offset=5.5,
    )

    assert isinstance(result, JulianDayResult)
    assert result.utc_datetime == datetime(1985, 4, 20, 12, 40, tzinfo=timezone.utc)
    assert abs(result.julian_day_ut - 2446176.027777) < 0.001


def test_calculate_julian_day_crosses_to_previous_utc_day() -> None:
    result = calculate_julian_day(
        year=1985,
        month=4,
        day=20,
        hour=0,
        minute=30,
        second=0,
        timezone_offset=5.5,
    )

    assert result.utc_datetime == datetime(1985, 4, 19, 19, 0, tzinfo=timezone.utc)


def test_calculate_julian_day_rejects_invalid_date() -> None:
    with pytest.raises(ValueError, match="Invalid local date/time components"):
        calculate_julian_day(
            year=2026,
            month=2,
            day=30,
            hour=12,
            minute=0,
            second=0,
            timezone_offset=5.5,
        )


def test_calculate_julian_day_rejects_invalid_timezone_offset() -> None:
    with pytest.raises(ValueError, match="timezone_offset must be between"):
        calculate_julian_day(
            year=2026,
            month=1,
            day=1,
            hour=12,
            minute=0,
            second=0,
            timezone_offset=15.0,
        )


def test_calculate_julian_day_rejects_non_numeric_timezone_offset() -> None:
    with pytest.raises(TypeError, match="timezone_offset must be a numeric"):
        calculate_julian_day(
            year=2026,
            month=1,
            day=1,
            hour=12,
            minute=0,
            second=0,
            timezone_offset="Asia/Kolkata",  # type: ignore[arg-type]
        )
