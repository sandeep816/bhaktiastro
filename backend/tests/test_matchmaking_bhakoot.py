"""Tests for deterministic Bhakoot Koota matchmaking."""

from __future__ import annotations

import inspect
import json

import pytest

from backend.app.constants.rashi import RASHI_LIST
from backend.app.matchmaking import BHAKOOT_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import BHAKOOT_DOSHA_POSITION_PAIRS
from backend.app.matchmaking import BHAKOOT_KOOTA_ID
from backend.app.matchmaking import BHAKOOT_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import BHAKOOT_POSITION_PAIRS
from backend.app.matchmaking import BHAKOOT_SCORING_MATRIX
from backend.app.matchmaking import MATCHMAKING_BHAKOOT_ISSUE_CODES
from backend.app.matchmaking import MatchmakingBhakootIdentity
from backend.app.matchmaking import MatchmakingBhakootIssue
from backend.app.matchmaking import MatchmakingBhakootKootaResult
from backend.app.matchmaking import MatchmakingBhakootRelationship
from backend.app.matchmaking import calculate_bhakoot_inclusive_distance
from backend.app.matchmaking import calculate_bhakoot_koota
from backend.app.matchmaking import classify_bhakoot_rashi
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import get_bhakoot_relationship

EXPECTED_SCORE_ROWS = (
    (7.0, 0.0, 7.0, 7.0, 0.0, 0.0, 7.0, 0.0, 0.0, 7.0, 7.0, 0.0),
    (0.0, 7.0, 0.0, 7.0, 7.0, 0.0, 0.0, 7.0, 0.0, 0.0, 7.0, 7.0),
    (7.0, 0.0, 7.0, 0.0, 7.0, 7.0, 0.0, 0.0, 7.0, 0.0, 0.0, 7.0),
    (7.0, 7.0, 0.0, 7.0, 0.0, 7.0, 7.0, 0.0, 0.0, 7.0, 0.0, 0.0),
    (0.0, 7.0, 7.0, 0.0, 7.0, 0.0, 7.0, 7.0, 0.0, 0.0, 7.0, 0.0),
    (0.0, 0.0, 7.0, 7.0, 0.0, 7.0, 0.0, 7.0, 7.0, 0.0, 0.0, 7.0),
    (7.0, 0.0, 0.0, 7.0, 7.0, 0.0, 7.0, 0.0, 7.0, 7.0, 0.0, 0.0),
    (0.0, 7.0, 0.0, 0.0, 7.0, 7.0, 0.0, 7.0, 0.0, 7.0, 7.0, 0.0),
    (0.0, 0.0, 7.0, 0.0, 0.0, 7.0, 7.0, 0.0, 7.0, 0.0, 7.0, 7.0),
    (7.0, 0.0, 0.0, 7.0, 0.0, 0.0, 7.0, 7.0, 0.0, 7.0, 0.0, 7.0),
    (7.0, 7.0, 0.0, 0.0, 7.0, 0.0, 0.0, 7.0, 7.0, 0.0, 7.0, 0.0),
    (0.0, 7.0, 7.0, 0.0, 0.0, 7.0, 0.0, 0.0, 7.0, 7.0, 0.0, 7.0),
)

EXPECTED_SCORING_MATRIX = {
    bride_index: dict(zip(range(1, 13), row))
    for bride_index, row in enumerate(EXPECTED_SCORE_ROWS, start=1)
}

EXPECTED_PAIR_DATA = {
    (1, 1): ("1_1", "compatible", 7.0),
    (2, 12): ("2_12", "dosha", 0.0),
    (3, 11): ("3_11", "compatible", 7.0),
    (4, 10): ("4_10", "compatible", 7.0),
    (5, 9): ("5_9", "dosha", 0.0),
    (6, 8): ("6_8", "dosha", 0.0),
    (7, 7): ("7_7", "compatible", 7.0),
}


@pytest.mark.parametrize(
    ("rashi_index", "english", "hindi", "sanskrit"),
    [(rashi.index, rashi.english, rashi.hindi, rashi.sanskrit) for rashi in RASHI_LIST],
)
def test_all_twelve_rashis_use_canonical_full_rashi_identity(
    rashi_index: int,
    english: str,
    hindi: str,
    sanskrit: str,
) -> None:
    identity = classify_bhakoot_rashi((rashi_index - 1) * 30.0 + 1.0)

    assert identity["is_valid"] is True
    assert identity["rashi_index"] == rashi_index
    assert identity["rashi_english"] == english
    assert identity["rashi_hindi"] == hindi
    assert identity["rashi_sanskrit"] == identity["rashi"] == sanskrit


