"""Tests for deterministic matchmaking input validation."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from backend.app.matchmaking import MATCHMAKING_VALIDATION_CODES
from backend.app.matchmaking import MatchmakingPairValidationResult
from backend.app.matchmaking import MatchmakingPersonValidationResult
from backend.app.matchmaking import MatchmakingValidationIssue
from backend.app.matchmaking import validate_matchmaking_pair
from backend.app.matchmaking import validate_matchmaking_person


def test_valid_person_passes_and_preserves_normalized_values() -> None:
    result = validate_matchmaking_person(_person(" Person-A "))

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []
    assert result["normalized_value"]["person_id"] == "person-a"
    assert result["normalized_value"]["timezone"] == "Asia/Kolkata"


def test_empty_optional_person_fields_are_valid_and_not_calculated() -> None:
    result = validate_matchmaking_person({})

    assert result["is_valid"] is True
    assert result["normalized_value"]["rashi"] == ""
    assert result["normalized_value"]["nakshatra"] == ""
    assert result["normalized_value"]["lagna"] == ""
    assert result["normalized_value"]["nakshatra_pada"] is None


def test_invalid_person_type_fails_safely() -> None:
    result = validate_matchmaking_person(["not", "a", "mapping"])

    assert result["is_valid"] is False
    assert _issue_pairs(result) == [("", "invalid_type")]
    assert result["normalized_value"]["person_id"] == ""


@pytest.mark.parametrize("latitude", [-90, 90, -90.0, 90.0])
def test_latitude_boundaries_are_accepted(latitude: float) -> None:
    assert validate_matchmaking_person({"latitude": latitude})["is_valid"] is True


@pytest.mark.parametrize("latitude", [-90.0001, 90.0001])
def test_latitude_outside_boundaries_is_rejected(latitude: float) -> None:
    result = validate_matchmaking_person({"latitude": latitude})

    assert _issue_pairs(result) == [("latitude", "latitude_out_of_range")]


@pytest.mark.parametrize("longitude", [-180, 180, -180.0, 180.0])
def test_longitude_boundaries_are_accepted(longitude: float) -> None:
    assert validate_matchmaking_person({"longitude": longitude})["is_valid"] is True


@pytest.mark.parametrize("longitude", [-180.0001, 180.0001])
def test_longitude_outside_boundaries_is_rejected(longitude: float) -> None:
    result = validate_matchmaking_person({"longitude": longitude})

    assert _issue_pairs(result) == [("longitude", "longitude_out_of_range")]


@pytest.mark.parametrize("pada", [1, 2, 3, 4])
def test_nakshatra_pada_one_through_four_is_accepted(pada: int) -> None:
    result = validate_matchmaking_person({"nakshatra_pada": pada})

    assert result["is_valid"] is True
    assert result["normalized_value"]["nakshatra_pada"] == pada


@pytest.mark.parametrize("pada", [0, 5, -1])
def test_nakshatra_pada_outside_range_is_rejected(pada: int) -> None:
    result = validate_matchmaking_person({"nakshatra_pada": pada})

    assert _issue_pairs(result) == [
        ("nakshatra_pada", "nakshatra_pada_out_of_range")
    ]


@pytest.mark.parametrize("field", ["latitude", "longitude"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_coordinates_are_rejected_and_neutralized(
    field: str, value: float
) -> None:
    result = validate_matchmaking_person({field: value})

    assert result["is_valid"] is False
    assert result["errors"][0]["value"] is None
    assert result["normalized_value"][field] is None
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("birth_date", ["1992-04-10", "2000-02-29"])
def test_valid_iso_dates_are_accepted(birth_date: str) -> None:
    assert validate_matchmaking_person({"birth_date": birth_date})["is_valid"]


@pytest.mark.parametrize("birth_date", ["1992-02-30", "10/04/1992", "bad"])
def test_invalid_dates_are_rejected(birth_date: str) -> None:
    result = validate_matchmaking_person({"birth_date": birth_date})

    assert _issue_pairs(result) == [("birth_date", "invalid_date")]


@pytest.mark.parametrize("birth_time", ["08:15", "08:15:30", "08:15:30.5"])
def test_valid_iso_times_are_accepted(birth_time: str) -> None:
    assert validate_matchmaking_person({"birth_time": birth_time})["is_valid"]


@pytest.mark.parametrize("birth_time", ["25:00", "08:75", "8 PM", "bad"])
def test_invalid_times_are_rejected(birth_time: str) -> None:
    result = validate_matchmaking_person({"birth_time": birth_time})

    assert _issue_pairs(result) == [("birth_time", "invalid_time")]


def test_timezone_accepts_iana_name_and_rejects_unknown_name() -> None:
    valid = validate_matchmaking_person({"timezone": "Asia/Kolkata"})
    invalid = validate_matchmaking_person({"timezone": "Mars/Olympus"})

    assert valid["is_valid"] is True
    assert _issue_pairs(invalid) == [("timezone", "invalid_timezone")]


def test_unknown_fields_and_invalid_metadata_follow_strict_convention() -> None:
    result = validate_matchmaking_person(
        {"unknown": "value", "metadata": ["not", "a", "mapping"]}
    )

    assert _issue_pairs(result) == [
        ("unknown", "unknown_field"),
        ("metadata", "invalid_metadata"),
    ]


def test_pair_validates_both_people_and_preserves_order() -> None:
    result = validate_matchmaking_pair(
        {
            "person_a": _person("a"),
            "person_b": {**_person("b"), "latitude": 91},
        }
    )

    assert result["is_valid"] is False
    assert _issue_pairs(result) == [
        ("person_b.latitude", "latitude_out_of_range")
    ]
    assert result["normalized_value"]["person_a"]["person_id"] == "a"
    assert result["normalized_value"]["person_b"]["person_id"] == "b"


def test_pair_requires_both_mapping_like_people() -> None:
    result = validate_matchmaking_pair({"person_a": _person("a")})

    assert _issue_pairs(result) == [
        ("person_b", "required_field_missing"),
    ]


def test_same_non_empty_person_id_produces_duplicate_issue() -> None:
    result = validate_matchmaking_pair(
        {"person_a": _person("same"), "person_b": _person(" SAME ")}
    )

    assert _issue_pairs(result) == [
        ("person_b.person_id", "duplicate_person"),
    ]


def test_different_people_do_not_produce_duplicate_issue() -> None:
    result = validate_matchmaking_pair(
        {"person_a": _person("a"), "person_b": _person("b")}
    )

    assert result["is_valid"] is True
    assert result["errors"] == []


def test_validation_does_not_mutate_inputs_and_is_deterministic() -> None:
    pair = {
        "person_a": _person("a"),
        "person_b": {**_person("b"), "nakshatra_pada": 8},
        "metadata": {"source_components": ["kundali"]},
    }
    original = deepcopy(pair)

    first = validate_matchmaking_pair(pair)
    second = validate_matchmaking_pair(pair)

    assert pair == original
    assert first == second
    json.dumps(first, allow_nan=False)


def test_issue_order_and_message_keys_are_stable() -> None:
    value = {
        "z_extra": True,
        "a_extra": True,
        "birth_date": "bad",
        "latitude": 91,
        "longitude": -181,
        "timezone": "Unknown/Zone",
        "nakshatra_pada": 0,
    }

    result = validate_matchmaking_person(value)

    assert _issue_pairs(result) == [
        ("a_extra", "unknown_field"),
        ("z_extra", "unknown_field"),
        ("birth_date", "invalid_date"),
        ("latitude", "latitude_out_of_range"),
        ("longitude", "longitude_out_of_range"),
        ("timezone", "invalid_timezone"),
        ("nakshatra_pada", "nakshatra_pada_out_of_range"),
    ]
    assert [issue["message_key"] for issue in result["errors"]] == [
        f"matchmaking.validation.{code}" for _, code in _issue_pairs(result)
    ]


def test_public_validation_imports_and_codes_are_stable() -> None:
    assert MatchmakingValidationIssue
    assert MatchmakingPersonValidationResult
    assert MatchmakingPairValidationResult
    assert "invalid_type" in MATCHMAKING_VALIDATION_CODES
    assert "duplicate_person" in MATCHMAKING_VALIDATION_CODES


def test_validation_performs_no_astrology_or_compatibility_calculation() -> None:
    result = validate_matchmaking_pair({"person_a": {}, "person_b": {}})

    assert result["is_valid"] is True
    for person in result["normalized_value"].values():
        if isinstance(person, dict) and "rashi" in person:
            assert person["rashi"] == ""
            assert person["nakshatra"] == ""
            assert person["lagna"] == ""


def _person(person_id: str) -> dict[str, object]:
    return {
        "person_id": person_id,
        "name": "Sample Person",
        "birth_date": "1992-04-10",
        "birth_time": "08:15:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata",
        "rashi": "mesha",
        "nakshatra": "ashwini",
        "nakshatra_pada": 2,
        "lagna": "karka",
        "metadata": {"source_components": ["kundali"]},
    }


def _issue_pairs(
    result: MatchmakingPersonValidationResult | MatchmakingPairValidationResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]
