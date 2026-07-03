"""Current Dasha lookup helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from backend.app.dasha.antardasha import _parse_dasha_datetime


Period = dict[str, Any]


class CurrentDasha(TypedDict):
    """JSON-safe current Dasha lookup output."""

    target_datetime: str
    mahadasha: Period | None
    antardasha: Period | None
    pratyantardasha: Period | None


def find_period_at_datetime(
    periods: list[Period],
    target_datetime: datetime | str,
) -> Period | None:
    """Find the period active at a target datetime.

    Period bounds are treated as half-open intervals:
    ``start_datetime <= target_datetime < end_datetime``.
    """

    target = _parse_dasha_datetime(target_datetime, "target_datetime")

    for period in periods:
        start_datetime = _parse_period_datetime(period, "start_datetime")
        end_datetime = _parse_period_datetime(period, "end_datetime")
        try:
            if start_datetime <= target < end_datetime:
                return period
        except TypeError as exc:
            raise ValueError(
                "period datetimes and target_datetime must use matching timezone style"
            ) from exc

    return None


def get_current_dasha(
    mahadasha_timeline: list[Period],
    target_datetime: datetime | str,
    include_antardasha: bool = True,
    include_pratyantardasha: bool = True,
) -> CurrentDasha:
    """Return the active Dasha periods for a target datetime.

    Nested Antardasha and Pratyantardasha levels are looked up only when the
    corresponding nested period lists are already present on the parent period.
    Missing nested data is returned as ``None``.
    """

    target = _parse_dasha_datetime(target_datetime, "target_datetime")
    target_iso = target.isoformat(timespec="seconds")
    mahadasha = find_period_at_datetime(mahadasha_timeline, target)
    antardasha = None
    pratyantardasha = None

    if mahadasha is not None and include_antardasha:
        antardasha_periods = mahadasha.get("antardashas")
        if isinstance(antardasha_periods, list):
            antardasha = find_period_at_datetime(antardasha_periods, target)

    if antardasha is not None and include_pratyantardasha:
        pratyantardasha_periods = antardasha.get("pratyantardashas")
        if isinstance(pratyantardasha_periods, list):
            pratyantardasha = find_period_at_datetime(
                pratyantardasha_periods,
                target,
            )

    return {
        "target_datetime": target_iso,
        "mahadasha": mahadasha,
        "antardasha": antardasha,
        "pratyantardasha": pratyantardasha,
    }


def _parse_period_datetime(period: Period, field_name: str) -> datetime:
    """Parse a datetime field from a Dasha period."""

    if not isinstance(period, dict):
        raise TypeError("period must be a dictionary")

    try:
        value = period[field_name]
    except KeyError as exc:
        raise ValueError(f"period must include {field_name}") from exc

    return _parse_dasha_datetime(value, field_name)
