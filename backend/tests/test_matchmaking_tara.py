"""Tests for deterministic Tara Koota matchmaking."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from backend.app.matchmaking import MATCHMAKING_TARA_ISSUE_CODES
from backend.app.matchmaking import TARA_CLASSIFICATIONS
from backend.app.matchmaking import TARA_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import TARA_FAVORABLE_NUMBERS
from backend.app.matchmaking import TARA_KOOTA_ID
from backend.app.matchmaking import TARA_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import TARA_UNFAVORABLE_NUMBERS
from backend.app.matchmaking import MatchmakingTaraClassification
from backend.app.matchmaking import MatchmakingTaraDirectionalResult
from backend.app.matchmaking import MatchmakingTaraIssue
from backend.app.matchmaking import MatchmakingTaraKootaResult
from backend.app.matchmaking import calculate_tara_direction
from backend.app.matchmaking import calculate_tara_inclusive_count
from backend.app.matchmaking import calculate_tara_koota
from backend.app.matchmaking import classify_tara


EXPECTED_CLASSIFICATIONS = {
    1: ("janma", "Janma", False),
    2: ("sampat", "Sampat", True),
    3: ("vipat", "Vipat", False),
    4: ("kshema", "Kshema", True),
    5: ("pratyari", "Pratyari", False),
    6: ("sadhaka", "Sadhaka", True),
    7: ("vadha", "Vadha", False),
    8: ("mitra", "Mitra", True),
    9: ("ati_mitra", "Ati Mitra / Parama Mitra", True),
}


@pytest.mark.parametrize("inclusive_count", range(1, 28))
def test_all_twenty_seven_counts_follow_modulo_nine(inclusive_count: int) -> None:
    result = classify_tara(inclusive_count)
    expected_number = ((inclusive_count - 1) % 9) + 1
    expected = EXPECTED_CLASSIFICATIONS[expected_number]

    assert result["inclusive_count"] == inclusive_count
    assert result["tara_number"] == expected_number
    assert result["tara"] == expected[0]
    assert result["tara_name"] == expected[1]
    assert result["favorable"] is expected[2]
    assert result["score"] == (1.5 if expected[2] else 0.0)


@pytest.mark.parametrize(
    ("tara_number", "identifier", "display_name", "favorable"),
    [
        (number, *expected)
        for number, expected in EXPECTED_CLASSIFICATIONS.items()
    ],
)
def test_all_nine_classification_definitions_are_exact(
    tara_number: int,
    identifier: str,
    display_name: str,
    favorable: bool,
) -> None:
    assert TARA_CLASSIFICATIONS[tara_number] == {
        "identifier": identifier,
        "display_name": display_name,
        "favorable": favorable,
    }


def test_favorable_and_unfavorable_sets_are_explicit() -> None:
    assert TARA_FAVORABLE_NUMBERS == (2, 4, 6, 8, 9)
    assert TARA_UNFAVORABLE_NUMBERS == (1, 3, 5, 7)


@pytest.mark.parametrize(
    ("index_from", "index_to", "expected"),
    [
        (0, 0, 1),
        (0, 1, 2),
        (26, 0, 2),
        (0, 8, 9),
        (0, 9, 10),
        (0, 26, 27),
    ],
)
def test_inclusive_circular_count_boundaries(
    index_from: int,
    index_to: int,
    expected: int,
) -> None:
    assert calculate_tara_inclusive_count(index_from, index_to) == expected


@pytest.mark.parametrize(
    ("count", "tara_number"),
    [(9, 9), (10, 1), (18, 9), (19, 1), (27, 9)],
)
def test_modulo_boundaries_never_return_zero(count: int, tara_number: int) -> None:
    assert classify_tara(count)["tara_number"] == tara_number


def test_directional_result_exposes_auditable_fields() -> None:
    result = calculate_tara_direction(
        26,
        0,
        source_role="bride",
        destination_role="groom",
        source_nakshatra="Revati",
        destination_nakshatra="Ashwini",
    )

    assert result == {
        "source_role": "bride",
        "destination_role": "groom",
        "source_nakshatra": "Revati",
        "destination_nakshatra": "Ashwini",
        "source_index": 26,
        "destination_index": 0,
        "circular_distance": 1,
        "inclusive_count": 2,
        "tara_number": 2,
        "tara": "sampat",
        "tara_name": "Sampat",
        "favorable": True,
        "score": 1.5,
    }


@pytest.mark.parametrize(
    ("bride", "groom", "expected_score"),
    [(0, 0, 0.0), (0, 2, 1.5), (0, 1, 3.0)],
)
def test_all_valid_final_scores(
    bride: int,
    groom: int,
    expected_score: float,
) -> None:
    result = calculate_tara_koota(
        _pair(bride, groom),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["status"] == "complete"
    assert result["score"] == expected_score
    assert result["maximum_score"] == 3.0


def test_role_reversal_swaps_directions_but_preserves_person_order() -> None:
    pair = _pair("Ashwini", "Krittika")
    normal = calculate_tara_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    reversed_roles = calculate_tara_koota(
        pair,
        bride_role="person_b",
        groom_role="person_a",
    )

    assert normal["person_a_nakshatra"]["name"] == "Ashwini"
    assert normal["person_b_nakshatra"]["name"] == "Krittika"
    assert reversed_roles["person_a_nakshatra"]["name"] == "Ashwini"
    assert reversed_roles["person_b_nakshatra"]["name"] == "Krittika"
    assert normal["bride_to_groom"]["inclusive_count"] == 3
    assert reversed_roles["bride_to_groom"]["inclusive_count"] == 26
    assert _direction_payload(normal["groom_to_bride"]) == _direction_payload(
        reversed_roles["bride_to_groom"]
    )
    assert _direction_payload(normal["bride_to_groom"]) == _direction_payload(
        reversed_roles["groom_to_bride"]
    )


@pytest.mark.parametrize(("pada_a", "pada_b"), [(2, 2), (2, 3), (None, None)])
def test_same_nakshatra_always_scores_zero(
    pada_a: int | None,
    pada_b: int | None,
) -> None:
    result = calculate_tara_koota(
        _pair(0, 0, pada_a=pada_a, pada_b=pada_b),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["score"] == 0.0
    assert result["same_nakshatra"] is True
    assert result["bride_to_groom"]["tara"] == "janma"
    assert result["groom_to_bride"]["tara"] == "janma"


def test_names_and_indexes_produce_equivalent_scores() -> None:
    by_name = calculate_tara_koota(
        _pair("Ashwini", "Bharani"),
        bride_role="person_a",
        groom_role="person_b",
    )
    by_index = calculate_tara_koota(
        _pair(0, 1),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert by_name["score"] == by_index["score"] == 3.0
    assert by_name["bride_to_groom"]["tara"] == by_index["bride_to_groom"]["tara"]
    assert by_name["groom_to_bride"]["tara"] == by_index["groom_to_bride"]["tara"]


@pytest.mark.parametrize("invalid", [None, True, 1.5, "1", object()])
def test_classification_rejects_non_integer_counts(invalid: object) -> None:
    with pytest.raises(TypeError):
        classify_tara(invalid)


@pytest.mark.parametrize("invalid", [0, -1, 28])
def test_classification_rejects_out_of_range_counts(invalid: int) -> None:
    with pytest.raises(ValueError):
        classify_tara(invalid)


@pytest.mark.parametrize("invalid", [True, -1, 27, "Unknown", 1.5])
def test_invalid_nakshatra_inputs_return_safe_results(invalid: object) -> None:
    result = calculate_tara_koota(
        _pair(invalid, "Ashwini"),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["bride_to_groom"]["score"] is None
    assert result["errors"][0]["field"] == "bride.nakshatra"


@pytest.mark.parametrize(
    ("bride_role", "groom_role", "expected"),
    [
        (None, None, ("direction", "direction_missing")),
        ("person_c", "person_b", ("bride_role", "role_invalid")),
        ("person_a", "person_c", ("groom_role", "role_invalid")),
        ("person_a", "person_a", ("direction", "role_invalid")),
    ],
)
def test_invalid_role_assignments_fail_safely(
    bride_role: object,
    groom_role: object,
    expected: tuple[str, str],
) -> None:
    result = calculate_tara_koota(
        _pair(0, 1),
        bride_role=bride_role,
        groom_role=groom_role,
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert _result_issues(result) == [expected]


def test_errors_follow_explicit_bride_before_groom_order() -> None:
    result = calculate_tara_koota(
        _pair("", "Unknown"),
        bride_role="person_b",
        groom_role="person_a",
    )

    assert _result_issues(result) == [
        ("bride.nakshatra", "nakshatra_invalid"),
        ("groom.nakshatra", "nakshatra_missing"),
    ]


def test_result_contract_is_complete_and_auditable() -> None:
    result = calculate_tara_koota(
        _pair(0, 1),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["koota"] == TARA_KOOTA_ID
    assert result["compatibility_domain"] == TARA_COMPATIBILITY_DOMAIN
    assert result["maximum_score"] == TARA_KOOTA_MAXIMUM_SCORE
    assert result["direction"] == {
        "bride_role": "person_a",
        "groom_role": "person_b",
    }
    assert len(result["factors"]) == 3
    assert result["factors"][-1] == {
        "factor": "tara_directional_total",
        "awarded_score": 3.0,
        "maximum_score": 3.0,
    }
    assert len(result["references"]) == 2
    assert result["metadata"]["index_base"] == 0


def test_input_is_not_mutated_and_results_are_deterministic_and_independent() -> None:
    pair = _pair("Ashwini", "Bharani")
    original = deepcopy(pair)

    first = calculate_tara_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    second = calculate_tara_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )

    assert pair == original
    assert first == second
    json.dumps(first, allow_nan=False)
    first["factors"].append({"changed": True})
    first["person_a_nakshatra"]["warnings"].append(_issue_for_mutation())
    assert len(second["factors"]) == 3
    assert second["person_a_nakshatra"]["warnings"] == []


def test_no_later_koota_aggregation_or_prose_is_included() -> None:
    result = calculate_tara_koota(
        _pair(0, 1),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert "yoni" not in result
    assert "ashtakoota" not in result
    assert "summary" not in result
    assert "judgement" not in result


def test_public_imports_are_stable() -> None:
    assert "nakshatra_missing" in MATCHMAKING_TARA_ISSUE_CODES
    assert "direction_missing" in MATCHMAKING_TARA_ISSUE_CODES
    assert MatchmakingTaraClassification
    assert MatchmakingTaraDirectionalResult
    assert MatchmakingTaraIssue
    assert MatchmakingTaraKootaResult
    assert calculate_tara_inclusive_count
    assert classify_tara
    assert calculate_tara_direction
    assert calculate_tara_koota


def _pair(
    nakshatra_a: object,
    nakshatra_b: object,
    *,
    pada_a: object = None,
    pada_b: object = None,
) -> dict[str, object]:
    return {
        "person_a": {
            "person_id": "a",
            "nakshatra": nakshatra_a,
            "nakshatra_pada": pada_a,
        },
        "person_b": {
            "person_id": "b",
            "nakshatra": nakshatra_b,
            "nakshatra_pada": pada_b,
        },
    }


def _result_issues(result: MatchmakingTaraKootaResult) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _direction_payload(
    result: MatchmakingTaraDirectionalResult,
) -> tuple[object, ...]:
    return (
        result["source_nakshatra"],
        result["destination_nakshatra"],
        result["source_index"],
        result["destination_index"],
        result["circular_distance"],
        result["inclusive_count"],
        result["tara_number"],
        result["tara"],
        result["favorable"],
        result["score"],
    )


def _issue_for_mutation() -> MatchmakingTaraIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
