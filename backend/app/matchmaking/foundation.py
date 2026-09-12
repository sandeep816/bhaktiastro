"""JSON-safe data foundations for future deterministic matchmaking."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from typing import Literal, TypeAlias, TypedDict

MATCHMAKING_SCHEMA_VERSION = "1.0"

MatchmakingStatus = Literal["not_evaluated", "partial", "complete", "invalid"]
MatchmakingJsonValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | list["MatchmakingJsonValue"]
    | dict[str, "MatchmakingJsonValue"]
)

MATCHMAKING_STATUSES: tuple[MatchmakingStatus, ...] = (
    "not_evaluated",
    "partial",
    "complete",
    "invalid",
)
MATCHMAKING_DEFAULT_STATUS: MatchmakingStatus = "not_evaluated"


class MatchmakingMetadata(TypedDict):
    """Stable metadata shared by matchmaking foundation objects."""

    component: str
    schema_version: str
    deterministic: bool
    calculation_complete: bool
    source_components: list[str]


class MatchmakingPerson(TypedDict):
    """Normalized input data for one person without astrology calculation."""

    person_id: str
    name: str
    birth_date: str
    birth_time: str
    latitude: float | None
    longitude: float | None
    timezone: str
    rashi: str
    nakshatra: str
    nakshatra_pada: int | None
    lagna: str
    metadata: MatchmakingMetadata


class MatchmakingPair(TypedDict):
    """Ordered pair of normalized matchmaking people."""

    person_a: MatchmakingPerson
    person_b: MatchmakingPerson
    metadata: MatchmakingMetadata


class MatchmakingResult(TypedDict):
    """Result envelope reserved for future compatibility calculators."""

    matchmaking_id: str
    status: str
    score: float | None
    maximum_score: float | None
    percentage: float | None
    factors: list[MatchmakingJsonValue]
    warnings: list[str]
    references: list[str]
    notes: list[MatchmakingJsonValue]
    metadata: MatchmakingMetadata


def create_empty_matchmaking_person(person_id: str = "") -> MatchmakingPerson:
    """Create an empty, stable person input shape."""

    return create_matchmaking_person(person_id=person_id)


def create_matchmaking_person(
    *,
    person_id: str = "",
    name: str = "",
    birth_date: str = "",
    birth_time: str = "",
    latitude: object = None,
    longitude: object = None,
    timezone: str = "",
    rashi: str = "",
    nakshatra: str = "",
    nakshatra_pada: object = None,
    lagna: str = "",
    metadata: Mapping[str, object] | None = None,
) -> MatchmakingPerson:
    """Normalize supplied person data without deriving astrology values."""

    return {
        "person_id": _normalize_key(person_id),
        "name": _normalize_display_text(name),
        "birth_date": _normalize_display_text(birth_date),
        "birth_time": _normalize_display_text(birth_time),
        "latitude": _normalize_number(latitude),
        "longitude": _normalize_number(longitude),
        "timezone": _normalize_display_text(timezone),
        "rashi": _normalize_key(rashi),
        "nakshatra": _normalize_key(nakshatra),
        "nakshatra_pada": _normalize_integer(nakshatra_pada),
        "lagna": _normalize_key(lagna),
        "metadata": _create_metadata(metadata, component="matchmaking_person"),
    }


def create_empty_matchmaking_pair() -> MatchmakingPair:
    """Create an empty, ordered matchmaking pair."""

    return create_matchmaking_pair()


def create_matchmaking_pair(
    person_a: Mapping[str, object] | None = None,
    person_b: Mapping[str, object] | None = None,
    *,
    metadata: Mapping[str, object] | None = None,
) -> MatchmakingPair:
    """Create an ordered pair without mutating or swapping supplied people."""

    return {
        "person_a": _normalize_person(person_a),
        "person_b": _normalize_person(person_b),
        "metadata": _create_metadata(metadata, component="matchmaking_pair"),
    }


def create_empty_matchmaking_result(
    matchmaking_id: str = "",
) -> MatchmakingResult:
    """Create an unevaluated matchmaking result foundation."""

    return create_matchmaking_result(matchmaking_id=matchmaking_id)


def create_matchmaking_result(
    *,
    matchmaking_id: str = "",
    status: object = MATCHMAKING_DEFAULT_STATUS,
    score: object = None,
    maximum_score: object = None,
    percentage: object = None,
    factors: Sequence[object] | None = None,
    warnings: Sequence[object] | None = None,
    references: Sequence[object] | None = None,
    notes: Sequence[object] | None = None,
    metadata: Mapping[str, object] | None = None,
) -> MatchmakingResult:
    """Create a result envelope without calculating compatibility."""

    normalized_status = _normalize_key(status)
    if normalized_status not in MATCHMAKING_STATUSES:
        normalized_status = MATCHMAKING_DEFAULT_STATUS

    return {
        "matchmaking_id": _normalize_key(matchmaking_id),
        "status": normalized_status,
        "score": _normalize_number(score),
        "maximum_score": _normalize_number(maximum_score),
        "percentage": _normalize_percentage(percentage),
        "factors": _normalize_json_list(factors),
        "warnings": _normalize_text_list(warnings),
        "references": _normalize_text_list(references),
        "notes": _normalize_json_list(notes),
        "metadata": _create_metadata(
            metadata,
            component="matchmaking_result",
            calculation_complete=normalized_status == "complete",
        ),
    }


def _normalize_person(value: Mapping[str, object] | None) -> MatchmakingPerson:
    source = value if isinstance(value, Mapping) else {}
    return create_matchmaking_person(
        person_id=source.get("person_id", ""),
        name=source.get("name", ""),
        birth_date=source.get("birth_date", ""),
        birth_time=source.get("birth_time", ""),
        latitude=source.get("latitude"),
        longitude=source.get("longitude"),
        timezone=source.get("timezone", ""),
        rashi=source.get("rashi", ""),
        nakshatra=source.get("nakshatra", ""),
        nakshatra_pada=source.get("nakshatra_pada"),
        lagna=source.get("lagna", ""),
        metadata=(
            source.get("metadata")
            if isinstance(source.get("metadata"), Mapping)
            else None
        ),
    )


def _create_metadata(
    metadata: Mapping[str, object] | None,
    *,
    component: str,
    calculation_complete: bool = False,
) -> MatchmakingMetadata:
    source = metadata if isinstance(metadata, Mapping) else {}
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation_complete": calculation_complete,
        "source_components": _normalize_text_list(source.get("source_components")),
    }


def _normalize_key(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().casefold()


def _normalize_display_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _normalize_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    normalized = float(value)
    return normalized if math.isfinite(normalized) else None


def _normalize_integer(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, Integral):
        return None
    return int(value)


def _normalize_percentage(value: object) -> float | None:
    normalized = _normalize_number(value)
    if normalized is None:
        return None
    return round(max(0.0, min(100.0, normalized)), 4)


def _normalize_text_list(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [text for item in value if (text := _normalize_display_text(item))]


def _normalize_json_list(value: object) -> list[MatchmakingJsonValue]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_make_json_safe(item) for item in value]


def _make_json_safe(value: object) -> MatchmakingJsonValue:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Real):
        normalized = float(value)
        if not math.isfinite(normalized):
            return None
        return int(value) if isinstance(value, Integral) else normalized
    if isinstance(value, Mapping):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_make_json_safe(item) for item in value]
    return str(value)
