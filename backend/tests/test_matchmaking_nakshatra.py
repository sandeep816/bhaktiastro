"""Tests for matchmaking Nakshatra identity and pair-context foundations."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from backend.app.matchmaking import MATCHMAKING_NAKSHATRA_INDEX_BASE
from backend.app.matchmaking import MATCHMAKING_NAKSHATRA_ISSUE_CODES
from backend.app.matchmaking import MatchmakingNakshatraIdentity
from backend.app.matchmaking import MatchmakingNakshatraIssue
from backend.app.matchmaking import MatchmakingNakshatraPairContext
from backend.app.matchmaking import build_nakshatra_pair_context
from backend.app.matchmaking import calculate_nakshatra_distance
from backend.app.matchmaking import normalize_matchmaking_nakshatra


def test_canonical_nakshatra_name_normalizes_correctly() -> None:
    identity = normalize_matchmaking_nakshatra(" Ashwini ", pada=1)

    assert identity["is_valid"] is True
    assert identity["name"] == "Ashwini"
    assert identity["index"] == 0
    assert identity["pada"] == 1
    assert identity["metadata"]["index_base"] == 0


def test_canonical_numeric_index_normalizes_correctly() -> None:
    identity = normalize_matchmaking_nakshatra(26, pada=4)

    assert identity["is_valid"] is True
    assert identity["name"] == "Revati"
    assert identity["index"] == 26
    assert identity["pada"] == 4


def test_name_and_index_resolve_to_same_identity() -> None:
    by_name = normalize_matchmaking_nakshatra("Bharani")
    by_index = normalize_matchmaking_nakshatra(1)

    assert by_name["name"] == by_index["name"]
    assert by_name["index"] == by_index["index"]


def test_first_and_last_nakshatra_boundaries_are_accepted() -> None:
    first = normalize_matchmaking_nakshatra(0)
    last = normalize_matchmaking_nakshatra(26)

    assert first["is_valid"] is True
    assert first["name"] == "Ashwini"
    assert last["is_valid"] is True
    assert last["name"] == "Revati"


@pytest.mark.parametrize("index", [-1, 27])
def test_index_outside_range_is_rejected(index: int) -> None:
    identity = normalize_matchmaking_nakshatra(index)

    assert identity["is_valid"] is False
    assert _issue_pairs(identity) == [("nakshatra", "nakshatra_index_out_of_range")]
    assert identity["index"] is None


def test_unknown_nakshatra_name_is_rejected() -> None:
    identity = normalize_matchmaking_nakshatra("Not A Nakshatra")

    assert identity["is_valid"] is False
    assert _issue_pairs(identity) == [("nakshatra", "nakshatra_invalid")]


@pytest.mark.parametrize("pada", [1, 2, 3, 4])
def test_valid_pada_values_are_accepted(pada: int) -> None:
    identity = normalize_matchmaking_nakshatra("Ashwini", pada=pada)

    assert identity["is_valid"] is True
    assert identity["pada"] == pada


@pytest.mark.parametrize("pada", [0, 5, 2.5, True])
def test_invalid_pada_values_are_rejected(pada: object) -> None:
    identity = normalize_matchmaking_nakshatra("Ashwini", pada=pada)

    assert identity["is_valid"] is False
    assert _issue_pairs(identity) == [("pada", "nakshatra_pada_out_of_range")]
    assert identity["pada"] is None


def test_missing_nakshatra_fails_safely() -> None:
    identity = normalize_matchmaking_nakshatra({})

    assert identity["is_valid"] is False
    assert identity["name"] == ""
    assert identity["index"] is None
    assert _issue_pairs(identity) == [("nakshatra", "nakshatra_missing")]


def test_same_nakshatra_gives_forward_distance_zero() -> None:
    context = build_nakshatra_pair_context(_person("a", "Ashwini"), _person("b", 0))

    assert context["is_valid"] is True
    assert context["forward_distance"] == 0
    assert context["reverse_distance"] == 0
    assert context["same_nakshatra"] is True


def test_adjacent_nakshatras_give_expected_distances() -> None:
    context = build_nakshatra_pair_context(_person("a", 0), _person("b", 1))

    assert context["forward_distance"] == 1
    assert context["reverse_distance"] == 26
    assert calculate_nakshatra_distance(0, 1) == 1


def test_wrap_around_distance_from_last_to_first_is_correct() -> None:
    context = build_nakshatra_pair_context(_person("a", 26), _person("b", 0))

    assert context["forward_distance"] == 1
    assert context["reverse_distance"] == 26


def test_person_order_is_preserved() -> None:
    context = build_nakshatra_pair_context(
        {"person_a": _person("a", "Ashwini"), "person_b": _person("b", "Revati")}
    )

    assert context["person_a"]["source_person_id"] == "a"
    assert context["person_b"]["source_person_id"] == "b"
    assert context["person_a"]["name"] == "Ashwini"
    assert context["person_b"]["name"] == "Revati"


def test_same_nakshatra_and_same_pada_flags_are_correct() -> None:
    same = build_nakshatra_pair_context(
        _person("a", "Ashwini", 2),
        _person("b", "Ashwini", 2),
    )
    different_pada = build_nakshatra_pair_context(
        _person("a", "Ashwini", 2),
        _person("b", "Ashwini", 3),
    )

    assert same["same_nakshatra"] is True
    assert same["same_pada"] is True
    assert different_pada["same_nakshatra"] is True
    assert different_pada["same_pada"] is False


def test_inputs_are_not_mutated_and_repeated_calls_are_equal() -> None:
    pair = {"person_a": _person("a", "Ashwini"), "person_b": _person("b", "Bharani")}
    original = deepcopy(pair)

    first = build_nakshatra_pair_context(pair)
    second = build_nakshatra_pair_context(pair)

    assert pair == original
    assert first == second


def test_output_is_json_serializable() -> None:
    context = build_nakshatra_pair_context(
        _person("a", "Ashwini"),
        _person("b", "Bharani"),
    )

    json.dumps(context, allow_nan=False)


def test_invalid_input_follows_validation_issue_conventions() -> None:
    context = build_nakshatra_pair_context(_person("a", ""), _person("b", "Bharani"))

    assert context["is_valid"] is False
    assert context["errors"][0] == {
        "field": "person_a.nakshatra",
        "code": "nakshatra_missing",
        "message_key": "matchmaking.validation.nakshatra_missing",
        "severity": "error",
        "value": "",
        "metadata": {},
    }


def test_public_imports_and_issue_codes_are_stable() -> None:
    assert MATCHMAKING_NAKSHATRA_INDEX_BASE == 0
    assert "nakshatra_missing" in MATCHMAKING_NAKSHATRA_ISSUE_CODES
    assert MatchmakingNakshatraIdentity
    assert MatchmakingNakshatraIssue
    assert MatchmakingNakshatraPairContext


def test_no_koota_score_or_compatibility_judgement_is_produced() -> None:
    context = build_nakshatra_pair_context(_person("a", "Ashwini"), _person("b", 1))

    assert "score" not in context
    assert "points" not in context
    assert "judgement" not in context
    assert "compatibility" not in context
    assert context["metadata"]["calculation_scope"] == (
        "nakshatra_pair_context_preparation"
    )


def _person(
    person_id: str,
    nakshatra: object,
    pada: object | None = None,
) -> dict[str, object]:
    return {
        "person_id": person_id,
        "nakshatra": nakshatra,
        "nakshatra_pada": pada,
    }


def _issue_pairs(
    result: MatchmakingNakshatraIdentity | MatchmakingNakshatraPairContext,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]
