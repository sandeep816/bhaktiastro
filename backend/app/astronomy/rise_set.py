"""Sunrise, sunset, moonrise, and moonset calculation helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from importlib import import_module
import math
from numbers import Real
from pathlib import Path
from typing import Any, Optional, TypedDict

from backend.app.astronomy import ephemeris, julian
from backend.app.config import EPHE_PATH

MIN_LATITUDE_DEGREES = -90.0
MAX_LATITUDE_DEGREES = 90.0
MIN_LONGITUDE_DEGREES = -180.0
MAX_LONGITUDE_DEGREES = 180.0
GEOGRAPHIC_ALTITUDE_METERS = 0.0
SECONDS_PER_HOUR = 3600
UTC_SUFFIX = "Z"


class RiseSetResult(TypedDict):
    """Typed output for a rise/set event."""

    event: str
    local_time: Optional[str]
    utc_datetime: Optional[str]
    timezone_offset: float


def get_sunrise(
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Return sunrise for a local civil date and location.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        latitude: Geographic latitude in degrees, north positive.
        longitude: Geographic longitude in degrees, east positive.
        timezone_offset: Local UTC offset in decimal hours.

    Returns:
        RiseSetResult with local time and UTC datetime. If Swiss Ephemeris
        reports no event, time fields are returned as None.

    Raises:
        TypeError: If latitude or longitude is not numeric.
        ValueError: If date, latitude, longitude, or timezone offset is invalid.
        RuntimeError: If Swiss Ephemeris is not installed or fails fatally.
    """

    return _get_solar_event(
        event="sunrise",
        year=year,
        month=month,
        day=day,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


def get_sunset(
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Return sunset for a local civil date and location.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        latitude: Geographic latitude in degrees, north positive.
        longitude: Geographic longitude in degrees, east positive.
        timezone_offset: Local UTC offset in decimal hours.

    Returns:
        RiseSetResult with local time and UTC datetime. If Swiss Ephemeris
        reports no event, time fields are returned as None.

    Raises:
        TypeError: If latitude or longitude is not numeric.
        ValueError: If date, latitude, longitude, or timezone offset is invalid.
        RuntimeError: If Swiss Ephemeris is not installed or fails fatally.
    """

    return _get_solar_event(
        event="sunset",
        year=year,
        month=month,
        day=day,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


def get_moonrise(
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Return moonrise for a local civil date and location.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        latitude: Geographic latitude in degrees, north positive.
        longitude: Geographic longitude in degrees, east positive.
        timezone_offset: Local UTC offset in decimal hours.

    Returns:
        RiseSetResult with local time and UTC datetime. If Swiss Ephemeris
        reports no event on the requested local date, time fields are returned
        as None.

    Raises:
        TypeError: If latitude or longitude is not numeric.
        ValueError: If date, latitude, longitude, or timezone offset is invalid.
        RuntimeError: If Swiss Ephemeris is not installed or fails fatally.
    """

    return _get_lunar_event(
        event="moonrise",
        year=year,
        month=month,
        day=day,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


def get_moonset(
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Return moonset for a local civil date and location.

    Args:
        year: Local calendar year.
        month: Local calendar month.
        day: Local calendar day.
        latitude: Geographic latitude in degrees, north positive.
        longitude: Geographic longitude in degrees, east positive.
        timezone_offset: Local UTC offset in decimal hours.

    Returns:
        RiseSetResult with local time and UTC datetime. If Swiss Ephemeris
        reports no event on the requested local date, time fields are returned
        as None.

    Raises:
        TypeError: If latitude or longitude is not numeric.
        ValueError: If date, latitude, longitude, or timezone offset is invalid.
        RuntimeError: If Swiss Ephemeris is not installed or fails fatally.
    """

    return _get_lunar_event(
        event="moonset",
        year=year,
        month=month,
        day=day,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


def _get_solar_event(
    *,
    event: str,
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Calculate a solar rise/set event through Swiss Ephemeris."""

    swe = _load_swisseph()
    return _get_rise_set_event(
        event=event,
        body=swe.SUN,
        year=year,
        month=month,
        day=day,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


def _get_lunar_event(
    *,
    event: str,
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Calculate a lunar rise/set event through Swiss Ephemeris."""

    swe = _load_swisseph()
    return _get_rise_set_event(
        event=event,
        body=swe.MOON,
        year=year,
        month=month,
        day=day,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
    )


def _get_rise_set_event(
    *,
    event: str,
    body: int,
    year: int,
    month: int,
    day: int,
    latitude: float,
    longitude: float,
    timezone_offset: float,
) -> RiseSetResult:
    """Calculate one rise/set event through Swiss Ephemeris."""

    latitude_value = _validate_coordinate(
        latitude,
        "latitude",
        MIN_LATITUDE_DEGREES,
        MAX_LATITUDE_DEGREES,
    )
    longitude_value = _validate_coordinate(
        longitude,
        "longitude",
        MIN_LONGITUDE_DEGREES,
        MAX_LONGITUDE_DEGREES,
    )
    timezone_offset_value = _validate_timezone_offset(timezone_offset)

    local_midnight_jd = julian.calculate_julian_day(
        year,
        month,
        day,
        0,
        0,
        0,
        timezone_offset_value,
    ).julian_day_ut
    _validate_local_date(year, month, day)

    _set_ephemeris_path_if_available()

    swe = _load_swisseph()
    event_flag = swe.CALC_RISE if event.endswith("rise") else swe.CALC_SET
    rsmi = event_flag | swe.BIT_DISC_CENTER
    geopos = (longitude_value, latitude_value, GEOGRAPHIC_ALTITUDE_METERS)

    try:
        result_code, event_times = swe.rise_trans(
            local_midnight_jd,
            body,
            rsmi,
            geopos,
            flags=swe.FLG_SWIEPH,
        )
    except Exception as exc:
        raise RuntimeError(f"Swiss Ephemeris failed to calculate {event}") from exc

    if result_code != 0 or not event_times:
        return _event_not_found(event, timezone_offset_value)

    utc_datetime = _julian_day_to_utc_datetime(swe, float(event_times[0]))
    local_datetime = utc_datetime + timedelta(hours=timezone_offset_value)

    return {
        "event": event,
        "local_time": local_datetime.strftime("%H:%M:%S"),
        "utc_datetime": _format_utc_datetime(utc_datetime),
        "timezone_offset": timezone_offset_value,
    }


def _load_swisseph() -> Any:
    """Load the Swiss Ephemeris module."""

    try:
        return import_module("swisseph")
    except ImportError as exc:
        raise RuntimeError(
            "Swiss Ephemeris package 'pyswisseph' is required"
        ) from exc


def _set_ephemeris_path_if_available() -> None:
    """Use configured ephemeris setup when the configured path exists."""

    ephe_path = Path(EPHE_PATH).expanduser()
    if not ephe_path.exists():
        return

    try:
        ephemeris.set_ephe_path()
    except (FileNotFoundError, NotADirectoryError):
        return


def _validate_coordinate(
    value: float,
    name: str,
    minimum: float,
    maximum: float,
) -> float:
    """Validate a finite geographic coordinate."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")

    if not minimum <= numeric_value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum} degrees")

    return numeric_value


def _validate_timezone_offset(timezone_offset: float) -> float:
    """Validate timezone offset through the existing Julian helper rules."""

    if isinstance(timezone_offset, bool) or not isinstance(timezone_offset, Real):
        raise TypeError("timezone_offset must be a numeric UTC offset in hours")

    return float(timezone_offset)


def _validate_local_date(year: int, month: int, day: int) -> None:
    """Validate local date components."""

    try:
        date(year, month, day)
    except ValueError as exc:
        raise ValueError("Invalid local date components") from exc


def _julian_day_to_utc_datetime(swe: Any, jd_ut: float) -> datetime:
    """Convert Julian Day UT to a UTC datetime using Swiss Ephemeris."""

    year, month, day, hour_decimal = swe.revjul(jd_ut, swe.GREG_CAL)
    seconds_since_midnight = int(round(float(hour_decimal) * SECONDS_PER_HOUR))
    utc_datetime = datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
    return utc_datetime + timedelta(seconds=seconds_since_midnight)


def _format_utc_datetime(utc_datetime: datetime) -> str:
    """Format a UTC datetime as an ISO-8601 string with Z suffix."""

    return utc_datetime.isoformat().replace("+00:00", UTC_SUFFIX)


def _event_not_found(event: str, timezone_offset: float) -> RiseSetResult:
    """Return a stable no-event result."""

    return {
        "event": event,
        "local_time": None,
        "utc_datetime": None,
        "timezone_offset": timezone_offset,
    }
