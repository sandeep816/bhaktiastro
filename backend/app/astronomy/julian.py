"""Julian Day calculation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
from typing import Union

Number = Union[int, float]

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
MIN_TIMEZONE_OFFSET_HOURS = -14.0
MAX_TIMEZONE_OFFSET_HOURS = 14.0


@dataclass(frozen=True)
class JulianDayResult:
    """Calculated Julian Day result.

    Attributes:
        utc_datetime: Birth/event datetime converted from local time to UTC.
        julian_day_ut: Julian Day calculated for UT using Swiss Ephemeris.
    """

    utc_datetime: datetime
    julian_day_ut: float


def calculate_julian_day(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_offset: Number,
) -> JulianDayResult:
    """Convert local datetime to UTC and calculate Julian Day UT.

    Args:
        year: Local calendar year.
        month: Local calendar month, from 1 to 12.
        day: Local calendar day.
        hour: Local hour, from 0 to 23.
        minute: Local minute, from 0 to 59.
        second: Local second, from 0 to 59.
        timezone_offset: Local UTC offset in decimal hours, such as 5.5 for IST.

    Returns:
        A `JulianDayResult` containing the UTC datetime and Julian Day UT.

    Raises:
        TypeError: If `timezone_offset` is not numeric.
        ValueError: If date/time components or timezone offset are invalid.
        RuntimeError: If Swiss Ephemeris is not installed.
    """
    if isinstance(timezone_offset, bool) or not isinstance(timezone_offset, (int, float)):
        raise TypeError("timezone_offset must be a numeric UTC offset in hours")

    timezone_offset_hours = float(timezone_offset)
    if not math.isfinite(timezone_offset_hours):
        raise ValueError("timezone_offset must be finite")

    if not (
        MIN_TIMEZONE_OFFSET_HOURS
        <= timezone_offset_hours
        <= MAX_TIMEZONE_OFFSET_HOURS
    ):
        raise ValueError(
            "timezone_offset must be between "
            f"{MIN_TIMEZONE_OFFSET_HOURS} and {MAX_TIMEZONE_OFFSET_HOURS} hours"
        )

    try:
        local_datetime = datetime(year, month, day, hour, minute, second)
    except ValueError as exc:
        raise ValueError("Invalid local date/time components") from exc

    utc_datetime = (
        local_datetime - timedelta(hours=timezone_offset_hours)
    ).replace(tzinfo=timezone.utc)

    utc_hour = (
        utc_datetime.hour
        + utc_datetime.minute / MINUTES_PER_HOUR
        + utc_datetime.second / SECONDS_PER_HOUR
        + utc_datetime.microsecond / (SECONDS_PER_HOUR * 1_000_000)
    )

    try:
        import swisseph as swe
    except ImportError as exc:
        raise RuntimeError(
            "Swiss Ephemeris package 'pyswisseph' is required to calculate Julian Day"
        ) from exc

    julian_day_ut = swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        utc_hour,
        swe.GREG_CAL,
    )

    return JulianDayResult(
        utc_datetime=utc_datetime,
        julian_day_ut=float(julian_day_ut),
    )
