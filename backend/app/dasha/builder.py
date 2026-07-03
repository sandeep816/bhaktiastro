"""Dasha timeline builder helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from backend.app.dasha.antardasha import generate_antardasha_periods
from backend.app.dasha.current import CurrentDasha, get_current_dasha
from backend.app.dasha.pratyantardasha import generate_pratyantardasha_periods
from backend.app.dasha.timeline import (
    _parse_birth_datetime,
    generate_mahadasha_timeline,
)


Period = dict[str, Any]


class DashaTimelineMetadata(TypedDict):
    """Metadata for a built Dasha timeline."""

    engine: str
    system: str


class DashaTimelineBuild(TypedDict):
    """JSON-safe Dasha timeline builder output."""

    birth_datetime: str
    target_datetime: str | None
    mahadasha_timeline: list[Period]
    current_dasha: CurrentDasha | None
    metadata: DashaTimelineMetadata


def build_dasha_timeline(
    birth_datetime: datetime | str,
    nakshatra_index: int,
    moon_longitude: float,
    target_datetime: datetime | str | None = None,
    include_antardasha: bool = True,
    include_pratyantardasha: bool = False,
) -> DashaTimelineBuild:
    """Build a JSON-safe Vimshottari Dasha timeline.

    Args:
        birth_datetime: Birth datetime as a ``datetime`` object or ISO string.
        nakshatra_index: Zero-based birth Nakshatra index.
        moon_longitude: Moon sidereal longitude in degrees.
        target_datetime: Optional target datetime for current Dasha lookup.
        include_antardasha: Attach Antardasha periods under Mahadashas.
        include_pratyantardasha: Attach Pratyantardasha periods under
            Antardashas. This requires Antardasha attachment.

    Returns:
        JSON-safe Dasha timeline payload with optional current-Dasha summary.
    """

    normalized_birth_datetime = _parse_birth_datetime(birth_datetime)
    mahadasha_periods = generate_mahadasha_timeline(
        birth_datetime=normalized_birth_datetime,
        nakshatra_index=nakshatra_index,
        moon_longitude=moon_longitude,
    )
    built_timeline = [
        _build_mahadasha_period(
            mahadasha_period=period,
            include_antardasha=include_antardasha,
            include_pratyantardasha=include_pratyantardasha,
        )
        for period in mahadasha_periods
    ]

    current_dasha = None
    normalized_target_datetime = None
    if target_datetime is not None:
        current_dasha = get_current_dasha(
            mahadasha_timeline=built_timeline,
            target_datetime=target_datetime,
            include_antardasha=include_antardasha,
            include_pratyantardasha=include_pratyantardasha,
        )
        normalized_target_datetime = current_dasha["target_datetime"]

    return {
        "birth_datetime": normalized_birth_datetime.isoformat(timespec="seconds"),
        "target_datetime": normalized_target_datetime,
        "mahadasha_timeline": built_timeline,
        "current_dasha": current_dasha,
        "metadata": {
            "engine": "dasha",
            "system": "vimshottari",
        },
    }


def _build_mahadasha_period(
    mahadasha_period: Period,
    include_antardasha: bool,
    include_pratyantardasha: bool,
) -> Period:
    """Build one Mahadasha period with optional nested periods."""

    built_period = dict(mahadasha_period)
    if not include_antardasha:
        return built_period

    antardashas = generate_antardasha_periods(
        mahadasha_lord=str(built_period["dasha_lord"]),
        mahadasha_start=str(built_period["start_datetime"]),
        mahadasha_end=str(built_period["end_datetime"]),
        mahadasha_duration_years=float(built_period["duration_years"]),
    )
    built_period["antardashas"] = [
        _build_antardasha_period(
            antardasha_period=antardasha,
            include_pratyantardasha=include_pratyantardasha,
        )
        for antardasha in antardashas
    ]
    return built_period


def _build_antardasha_period(
    antardasha_period: Period,
    include_pratyantardasha: bool,
) -> Period:
    """Build one Antardasha period with optional Pratyantardasha periods."""

    built_period = dict(antardasha_period)
    if not include_pratyantardasha:
        return built_period

    built_period["pratyantardashas"] = generate_pratyantardasha_periods(
        mahadasha_lord=str(built_period["mahadasha_lord"]),
        antardasha_lord=str(built_period["antardasha_lord"]),
        antardasha_start=str(built_period["start_datetime"]),
        antardasha_end=str(built_period["end_datetime"]),
        antardasha_duration_years=float(built_period["duration_years"]),
    )
    return built_period
