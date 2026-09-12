"""Tests for the deterministic matchmaking foundation schemas."""

from __future__ import annotations

from copy import deepcopy
import json

from backend.app.matchmaking import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking import MATCHMAKING_STATUSES
from backend.app.matchmaking import MatchmakingPair
from backend.app.matchmaking import MatchmakingPerson
from backend.app.matchmaking import MatchmakingResult
from backend.app.matchmaking import create_empty_matchmaking_pair
from backend.app.matchmaking import create_empty_matchmaking_person
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import create_matchmaking_pair
from backend.app.matchmaking import create_matchmaking_person
from backend.app.matchmaking import create_matchmaking_result


PERSON_KEYS = {
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
}
METADATA_KEYS = {
    "component",
    "schema_version",
    "deterministic",
    "calculation_complete",
    "source_components",
}


def test_empty_person_has_complete_stable_structure() -> None:
    person = create_empty_matchmaking_person(" Person-A ")

    assert set(person) == PERSON_KEYS
    assert set(person["metadata"]) == METADATA_KEYS
    assert person["person_id"] == "person-a"
    assert person["latitude"] is None
    assert person["nakshatra_pada"] is None
    assert person["metadata"] == {
        "component": "matchmaking_person",
        "schema_version": "1.0",
        "deterministic": True,
        "calculation_complete": False,
        "source_components": [],
    }


def test_populated_person_preserves_normalized_valid_values() -> None:
    person = _person("A", "Anita")

    assert person["person_id"] == "a"
    assert person["name"] == "Anita"
    assert person["birth_date"] == "1992-04-10"
    assert person["birth_time"] == "08:15:00"
    assert person["latitude"] == 28.6139
    assert person["longitude"] == 77.209
    assert person["timezone"] == "Asia/Kolkata"
    assert person["rashi"] == "mesha"
    assert person["nakshatra"] == "ashwini"
    assert person["nakshatra_pada"] == 2
    assert person["lagna"] == "karka"
    assert person["metadata"]["source_components"] == ["kundali"]


def test_invalid_person_values_are_normalized_without_calculation() -> None:
    person = create_matchmaking_person(
        person_id=123,  # type: ignore[arg-type]
        name={"invalid": "text"},  # type: ignore[arg-type]
        latitude=float("nan"),
        longitude=float("inf"),
        nakshatra_pada=2.5,
        rashi=None,  # type: ignore[arg-type]
    )

    assert person["person_id"] == ""
    assert person["name"] == ""
    assert person["latitude"] is None
    assert person["longitude"] is None
    assert person["nakshatra_pada"] is None
    assert person["rashi"] == ""


def test_pair_preserves_order_and_does_not_mutate_people() -> None:
    person_a = _person("a", "Anita")
    person_b = _person("b", "Bharat")
    original_a = deepcopy(person_a)
    original_b = deepcopy(person_b)

    pair = create_matchmaking_pair(person_a, person_b)

    assert pair["person_a"]["person_id"] == "a"
    assert pair["person_b"]["person_id"] == "b"
    assert person_a == original_a
    assert person_b == original_b
    pair["person_a"]["metadata"]["source_components"].append("changed")
    assert person_a == original_a


def test_empty_pair_has_independent_people() -> None:
    pair = create_empty_matchmaking_pair()

    pair["person_a"]["metadata"]["source_components"].append("kundali")
    assert pair["person_b"]["metadata"]["source_components"] == []


def test_empty_result_has_complete_stable_structure() -> None:
    result = create_empty_matchmaking_result(" Pair-1 ")

    assert set(result) == {
        "matchmaking_id",
        "status",
        "score",
        "maximum_score",
        "percentage",
        "factors",
        "warnings",
        "references",
        "notes",
        "metadata",
    }
    assert result["matchmaking_id"] == "pair-1"
    assert result["status"] == "not_evaluated"
    assert result["score"] is None
    assert result["factors"] == []
    assert result["metadata"]["calculation_complete"] is False


def test_populated_result_preserves_values_without_calculating_them() -> None:
    factors = [{"factor_id": "placeholder", "score": 4.0}]
    notes = [{"scope": "foundation"}]
    original_factors = deepcopy(factors)
    original_notes = deepcopy(notes)

    result = create_matchmaking_result(
        matchmaking_id="pair-1",
        status="partial",
        score=4,
        maximum_score=8,
        percentage=150,
        factors=factors,
        warnings=[" source data incomplete "],
        references=["Source A"],
        notes=notes,
        metadata={"source_components": ["kundali", "nakshatra"]},
    )

    assert result["status"] == "partial"
    assert result["score"] == 4.0
    assert result["maximum_score"] == 8.0
    assert result["percentage"] == 100.0
    assert result["factors"] == original_factors
    assert result["warnings"] == ["source data incomplete"]
    assert result["notes"] == original_notes
    assert factors == original_factors
    assert notes == original_notes
    result["factors"][0]["score"] = 0  # type: ignore[index]
    assert factors == original_factors


def test_result_normalizes_invalid_and_non_finite_values() -> None:
    result = create_matchmaking_result(
        status="excellent",
        score=float("nan"),
        maximum_score=float("inf"),
        percentage=float("-inf"),
        factors=[{"value": float("nan")}],
        warnings=[None, " valid "],
        notes=[float("inf")],
    )

    assert result["status"] == "not_evaluated"
    assert result["score"] is None
    assert result["maximum_score"] is None
    assert result["percentage"] is None
    assert result["factors"] == [{"value": None}]
    assert result["warnings"] == ["valid"]
    assert result["notes"] == [None]
    json.dumps(result, allow_nan=False)


def test_outputs_are_json_serializable_deterministic_and_independent() -> None:
    kwargs = {
        "matchmaking_id": "pair-1",
        "factors": [["foundation"]],
        "metadata": {"source_components": ["kundali"]},
    }
    first = create_matchmaking_result(**kwargs)
    second = create_matchmaking_result(**kwargs)

    assert first == second
    json.dumps(first, allow_nan=False)
    first["factors"].append("changed")
    first["metadata"]["source_components"].append("changed")
    assert second["factors"] == [["foundation"]]
    assert second["metadata"]["source_components"] == ["kundali"]


def test_public_foundation_contract_contains_no_compatibility_calculator() -> None:
    assert MATCHMAKING_SCHEMA_VERSION == "1.0"
    assert MATCHMAKING_STATUSES == (
        "not_evaluated",
        "partial",
        "complete",
        "invalid",
    )
    assert MatchmakingPerson
    assert MatchmakingPair
    assert MatchmakingResult

    result = create_empty_matchmaking_result()
    assert result["status"] == "not_evaluated"
    assert result["score"] is None
    assert result["percentage"] is None


def _person(person_id: str, name: str) -> MatchmakingPerson:
    return create_matchmaking_person(
        person_id=person_id,
        name=name,
        birth_date="1992-04-10",
        birth_time="08:15:00",
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        rashi="Mesha",
        nakshatra="Ashwini",
        nakshatra_pada=2,
        lagna="Karka",
        metadata={"source_components": ["kundali"]},
    )
