"""Deterministic structural validation for matchmaking inputs."""

from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import date, time
from numbers import Integral, Real
from typing import Literal, TypedDict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.app.matchmaking.foundation import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking.foundation import MatchmakingJsonValue
from backend.app.matchmaking.foundation import MatchmakingPair
from backend.app.matchmaking.foundation import MatchmakingPerson
from backend.app.matchmaking.foundation import create_matchmaking_pair
from backend.app.matchmaking.foundation import create_matchmaking_person

INVALID_TYPE = "invalid_type"
REQUIRED_FIELD_MISSING = "required_field_missing"
UNKNOWN_FIELD = "unknown_field"
INVALID_DATE = "invalid_date"
INVALID_TIME = "invalid_time"
INVALID_TIMEZONE = "invalid_timezone"
LATITUDE_OUT_OF_RANGE = "latitude_out_of_range"
LONGITUDE_OUT_OF_RANGE = "longitude_out_of_range"
NAKSHATRA_PADA_OUT_OF_RANGE = "nakshatra_pada_out_of_range"
DUPLICATE_PERSON = "duplicate_person"
INVALID_METADATA = "invalid_metadata"

MATCHMAKING_VALIDATION_CODES = (
    INVALID_TYPE,
    REQUIRED_FIELD_MISSING,
    UNKNOWN_FIELD,
    INVALID_DATE,
    INVALID_TIME,
    INVALID_TIMEZONE,
    LATITUDE_OUT_OF_RANGE,
    LONGITUDE_OUT_OF_RANGE,
    NAKSHATRA_PADA_OUT_OF_RANGE,
    DUPLICATE_PERSON,
    INVALID_METADATA,
)

_PERSON_FIELDS = (
    "person_id",
    "name",
    "birth_date",
    "birth_time",
    "latitude",
    "longitude",
    "timezone",
    "rashi",
    "nakshatra",
    "nakshatra_pada",
    "lagna",
    "metadata",
)
_PAIR_FIELDS = ("person_a", "person_b", "metadata")
_TEXT_FIELDS = (
    "person_id",
    "name",
    "rashi",
    "nakshatra",
    "lagna",
)

ValidationSeverity = Literal["error", "warning"]


class MatchmakingValidationIssue(TypedDict):
    """One localization-ready matchmaking validation issue."""

    field: str
    code: str
    message_key: str
    severity: ValidationSeverity
    value: MatchmakingJsonValue
    metadata: dict[str, MatchmakingJsonValue]


class MatchmakingValidationMetadata(TypedDict):
    """Stable metadata for a validation operation."""

    component: str
    schema_version: str
    deterministic: bool
    issue_count: int


class MatchmakingPersonValidationResult(TypedDict):
    """Validation result containing a normalized person value."""

    is_valid: bool
    errors: list[MatchmakingValidationIssue]
    warnings: list[MatchmakingValidationIssue]
    normalized_value: MatchmakingPerson
    metadata: MatchmakingValidationMetadata


class MatchmakingPairValidationResult(TypedDict):
    """Validation result containing a normalized ordered pair value."""

    is_valid: bool
    errors: list[MatchmakingValidationIssue]
    warnings: list[MatchmakingValidationIssue]
    normalized_value: MatchmakingPair
    metadata: MatchmakingValidationMetadata


def validate_matchmaking_person(value: object) -> MatchmakingPersonValidationResult:
    """Validate and normalize one person without calculating astrology data."""

    if not isinstance(value, Mapping):
        errors = [_issue("", INVALID_TYPE, value)]
        return _person_result(errors, create_matchmaking_person())

    errors: list[MatchmakingValidationIssue] = []
    for field in sorted(set(value) - set(_PERSON_FIELDS), key=str):
        errors.append(_issue(str(field), UNKNOWN_FIELD, value.get(field)))

    for field in _TEXT_FIELDS:
        if field in value and not isinstance(value[field], str):
            errors.append(_issue(field, INVALID_TYPE, value[field]))

    _validate_date(value, errors)
    _validate_time(value, errors)
    _validate_coordinate(value, "latitude", -90.0, 90.0, errors)
    _validate_coordinate(value, "longitude", -180.0, 180.0, errors)
    _validate_timezone(value, errors)
    _validate_nakshatra_pada(value, errors)

    metadata = value.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        errors.append(_issue("metadata", INVALID_METADATA, metadata))

    normalized = create_matchmaking_person(
        person_id=value.get("person_id", ""),
        name=value.get("name", ""),
        birth_date=value.get("birth_date", ""),
        birth_time=value.get("birth_time", ""),
        latitude=value.get("latitude"),
        longitude=value.get("longitude"),
        timezone=value.get("timezone", ""),
        rashi=value.get("rashi", ""),
        nakshatra=value.get("nakshatra", ""),
        nakshatra_pada=value.get("nakshatra_pada"),
        lagna=value.get("lagna", ""),
        metadata=metadata if isinstance(metadata, Mapping) else None,
    )
    return _person_result(errors, normalized)