@pytest.mark.parametrize("rashi_index", range(1, 13))
def test_every_rashi_half_open_boundary(rashi_index: int) -> None:
    lower = (rashi_index - 1) * 30.0
    upper_inside = lower + 29.999999

    lower_identity = classify_bhakoot_rashi(lower)
    upper_identity = classify_bhakoot_rashi(upper_inside)

    assert lower_identity["rashi_index"] == rashi_index
    assert lower_identity["degree_in_rashi"] == 0.0
    assert upper_identity["rashi_index"] == rashi_index
    assert upper_identity["degree_in_rashi"] == 29.999999


@pytest.mark.parametrize(
    ("longitude", "normalized", "rashi_index"),
    [
        (0.0, 0.0, 1),
        (360.0, 0.0, 1),
        (-360.0, 0.0, 1),
        (-30.0, 330.0, 12),
        (750.0, 30.0, 2),
    ],
)
def test_longitude_normalization_is_reused(
    longitude: float,
    normalized: float,
    rashi_index: int,
) -> None:
    identity = classify_bhakoot_rashi(longitude)

    assert identity["sidereal_moon_longitude"] == normalized
    assert identity["rashi_index"] == rashi_index


@pytest.mark.parametrize(
    ("bride_index", "groom_index", "expected_score"),
    [
        (bride, groom, score)
        for bride, row in EXPECTED_SCORING_MATRIX.items()
        for groom, score in row.items()
    ],
)
def test_all_144_rashi_pairs_match_documented_matrix_and_distances(
    bride_index: int,
    groom_index: int,
    expected_score: float,
) -> None:
    relationship = get_bhakoot_relationship(bride_index, groom_index)
    bride_to_groom = ((groom_index - bride_index) % 12) + 1
    groom_to_bride = ((bride_index - groom_index) % 12) + 1
    canonical_pair = tuple(sorted((bride_to_groom, groom_to_bride)))
    pair_identifier, expected_relationship, pair_score = EXPECTED_PAIR_DATA[
        canonical_pair
    ]

    assert BHAKOOT_SCORING_MATRIX == EXPECTED_SCORING_MATRIX
    assert BHAKOOT_POSITION_PAIRS == EXPECTED_PAIR_DATA
    assert relationship["bride_rashi_index"] == bride_index
    assert relationship["groom_rashi_index"] == groom_index
    assert relationship["bride_to_groom_distance"] == bride_to_groom
    assert relationship["groom_to_bride_distance"] == groom_to_bride
    assert relationship["pair_identifier"] == pair_identifier
    assert relationship["position_pair"] == f"{canonical_pair[0]}/{canonical_pair[1]}"
    assert relationship["relationship"] == expected_relationship
    assert relationship["bhakoot_dosha"] is (expected_relationship == "dosha")
    assert relationship["same_rashi"] is (bride_index == groom_index)
    assert relationship["score"] == pair_score == expected_score


def test_every_position_class_has_complete_matrix_coverage() -> None:
    pair_counts: dict[str, int] = {}
    for bride_index in range(1, 13):
        for groom_index in range(1, 13):
            pair_identifier = get_bhakoot_relationship(bride_index, groom_index)[
                "pair_identifier"
            ]
            pair_counts[pair_identifier] = pair_counts.get(pair_identifier, 0) + 1

    assert pair_counts == {
        "1_1": 12,
        "2_12": 24,
        "3_11": 24,
        "4_10": 24,
        "5_9": 24,
        "6_8": 24,
        "7_7": 12,
    }
    assert BHAKOOT_DOSHA_POSITION_PAIRS == ((2, 12), (5, 9), (6, 8))


@pytest.mark.parametrize("rashi_index", range(1, 13))
def test_all_same_rashi_cases_receive_maximum(rashi_index: int) -> None:
    relationship = get_bhakoot_relationship(rashi_index, rashi_index)

    assert relationship["bride_to_groom_distance"] == 1
    assert relationship["groom_to_bride_distance"] == 1
    assert relationship["pair_identifier"] == "1_1"
    assert relationship["same_rashi"] is True
    assert relationship["bhakoot_dosha"] is False
    assert relationship["score"] == BHAKOOT_KOOTA_MAXIMUM_SCORE


