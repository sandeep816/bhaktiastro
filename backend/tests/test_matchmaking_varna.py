"""Tests for deterministic Varna Koota matchmaking foundation."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from backend.app.constants.rashi import RASHI_LIST
from backend.app.matchmaking import MATCHMAKING_RASHI_INDEX_BASE
from backend.app.matchmaking import MATCHMAKING_VARNA_ISSUE_CODES
from backend.app.matchmaking import RASHI_VARNA_BY_INDEX
from backend.app.matchmaking import VARNA_KOOTA_ID
from backend.app.matchmaking import VARNA_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import VARNA_RANKS
from backend.app.matchmaking import MatchmakingVarnaIdentity
from backend.app.matchmaking import MatchmakingVarnaIssue
from backend.app.matchmaking import MatchmakingVarnaKootaResult
from backend.app.matchmaking import calculate_varna_koota
from backend.app.matchmaking import resolve_varna
from backend.app.matchmaking import validate_matchmaking_pair


def test_every_canonical_rashi_resolves_to_exactly_one_varna() -> None:
    for rashi in RASHI_LIST:
        identity = resolve_varna(rashi.sanskrit)

        assert identity["is_valid"] is True
        assert identity["rashi_index"] == rashi.index
        assert identity["rashi"] == rashi.sanskrit
        assert identity["varna"] in VARNA_RANKS
        assert identity["varna_rank"] == VARNA_RANKS[identity["varna"]]


def test_rashi_name_and_index_resolve_to_same_varna() -> None:
    by_name = resolve_varna("Mesha")
    by_index = resolve_varna(1)

    assert by_name["rashi"] == by_index["rashi"]
    assert by_name["rashi_index"] == by_index["rashi_index"]
    assert by_name["varna"] == by_index["varna"]
    assert by_name["varna_rank"] == by_index["varna_rank"]


def test_first_and_last_rashi_boundaries_are_supported() -> None:
    first = resolve_varna(1)
    last = resolve_varna(12)

    assert first["is_valid"] is True
    assert first["rashi"] == "Mesha"
    assert last["is_valid"] is True
    assert last["rashi"] == "Meena"


def test_invalid_rashi_name_fails_safely() -> None:
    identity = resolve_varna("Not A Rashi")

    assert identity["is_valid"] is False
    assert identity["rashi"] == ""
    assert identity["rashi_index"] is None
    assert _identity_issues(identity) == [("rashi", "rashi_invalid")]


@pytest.mark.parametrize("index", [0, 13])
def test_invalid_rashi_index_fails_safely(index: int) -> None:
    identity = resolve_varna(index)

    assert identity["is_valid"] is False
    assert identity["rashi_index"] is None
    assert _identity_issues(identity) == [("rashi", "rashi_index_out_of_range")]


def test_missing_rashi_fails_safely() -> None:
    identity = resolve_varna({})

    assert identity["is_valid"] is False
    assert identity["rashi"] == ""
    assert _identity_issues(identity) == [("rashi", "rashi_missing")]


def test_all_four_varna_identifiers_are_represented() -> None:
    assert {resolve_varna(rashi.index)["varna"] for rashi in RASHI_LIST} == {
        "brahmin",
        "kshatriya",
        "vaishya",
        "shudra",
    }


def test_varna_rank_mapping_is_deterministic() -> None:
    assert VARNA_RANKS == {
        "shudra": 1,
        "vaishya": 2,
        "kshatriya": 3,
        "brahmin": 4,
    }
    assert RASHI_VARNA_BY_INDEX[1] == "kshatriya"
    assert RASHI_VARNA_BY_INDEX[4] == "brahmin"
    assert RASHI_VARNA_BY_INDEX[2] == "vaishya"
    assert RASHI_VARNA_BY_INDEX[3] == "shudra"


def test_valid_scoring_condition_returns_one() -> None:
    result = calculate_varna_koota(
        _pair("Mesha", "Meena"),
        subject_role="person_a",
        comparison_role="person_b",
    )

    assert result["status"] == "complete"
    assert result["score"] == 1.0
    assert result["maximum_score"] == 1.0
    assert result["factors"][0]["matched"] is True


def test_invalid_scoring_condition_returns_zero() -> None:
    result = calculate_varna_koota(
        _pair("Meena", "Mesha"),
        subject_role="person_a",
        comparison_role="person_b",
    )

    assert result["status"] == "complete"
    assert result["score"] == 0.0
    assert result["maximum_score"] == 1.0
    assert result["factors"][0]["matched"] is False


def test_maximum_score_is_always_one() -> None:
    valid = calculate_varna_koota(
        _pair("Mesha", "Meena"),
        subject_role="person_a",
        comparison_role="person_b",
    )
    invalid = calculate_varna_koota(_pair("", "Meena"))

    assert valid["maximum_score"] == VARNA_KOOTA_MAXIMUM_SCORE
    assert invalid["maximum_score"] == VARNA_KOOTA_MAXIMUM_SCORE


def test_direction_and_person_order_are_preserved() -> None:
    result = calculate_varna_koota(
        validate_matchmaking_pair(_pair("Mesha", "Meena")),
        subject_role="person_b",
        comparison_role="person_a",
    )

    assert result["direction"] == {
        "subject_role": "person_b",
        "comparison_role": "person_a",
    }
    assert result["person_a_varna"]["source_person_id"] == "a"
    assert result["person_b_varna"]["source_person_id"] == "b"
    assert result["person_a_varna"]["rashi"] == "Mesha"
    assert result["person_b_varna"]["rashi"] == "Meena"


def test_missing_direction_fails_safely() -> None:
    result = calculate_varna_koota(_pair("Mesha", "Meena"))

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert _result_issues(result) == [("direction", "direction_missing")]


@pytest.mark.parametrize(
    ("subject_role", "comparison_role", "expected_issue"),
    [
        ("person_c", "person_b", ("subject_role", "role_invalid")),
        ("person_a", "person_c", ("comparison_role", "role_invalid")),
        ("person_a", "person_a", ("direction", "role_invalid")),
    ],
)
def test_invalid_role_or_direction_fails_safely(
    subject_role: str,
    comparison_role: str,
    expected_issue: tuple[str, str],
) -> None:
    result = calculate_varna_koota(
        _pair("Mesha", "Meena"),
        subject_role=subject_role,
        comparison_role=comparison_role,
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert _result_issues(result) == [expected_issue]


def test_same_varna_input_follows_documented_rank_rule() -> None:
    result = calculate_varna_koota(
        _pair("Mesha", "Simha"),
        subject_role="person_a",
        comparison_role="person_b",
    )

    assert result["score"] == 1.0
    assert result["person_a_varna"]["varna"] == "kshatriya"
    assert result["person_b_varna"]["varna"] == "kshatriya"


def test_inputs_are_not_mutated_and_repeated_calls_are_equal() -> None:
    pair = _pair("Mesha", "Meena")
    original = deepcopy(pair)

    first = calculate_varna_koota(
        pair,
        subject_role="person_a",
        comparison_role="person_b",
    )
    second = calculate_varna_koota(
        pair,
        subject_role="person_a",
        comparison_role="person_b",
    )

    assert pair == original
    assert first == second


def test_output_is_json_serializable() -> None:
    result = calculate_varna_koota(
        _pair("Mesha", "Meena"),
        subject_role="person_a",
        comparison_role="person_b",
    )

    json.dumps(result, allow_nan=False)


def test_no_compatibility_prose_is_generated() -> None:
    result = calculate_varna_koota(
        _pair("Mesha", "Meena"),
        subject_role="person_a",
        comparison_role="person_b",
    )

    assert "summary" not in result
    assert "description" not in result
    assert "judgement" not in result
    assert result["references"] == []


def test_no_other_koota_scores_are_included() -> None:
    result = calculate_varna_koota(
        _pair("Mesha", "Meena"),
        subject_role="person_a",
        comparison_role="person_b",
    )

    assert result["koota"] == VARNA_KOOTA_ID
    assert "tara" not in result
    assert "yoni" not in result
    assert "gana" not in result
    assert "nadi" not in result
    assert "ashtakoota" not in result


def test_public_imports_work_from_matchmaking_package() -> None:
    assert MATCHMAKING_RASHI_INDEX_BASE == 1
    assert "direction_missing" in MATCHMAKING_VARNA_ISSUE_CODES
    assert MatchmakingVarnaIdentity
    assert MatchmakingVarnaIssue
    assert MatchmakingVarnaKootaResult


def _pair(rashi_a: object, rashi_b: object) -> dict[str, object]:
    return {
        "person_a": {"person_id": "a", "rashi": rashi_a},
        "person_b": {"person_id": "b", "rashi": rashi_b},
    }


def _identity_issues(
    identity: MatchmakingVarnaIdentity,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in identity["errors"]]


def _result_issues(
    result: MatchmakingVarnaKootaResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]