def validate_matchmaking_pair(value: object) -> MatchmakingPairValidationResult:
    """Validate and normalize a pair while preserving person order."""

    if not isinstance(value, Mapping):
        errors = [_issue("", INVALID_TYPE, value)]
        return _pair_result(errors, create_matchmaking_pair())

    errors: list[MatchmakingValidationIssue] = []
    for field in sorted(set(value) - set(_PAIR_FIELDS), key=str):
        errors.append(_issue(str(field), UNKNOWN_FIELD, value.get(field)))

    normalized_people: dict[str, MatchmakingPerson] = {}
    for field in ("person_a", "person_b"):
        if field not in value:
            errors.append(_issue(field, REQUIRED_FIELD_MISSING, None))
            normalized_people[field] = create_matchmaking_person()
            continue

        person_result = validate_matchmaking_person(value[field])
        normalized_people[field] = person_result["normalized_value"]
        errors.extend(_prefix_issues(field, person_result["errors"]))

    metadata = value.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        errors.append(_issue("metadata", INVALID_METADATA, metadata))

    person_a = normalized_people["person_a"]
    person_b = normalized_people["person_b"]
    if person_a["person_id"] and person_a["person_id"] == person_b["person_id"]:
        errors.append(
            _issue("person_b.person_id", DUPLICATE_PERSON, person_b["person_id"])
        )

    normalized = create_matchmaking_pair(
        person_a,
        person_b,
        metadata=metadata if isinstance(metadata, Mapping) else None,
    )
    return _pair_result(errors, normalized)


def _validate_date(
    value: Mapping[object, object], errors: list[MatchmakingValidationIssue]
) -> None:
    raw = value.get("birth_date")
    if raw in (None, ""):
        return
    if not isinstance(raw, str):
        errors.append(_issue("birth_date", INVALID_DATE, raw))
        return
    try:
        date.fromisoformat(raw.strip())
    except ValueError:
        errors.append(_issue("birth_date", INVALID_DATE, raw))


def _validate_time(
    value: Mapping[object, object], errors: list[MatchmakingValidationIssue]
) -> None:
    raw = value.get("birth_time")
    if raw in (None, ""):
        return
    if not isinstance(raw, str):
        errors.append(_issue("birth_time", INVALID_TIME, raw))
        return
    try:
        time.fromisoformat(raw.strip())
    except ValueError:
        errors.append(_issue("birth_time", INVALID_TIME, raw))


def _validate_coordinate(
    value: Mapping[object, object],
    field: str,
    minimum: float,
    maximum: float,
    errors: list[MatchmakingValidationIssue],
) -> None:
    raw = value.get(field)
    if raw is None:
        return
    if isinstance(raw, bool) or not isinstance(raw, Real):
        errors.append(_issue(field, INVALID_TYPE, raw))
        return
    numeric = float(raw)
    if not math.isfinite(numeric) or not minimum <= numeric <= maximum:
        code = LATITUDE_OUT_OF_RANGE if field == "latitude" else LONGITUDE_OUT_OF_RANGE
        errors.append(_issue(field, code, raw))


def _validate_timezone(
    value: Mapping[object, object], errors: list[MatchmakingValidationIssue]
) -> None:
    raw = value.get("timezone")
    if raw in (None, ""):
        return
    if not isinstance(raw, str):
        errors.append(_issue("timezone", INVALID_TIMEZONE, raw))
        return
    try:
        ZoneInfo(raw.strip())
    except (ValueError, ZoneInfoNotFoundError):
        errors.append(_issue("timezone", INVALID_TIMEZONE, raw))


def _validate_nakshatra_pada(
    value: Mapping[object, object], errors: list[MatchmakingValidationIssue]
) -> None:
    raw = value.get("nakshatra_pada")
    if raw is None:
        return
    if isinstance(raw, bool) or not isinstance(raw, Integral):
        errors.append(_issue("nakshatra_pada", INVALID_TYPE, raw))
        return
    if not 1 <= int(raw) <= 4:
        errors.append(_issue("nakshatra_pada", NAKSHATRA_PADA_OUT_OF_RANGE, raw))


def _prefix_issues(
    prefix: str, issues: list[MatchmakingValidationIssue]
) -> list[MatchmakingValidationIssue]:
    return [
        {
            **issue,
            "field": f"{prefix}.{issue['field']}" if issue["field"] else prefix,
            "metadata": dict(issue["metadata"]),
        }
        for issue in issues
    ]


def _issue(field: str, code: str, value: object) -> MatchmakingValidationIssue:
    return {
        "field": field,
        "code": code,
        "message_key": f"matchmaking.validation.{code}",
        "severity": "error",
        "value": _safe_value(value),
        "metadata": {},
    }


def _safe_value(value: object) -> MatchmakingJsonValue:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Real):
        numeric = float(value)
        if not math.isfinite(numeric):
            return None
        return int(value) if isinstance(value, Integral) else numeric
    return str(value)


def _person_result(
    errors: list[MatchmakingValidationIssue], normalized: MatchmakingPerson
) -> MatchmakingPersonValidationResult:
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": [],
        "normalized_value": normalized,
        "metadata": _validation_metadata("matchmaking_person_validation", len(errors)),
    }


def _pair_result(
    errors: list[MatchmakingValidationIssue], normalized: MatchmakingPair
) -> MatchmakingPairValidationResult:
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": [],
        "normalized_value": normalized,
        "metadata": _validation_metadata("matchmaking_pair_validation", len(errors)),
    }


def _validation_metadata(
    component: str, issue_count: int
) -> MatchmakingValidationMetadata:
    return {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "issue_count": issue_count,
    }
