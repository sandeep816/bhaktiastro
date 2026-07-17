"""Tests for deterministic Yoni Koota matchmaking."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from backend.app.matchmaking import MATCHMAKING_YONI_ISSUE_CODES
from backend.app.matchmaking import YONI_BY_NAKSHATRA_INDEX
from backend.app.matchmaking import YONI_CATEGORIES
from backend.app.matchmaking import YONI_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import YONI_KOOTA_ID
from backend.app.matchmaking import YONI_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import YONI_RELATIONSHIP_BY_SCORE
from backend.app.matchmaking import YONI_SCORING_MATRIX
from backend.app.matchmaking import YONI_SEXES
from backend.app.matchmaking import MatchmakingYoniIdentity
from backend.app.matchmaking import MatchmakingYoniIssue
from backend.app.matchmaking import MatchmakingYoniKootaResult
from backend.app.matchmaking import MatchmakingYoniRelationship
from backend.app.matchmaking import calculate_yoni_koota
from backend.app.matchmaking import classify_yoni
from backend.app.matchmaking import get_yoni_relationship

EXPECTED_NAKSHATRA_MAPPING = (
    ("Ashwini", "horse", "Ashwa", "male"),
    ("Bharani", "elephant", "Gaja", "male"),
    ("Krittika", "sheep", "Mesha", "female"),
    ("Rohini", "serpent", "Sarpa", "male"),
    ("Mrigashira", "serpent", "Sarpa", "female"),
    ("Ardra", "dog", "Shwana", "female"),
    ("Punarvasu", "cat", "Marjara", "female"),
    ("Pushya", "sheep", "Mesha", "male"),
    ("Ashlesha", "cat", "Marjara", "male"),
    ("Magha", "rat", "Mushika", "male"),
    ("Purva Phalguni", "rat", "Mushika", "female"),
    ("Uttara Phalguni", "cow", "Gau", "male"),
    ("Hasta", "buffalo", "Mahisha", "female"),
    ("Chitra", "tiger", "Vyaghra", "female"),
    ("Swati", "buffalo", "Mahisha", "male"),
    ("Vishakha", "tiger", "Vyaghra", "male"),
    ("Anuradha", "deer", "Mriga", "female"),
    ("Jyeshtha", "deer", "Mriga", "male"),
    ("Moola", "dog", "Shwana", "male"),
    ("Purva Ashadha", "monkey", "Vanara", "male"),
    ("Uttara Ashadha", "mongoose", "Nakula", "male"),
    ("Shravana", "monkey", "Vanara", "female"),
    ("Dhanishtha", "lion", "Simha", "female"),
    ("Shatabhisha", "horse", "Ashwa", "female"),
    ("Purva Bhadrapada", "lion", "Simha", "male"),
    ("Uttara Bhadrapada", "cow", "Gau", "female"),
    ("Revati", "elephant", "Gaja", "female"),
)

EXPECTED_SCORING_ROWS = (
    (4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1),
    (2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),
    (2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1),
    (3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),
    (2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),
    (2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),
    (2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),
    (1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),
    (0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),
    (1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),
    (3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1),
    (3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2),
    (2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2),
    (1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4),
)

EXPECTED_SCORING_MATRIX = {
    row_yoni: {
        column_yoni: float(EXPECTED_SCORING_ROWS[row_index][column_index])
        for column_index, column_yoni in enumerate(YONI_CATEGORIES)
    }
    for row_index, row_yoni in enumerate(YONI_CATEGORIES)
}

SAME_YONI_NAKSHATRA_PAIRS = (
    (0, 23),
    (1, 26),
    (2, 7),
    (3, 4),
    (5, 18),
    (6, 8),
    (9, 10),
    (11, 25),
    (12, 14),
    (13, 15),
    (16, 17),
    (19, 21),
    (20, 20),
    (22, 24),
)

SWORN_ENEMY_PAIRS = (
    ("horse", "buffalo"),
    ("elephant", "lion"),
    ("sheep", "monkey"),
    ("serpent", "mongoose"),
    ("dog", "deer"),
    ("cat", "rat"),
    ("cow", "tiger"),
)


@pytest.mark.parametrize(
    ("index", "name", "yoni", "traditional_name", "yoni_sex"),
    [
        (index, *definition)
        for index, definition in enumerate(EXPECTED_NAKSHATRA_MAPPING)
    ],
)
def test_all_twenty_seven_nakshatras_classify_by_name_and_index(
    index: int,
    name: str,
    yoni: str,
    traditional_name: str,
    yoni_sex: str,
) -> None:
    by_name = classify_yoni(name)
    by_index = classify_yoni(index)

    for result in (by_name, by_index):
        assert result["is_valid"] is True
        assert result["nakshatra"] == name
        assert result["nakshatra_index"] == index
        assert result["yoni"] == yoni
        assert result["traditional_name"] == traditional_name
        assert result["yoni_sex"] == yoni_sex
        assert result["errors"] == []

    assert YONI_BY_NAKSHATRA_INDEX[index] == {
        "yoni": yoni,
        "traditional_name": traditional_name,
        "yoni_sex": yoni_sex,
    }


def test_mapping_is_exhaustive_and_uses_only_canonical_values() -> None:
    assert tuple(YONI_BY_NAKSHATRA_INDEX) == tuple(range(27))
    assert {item["yoni"] for item in YONI_BY_NAKSHATRA_INDEX.values()} == set(
        YONI_CATEGORIES
    )
    assert {item["yoni_sex"] for item in YONI_BY_NAKSHATRA_INDEX.values()} == set(
        YONI_SEXES
    )
    assert "Abhijit" not in {item[0] for item in EXPECTED_NAKSHATRA_MAPPING}


@pytest.mark.parametrize(
    ("bride_yoni", "groom_yoni", "expected_score"),
    [
        (bride, groom, score)
        for bride, row in EXPECTED_SCORING_MATRIX.items()
        for groom, score in row.items()
    ],
)
def test_every_scoring_matrix_cell_and_relationship(
    bride_yoni: str,
    groom_yoni: str,
    expected_score: float,
) -> None:
    lookup = get_yoni_relationship(bride_yoni, groom_yoni)

    assert YONI_SCORING_MATRIX == EXPECTED_SCORING_MATRIX
    assert lookup == {
        "bride_yoni": bride_yoni,
        "groom_yoni": groom_yoni,
        "relationship": YONI_RELATIONSHIP_BY_SCORE[expected_score],
        "score": expected_score,
    }
    assert expected_score == YONI_SCORING_MATRIX[groom_yoni][bride_yoni]


@pytest.mark.parametrize(
    ("score", "relationship"),
    [
        (4.0, "same"),
        (3.0, "friendly"),
        (2.0, "neutral"),
        (1.0, "enemy"),
        (0.0, "sworn_enemy"),
    ],
)
def test_all_five_relationship_classes_are_stable(
    score: float,
    relationship: str,
) -> None:
    assert YONI_RELATIONSHIP_BY_SCORE[score] == relationship


@pytest.mark.parametrize(("first", "second"), SWORN_ENEMY_PAIRS)
def test_all_sworn_enemy_pairs_score_zero_in_both_orders(
    first: str,
    second: str,
) -> None:
    assert get_yoni_relationship(first, second)["score"] == 0.0
    assert get_yoni_relationship(second, first)["score"] == 0.0
    assert get_yoni_relationship(first, second)["relationship"] == "sworn_enemy"


@pytest.mark.parametrize(
    ("first", "second", "relationship", "score"),
    [
        ("horse", "serpent", "friendly", 3.0),
        ("elephant", "dog", "neutral", 2.0),
        ("tiger", "lion", "enemy", 1.0),
    ],
)
def test_nonzero_relationships_are_symmetric(
    first: str,
    second: str,
    relationship: str,
    score: float,
) -> None:
    forward = get_yoni_relationship(first, second)
    reverse = get_yoni_relationship(second, first)

    assert (forward["relationship"], forward["score"]) == (relationship, score)
    assert (reverse["relationship"], reverse["score"]) == (relationship, score)


@pytest.mark.parametrize(("first_index", "second_index"), SAME_YONI_NAKSHATRA_PAIRS)
def test_every_same_yoni_pair_receives_maximum_score(
    first_index: int,
    second_index: int,
) -> None:
    result = calculate_yoni_koota(
        _pair(first_index, second_index),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["status"] == "complete"
    assert result["score"] == YONI_KOOTA_MAXIMUM_SCORE
    assert result["relationship"] == "same"
    assert result["same_yoni"] is True


@pytest.mark.parametrize(("pada_a", "pada_b"), [(2, 2), (2, 3), (None, None)])
@pytest.mark.parametrize("nakshatra", [0, 20])
def test_same_nakshatra_always_scores_four_independent_of_pada(
    nakshatra: int,
    pada_a: int | None,
    pada_b: int | None,
) -> None:
    result = calculate_yoni_koota(
        _pair(nakshatra, nakshatra, pada_a=pada_a, pada_b=pada_b),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["score"] == 4.0
    assert result["relationship"] == "same"
    assert result["same_nakshatra"] is True
    assert result["same_yoni"] is True


def test_role_reversal_preserves_score_and_person_order() -> None:
    pair = _pair("Ashwini", "Rohini")
    normal = calculate_yoni_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    reversed_roles = calculate_yoni_koota(
        pair,
        bride_role="person_b",
        groom_role="person_a",
    )

    assert normal["person_a_nakshatra"]["name"] == "Ashwini"
    assert normal["person_b_nakshatra"]["name"] == "Rohini"
    assert reversed_roles["person_a_nakshatra"]["name"] == "Ashwini"
    assert reversed_roles["person_b_nakshatra"]["name"] == "Rohini"
    assert normal["bride_yoni"]["yoni"] == reversed_roles["groom_yoni"]["yoni"]
    assert normal["groom_yoni"]["yoni"] == reversed_roles["bride_yoni"]["yoni"]
    assert normal["score"] == reversed_roles["score"] == 3.0
    assert normal["relationship"] == reversed_roles["relationship"] == "friendly"


def test_result_contract_is_complete_and_auditable() -> None:
    result = calculate_yoni_koota(
        _pair("Ashwini", "Swati"),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["koota"] == YONI_KOOTA_ID
    assert result["compatibility_domain"] == YONI_COMPATIBILITY_DOMAIN
    assert result["status"] == "complete"
    assert result["score"] == 0.0
    assert result["maximum_score"] == 4.0
    assert result["direction"] == {
        "bride_role": "person_a",
        "groom_role": "person_b",
    }
    assert result["bride_yoni"]["yoni"] == "horse"
    assert result["bride_yoni"]["yoni_sex"] == "male"
    assert result["groom_yoni"]["yoni"] == "buffalo"
    assert result["groom_yoni"]["yoni_sex"] == "male"
    assert result["relationship"] == "sworn_enemy"
    assert result["factors"] == [
        {
            "factor": "yoni_symmetric_matrix",
            "row_role": "bride",
            "column_role": "groom",
            "bride_yoni": "horse",
            "groom_yoni": "buffalo",
            "relationship": "sworn_enemy",
            "awarded_score": 0.0,
        }
    ]
    assert result["metadata"]["directional"] is False
    assert result["metadata"]["symmetric"] is True
    assert result["metadata"]["index_base"] == 0
    assert len(result["references"]) == 3


@pytest.mark.parametrize("invalid", [None, "", True, -1, 27, "Unknown", 1.5])
def test_invalid_nakshatra_inputs_return_safe_results(invalid: object) -> None:
    identity = classify_yoni(invalid)

    assert identity["is_valid"] is False
    assert identity["yoni"] == ""
    assert identity["errors"]

    result = calculate_yoni_koota(
        _pair(invalid, "Ashwini"),
        bride_role="person_a",
        groom_role="person_b",
    )
    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["relationship"] == ""
    assert result["errors"][0]["field"] == "bride.nakshatra"


@pytest.mark.parametrize(
    ("bride", "groom", "exception"),
    [
        (None, "horse", TypeError),
        ("horse", None, TypeError),
        ("", "horse", ValueError),
        ("Horse", "horse", ValueError),
        ("goat", "horse", ValueError),
        ("rabbit", "horse", ValueError),
        ("horse", "unknown", ValueError),
    ],
)
def test_category_lookup_rejects_malformed_values(
    bride: object,
    groom: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        get_yoni_relationship(bride, groom)  # type: ignore[arg-type]


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
    result = calculate_yoni_koota(
        _pair(0, 1),
        bride_role=bride_role,
        groom_role=groom_role,
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert _result_issues(result) == [expected]


def test_errors_follow_explicit_bride_before_groom_order() -> None:
    result = calculate_yoni_koota(
        _pair("", "Unknown"),
        bride_role="person_b",
        groom_role="person_a",
    )

    assert _result_issues(result) == [
        ("bride.nakshatra", "nakshatra_invalid"),
        ("groom.nakshatra", "nakshatra_missing"),
    ]


def test_pada_is_preserved_but_does_not_change_score() -> None:
    with_padas = calculate_yoni_koota(
        _pair(0, 3, pada_a=1, pada_b=4),
        bride_role="person_a",
        groom_role="person_b",
    )
    without_padas = calculate_yoni_koota(
        _pair(0, 3),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert with_padas["bride_yoni"]["nakshatra_pada"] == 1
    assert with_padas["groom_yoni"]["nakshatra_pada"] == 4
    assert with_padas["score"] == without_padas["score"] == 3.0


@pytest.mark.parametrize("invalid_pada", [0, 5, 2.5, True])
def test_invalid_pada_returns_safe_result(invalid_pada: object) -> None:
    result = calculate_yoni_koota(
        _pair(0, 3, pada_a=invalid_pada),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert _result_issues(result) == [("bride.pada", "nakshatra_pada_out_of_range")]


def test_input_is_not_mutated_and_results_are_deterministic_and_independent() -> None:
    pair = _pair("Ashwini", "Rohini", pada_a=1, pada_b=2)
    original = deepcopy(pair)

    first = calculate_yoni_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    second = calculate_yoni_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )

    assert pair == original
    assert first == second
    json.dumps(first, allow_nan=False)
    first["factors"].append({"changed": True})
    first["bride_yoni"]["warnings"].append(_issue_for_mutation())
    first["person_a_nakshatra"]["warnings"].append(_nakshatra_issue_for_mutation())
    assert len(second["factors"]) == 1
    assert second["bride_yoni"]["warnings"] == []
    assert second["person_a_nakshatra"]["warnings"] == []


def test_no_later_koota_aggregation_or_prose_is_included() -> None:
    result = calculate_yoni_koota(
        _pair(0, 3),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert "graha_maitri" not in result
    assert "ashtakoota" not in result
    assert "summary" not in result
    assert "judgement" not in result
    assert "remedy" not in result


def test_public_imports_are_stable() -> None:
    assert "nakshatra_missing" in MATCHMAKING_YONI_ISSUE_CODES
    assert "direction_missing" in MATCHMAKING_YONI_ISSUE_CODES
    assert MatchmakingYoniIdentity
    assert MatchmakingYoniIssue
    assert MatchmakingYoniKootaResult
    assert MatchmakingYoniRelationship
    assert classify_yoni
    assert get_yoni_relationship
    assert calculate_yoni_koota


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


def _result_issues(result: MatchmakingYoniKootaResult) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _issue_for_mutation() -> MatchmakingYoniIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }


def _nakshatra_issue_for_mutation() -> dict[str, object]:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