@pytest.mark.parametrize("offset", [0, 2, 3, 6, 9, 10])
def test_every_compatible_offset_scores_seven(offset: int) -> None:
    for bride_index in range(1, 13):
        groom_index = ((bride_index - 1 + offset) % 12) + 1
        relationship = get_bhakoot_relationship(bride_index, groom_index)

        assert relationship["relationship"] == "compatible"
        assert relationship["bhakoot_dosha"] is False
        assert relationship["score"] == 7.0


@pytest.mark.parametrize("offset", [1, 4, 5, 7, 8, 11])
def test_every_dosha_offset_scores_zero(offset: int) -> None:
    for bride_index in range(1, 13):
        groom_index = ((bride_index - 1 + offset) % 12) + 1
        relationship = get_bhakoot_relationship(bride_index, groom_index)

        assert relationship["relationship"] == "dosha"
        assert relationship["bhakoot_dosha"] is True
        assert relationship["score"] == 0.0


@pytest.mark.parametrize(
    ("bride_index", "groom_index"),
    [(1, 2), (1, 5), (1, 6), (12, 1), (9, 1), (8, 1)],
)
def test_role_reversal_swaps_distances_but_not_score(
    bride_index: int,
    groom_index: int,
) -> None:
    forward = get_bhakoot_relationship(bride_index, groom_index)
    reverse = get_bhakoot_relationship(groom_index, bride_index)

    assert forward["bride_to_groom_distance"] == reverse["groom_to_bride_distance"]
    assert forward["groom_to_bride_distance"] == reverse["bride_to_groom_distance"]
    assert forward["pair_identifier"] == reverse["pair_identifier"]
    assert forward["relationship"] == reverse["relationship"]
    assert forward["bhakoot_dosha"] == reverse["bhakoot_dosha"]
    assert forward["score"] == reverse["score"]


def test_degree_within_full_rashi_does_not_change_score() -> None:
    early = calculate_bhakoot_koota(
        bride_moon_longitude=30.0,
        groom_moon_longitude=180.0,
    )
    late = calculate_bhakoot_koota(
        bride_moon_longitude=59.999999,
        groom_moon_longitude=209.999999,
    )

    assert early["bride_moon_rashi"]["rashi_index"] == 2
    assert late["bride_moon_rashi"]["rashi_index"] == 2
    assert early["groom_moon_rashi"]["rashi_index"] == 7
    assert late["groom_moon_rashi"]["rashi_index"] == 7
    assert early["score"] == late["score"] == 0.0


@pytest.mark.parametrize("value", [True, False, "30", None, object()])
def test_classification_rejects_non_real_values(value: object) -> None:
    with pytest.raises(TypeError):
        classify_bhakoot_rashi(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_classification_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError):
        classify_bhakoot_rashi(value)


@pytest.mark.parametrize("value", [True, False, 0, 13, -1, 1.0, "1", "Mesha", None])
def test_distance_rejects_invalid_rashi_indexes(value: object) -> None:
    exception = (
        ValueError
        if isinstance(value, int) and not isinstance(value, bool)
        else TypeError
    )
    with pytest.raises(exception):
        calculate_bhakoot_inclusive_distance(value, 1)  # type: ignore[arg-type]
    with pytest.raises(exception):
        calculate_bhakoot_inclusive_distance(1, value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, False, 0, 13, -1, 1.0, "1", "Mesha", None])
def test_relationship_rejects_invalid_rashi_indexes(value: object) -> None:
    exception = (
        ValueError
        if isinstance(value, int) and not isinstance(value, bool)
        else TypeError
    )
    with pytest.raises(exception):
        get_bhakoot_relationship(value, 1)  # type: ignore[arg-type]
    with pytest.raises(exception):
        get_bhakoot_relationship(1, value)  # type: ignore[arg-type]


def test_high_level_invalid_result_is_ordered_and_has_no_partial_score() -> None:
    result = calculate_bhakoot_koota(
        bride_moon_longitude=True,
        groom_moon_longitude=float("nan"),
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["bride_to_groom_distance"] is None
    assert result["groom_to_bride_distance"] is None
    assert result["pair_identifier"] == ""
    assert result["relationship"] == ""
    assert result["same_rashi"] is None
    assert result["bhakoot_dosha"] is None
    assert result["factors"] == []
    assert _result_issues(result) == [
        ("bride.sidereal_moon_longitude", "moon_longitude_invalid"),
        ("groom.sidereal_moon_longitude", "moon_longitude_invalid"),
    ]


def test_missing_longitudes_have_stable_issue_codes() -> None:
    result = calculate_bhakoot_koota()

    assert _result_issues(result) == [
        ("bride.sidereal_moon_longitude", "moon_longitude_missing"),
        ("groom.sidereal_moon_longitude", "moon_longitude_missing"),
    ]


def test_structured_result_exposes_required_audit_contract() -> None:
    result = calculate_bhakoot_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert result["koota"] == BHAKOOT_KOOTA_ID
    assert result["compatibility_domain"] == BHAKOOT_COMPATIBILITY_DOMAIN
    assert result["status"] == "complete"
    assert result["score"] == 0.0
    assert result["maximum_score"] == 7.0
    assert result["bride_moon_rashi"]["rashi"] == "Mesha"
    assert result["groom_moon_rashi"]["rashi"] == "Vrishabha"
    assert result["bride_to_groom_distance"] == 2
    assert result["groom_to_bride_distance"] == 12
    assert result["pair_identifier"] == "2_12"
    assert result["position_pair"] == "2/12"
    assert result["relationship"] == "dosha"
    assert result["same_rashi"] is False
    assert result["bhakoot_dosha"] is True
    assert result["direction"] == {"row_role": "bride", "column_role": "groom"}
    assert result["metadata"]["directional"] is False
    assert result["metadata"]["symmetric"] is True
    assert result["metadata"]["relationship_type"] == (
        "inclusive_circular_rashi_distance"
    )
    assert result["metadata"]["rashi_count"] == 12
    assert result["metadata"]["index_base"] == 1


def test_calculator_inputs_are_keyword_only() -> None:
    signature = inspect.signature(calculate_bhakoot_koota)

    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    with pytest.raises(TypeError):
        calculate_bhakoot_koota(0.0, 30.0)  # type: ignore[misc]


def test_results_are_deterministic_json_safe_and_independent() -> None:
    inputs = {"bride_moon_longitude": 0.0, "groom_moon_longitude": 30.0}
    original = dict(inputs)
    first = calculate_bhakoot_koota(**inputs)
    second = calculate_bhakoot_koota(**inputs)

    assert first == second
    assert inputs == original
    json.dumps(first, allow_nan=False)
    first["direction"]["row_role"] = "changed"
    first["factors"].append({"changed": True})
    first["bride_moon_rashi"]["warnings"].append(_issue_for_mutation())
    first["bride_moon_rashi"]["metadata"]["component"] = "changed"
    first["references"].append("changed")
    assert second["direction"]["row_role"] == "bride"
    assert len(second["factors"]) == 1
    assert second["bride_moon_rashi"]["warnings"] == []
    assert second["bride_moon_rashi"]["metadata"]["component"] != "changed"
    assert "changed" not in second["references"]


@pytest.mark.parametrize(
    ("bride", "groom"),
    [(30.0, 180.0), (0.0, 210.0)],
)
def test_same_rashi_lord_does_not_cancel_bhakoot_dosha(
    bride: float,
    groom: float,
) -> None:
    result = calculate_bhakoot_koota(
        bride_moon_longitude=bride,
        groom_moon_longitude=groom,
    )

    assert result["pair_identifier"] == "6_8"
    assert result["bhakoot_dosha"] is True
    assert result["score"] == 0.0


def test_no_cancellation_or_interpretation_inputs_are_present() -> None:
    result = calculate_bhakoot_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )
    serialized = json.dumps(result).casefold()

    for excluded in (
        "friendship",
        "same_lord",
        "friendly_lord",
        "parihara",
        "cancellation",
        "navamsha",
        "nakshatra",
        "pada",
        "aspect",
        "judgement",
        "advice",
        "remedy",
    ):
        assert excluded not in serialized


def test_existing_matchmaking_foundation_remains_usable() -> None:
    result = create_empty_matchmaking_result("pair-1")

    assert result["matchmaking_id"] == "pair-1"
    assert result["status"] == "not_evaluated"
    assert result["factors"] == []


def test_public_exports_are_available() -> None:
    assert "moon_longitude_invalid" in MATCHMAKING_BHAKOOT_ISSUE_CODES
    assert BHAKOOT_DOSHA_POSITION_PAIRS == ((2, 12), (5, 9), (6, 8))
    assert MatchmakingBhakootIdentity
    assert MatchmakingBhakootIssue
    assert MatchmakingBhakootKootaResult
    assert MatchmakingBhakootRelationship
    assert calculate_bhakoot_inclusive_distance
    assert calculate_bhakoot_koota
    assert classify_bhakoot_rashi
    assert get_bhakoot_relationship


def _result_issues(
    result: MatchmakingBhakootKootaResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _issue_for_mutation() -> MatchmakingBhakootIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
