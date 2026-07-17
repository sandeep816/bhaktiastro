"""Tests for deterministic Graha Maitri Koota matchmaking."""

from __future__ import annotations

import inspect
import json

import pytest

from backend.app.kundali.graha_relationship import NATURAL_RELATIONSHIPS
from backend.app.matchmaking import GRAHA_MAITRI_COMBINED_SCORES
from backend.app.matchmaking import GRAHA_MAITRI_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import GRAHA_MAITRI_KOOTA_ID
from backend.app.matchmaking import GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import GRAHA_MAITRI_LORDS
from backend.app.matchmaking import GRAHA_MAITRI_SCORING_MATRIX
from backend.app.matchmaking import MATCHMAKING_GRAHA_MAITRI_ISSUE_CODES
from backend.app.matchmaking import MatchmakingGrahaMaitriIdentity
from backend.app.matchmaking import MatchmakingGrahaMaitriIssue
from backend.app.matchmaking import MatchmakingGrahaMaitriKootaResult
from backend.app.matchmaking import MatchmakingGrahaMaitriRelationship
from backend.app.matchmaking import calculate_graha_maitri_koota
from backend.app.matchmaking import classify_graha_maitri_lord
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import get_graha_maitri_relationship

EXPECTED_RASHIS = (
    ("Aries", "Mesha", "mars"),
    ("Taurus", "Vrishabha", "venus"),
    ("Gemini", "Mithuna", "mercury"),
    ("Cancer", "Karka", "moon"),
    ("Leo", "Simha", "sun"),
    ("Virgo", "Kanya", "mercury"),
    ("Libra", "Tula", "venus"),
    ("Scorpio", "Vrishchika", "mars"),
    ("Sagittarius", "Dhanu", "jupiter"),
    ("Capricorn", "Makara", "saturn"),
    ("Aquarius", "Kumbha", "saturn"),
    ("Pisces", "Meena", "jupiter"),
)

EXPECTED_SCORING_MATRIX = {
    "sun": dict(zip(GRAHA_MAITRI_LORDS, (5.0, 5.0, 5.0, 4.0, 5.0, 0.0, 0.0))),
    "moon": dict(zip(GRAHA_MAITRI_LORDS, (5.0, 5.0, 4.0, 1.0, 4.0, 0.5, 0.5))),
    "mars": dict(zip(GRAHA_MAITRI_LORDS, (5.0, 4.0, 5.0, 0.5, 5.0, 3.0, 0.5))),
    "mercury": dict(zip(GRAHA_MAITRI_LORDS, (4.0, 1.0, 0.5, 5.0, 0.5, 5.0, 4.0))),
    "jupiter": dict(zip(GRAHA_MAITRI_LORDS, (5.0, 4.0, 5.0, 0.5, 5.0, 0.5, 3.0))),
    "venus": dict(zip(GRAHA_MAITRI_LORDS, (0.0, 0.5, 3.0, 5.0, 0.5, 5.0, 5.0))),
    "saturn": dict(zip(GRAHA_MAITRI_LORDS, (0.0, 0.5, 0.5, 4.0, 3.0, 5.0, 5.0))),
}


@pytest.mark.parametrize(
    ("rashi_index", "english", "sanskrit", "lord"),
    [
        (index, english, sanskrit, lord)
        for index, (english, sanskrit, lord) in enumerate(EXPECTED_RASHIS, start=1)
    ],
)
def test_all_twelve_rashis_use_canonical_lordship(
    rashi_index: int,
    english: str,
    sanskrit: str,
    lord: str,
) -> None:
    identity = classify_graha_maitri_lord((rashi_index - 1) * 30.0 + 1.0)

    assert identity["rashi_index"] == rashi_index
    assert identity["rashi_english"] == english
    assert identity["rashi_sanskrit"] == sanskrit
    assert identity["rashi"] == sanskrit
    assert identity["lord"] == lord


@pytest.mark.parametrize("rashi_index", range(1, 13))
def test_every_rashi_half_open_boundary(rashi_index: int) -> None:
    lower = (rashi_index - 1) * 30.0
    upper_inside = lower + 29.999999

    assert classify_graha_maitri_lord(lower)["rashi_index"] == rashi_index
    assert classify_graha_maitri_lord(upper_inside)["rashi_index"] == rashi_index


@pytest.mark.parametrize(
    ("longitude", "normalized", "rashi_index"),
    [(0.0, 0.0, 1), (360.0, 0.0, 1), (-30.0, 330.0, 12), (750.0, 30.0, 2)],
)
def test_longitude_normalization_is_reused(
    longitude: float,
    normalized: float,
    rashi_index: int,
) -> None:
    identity = classify_graha_maitri_lord(longitude)

    assert identity["sidereal_moon_longitude"] == normalized
    assert identity["rashi_index"] == rashi_index


@pytest.mark.parametrize(
    ("source", "group", "target"),
    [
        (source, group, target)
        for source, relationships in NATURAL_RELATIONSHIPS.items()
        for group in ("friends", "neutrals", "enemies")
        for target in relationships[group]
    ],
)
def test_every_permanent_relationship_entry_is_reused(
    source: str,
    group: str,
    target: str,
) -> None:
    relationship = get_graha_maitri_relationship(source, target)

    assert (
        relationship["bride_to_groom"]
        == {
            "friends": "friend",
            "neutrals": "neutral",
            "enemies": "enemy",
        }[group]
    )


@pytest.mark.parametrize(
    ("bride_lord", "groom_lord", "expected"),
    [
        (bride, groom, score)
        for bride, row in EXPECTED_SCORING_MATRIX.items()
        for groom, score in row.items()
    ],
)
def test_every_scoring_matrix_cell(
    bride_lord: str,
    groom_lord: str,
    expected: float,
) -> None:
    assert GRAHA_MAITRI_SCORING_MATRIX == EXPECTED_SCORING_MATRIX
    assert get_graha_maitri_relationship(bride_lord, groom_lord)["score"] == expected
    assert expected == EXPECTED_SCORING_MATRIX[groom_lord][bride_lord]


@pytest.mark.parametrize(
    ("bride", "groom", "combined", "score"),
    [
        ("sun", "sun", "same_lord", 5.0),
        ("sun", "moon", "mutual_friend", 5.0),
        ("sun", "mercury", "friend_neutral", 4.0),
        ("mars", "venus", "mutual_neutral", 3.0),
        ("moon", "mercury", "friend_enemy", 1.0),
        ("moon", "venus", "neutral_enemy", 0.5),
        ("sun", "venus", "mutual_enemy", 0.0),
    ],
)
def test_every_combined_relationship_and_score(
    bride: str,
    groom: str,
    combined: str,
    score: float,
) -> None:
    result = get_graha_maitri_relationship(bride, groom)

    assert result["combined_relationship"] == combined
    assert result["score"] == score


@pytest.mark.parametrize("lord", GRAHA_MAITRI_LORDS)
def test_every_same_lord_receives_maximum(lord: str) -> None:
    relationship = get_graha_maitri_relationship(lord, lord)

    assert relationship["same_lord"] is True
    assert relationship["bride_to_groom"] == "same"
    assert relationship["groom_to_bride"] == "same"
    assert relationship["score"] == GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE


@pytest.mark.parametrize(
    ("bride", "groom"),
    [
        (0.0, 210.0),
        (30.0, 180.0),
        (60.0, 150.0),
        (240.0, 330.0),
        (270.0, 300.0),
    ],
)
def test_different_rashi_shared_lords_score_maximum_in_both_orders(
    bride: float,
    groom: float,
) -> None:
    forward = calculate_graha_maitri_koota(
        bride_moon_longitude=bride,
        groom_moon_longitude=groom,
    )
    reverse = calculate_graha_maitri_koota(
        bride_moon_longitude=groom,
        groom_moon_longitude=bride,
    )

    assert forward["score"] == reverse["score"] == 5.0
    assert forward["same_lord"] is reverse["same_lord"] is True


@pytest.mark.parametrize(
    ("bride", "groom"),
    [("sun", "mercury"), ("moon", "mercury"), ("moon", "venus")],
)
def test_role_reversal_swaps_directional_statuses_not_score(
    bride: str,
    groom: str,
) -> None:
    forward = get_graha_maitri_relationship(bride, groom)
    reverse = get_graha_maitri_relationship(groom, bride)

    assert forward["bride_to_groom"] == reverse["groom_to_bride"]
    assert forward["groom_to_bride"] == reverse["bride_to_groom"]
    assert forward["score"] == reverse["score"]


def test_degree_within_rashi_does_not_change_lord_or_score() -> None:
    early = calculate_graha_maitri_koota(
        bride_moon_longitude=120.0,
        groom_moon_longitude=60.0,
    )
    late = calculate_graha_maitri_koota(
        bride_moon_longitude=149.999999,
        groom_moon_longitude=89.999999,
    )

    assert early["bride_moon_rashi"]["lord"] == late["bride_moon_rashi"]["lord"]
    assert early["groom_moon_rashi"]["lord"] == late["groom_moon_rashi"]["lord"]
    assert early["score"] == late["score"]


@pytest.mark.parametrize("value", [True, False, "30", None, object()])
def test_classification_rejects_non_real_values(value: object) -> None:
    with pytest.raises(TypeError):
        classify_graha_maitri_lord(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_classification_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError):
        classify_graha_maitri_lord(value)


@pytest.mark.parametrize(
    ("bride", "groom", "exception"),
    [
        (None, "sun", TypeError),
        ("sun", None, TypeError),
        ("", "sun", ValueError),
        ("Sun", "moon", ValueError),
        ("surya", "moon", ValueError),
        ("rahu", "moon", ValueError),
        ("ketu", "moon", ValueError),
        ("earth", "moon", ValueError),
        ("sun ", "moon", ValueError),
    ],
)
def test_lord_lookup_rejects_noncanonical_values(
    bride: object,
    groom: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        get_graha_maitri_relationship(bride, groom)  # type: ignore[arg-type]


def test_high_level_invalid_result_is_ordered_and_has_no_partial_score() -> None:
    result = calculate_graha_maitri_koota(
        bride_moon_longitude=True,
        groom_moon_longitude=float("nan"),
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["factors"] == []
    assert _result_issues(result) == [
        ("bride.sidereal_moon_longitude", "moon_longitude_invalid"),
        ("groom.sidereal_moon_longitude", "moon_longitude_invalid"),
    ]


def test_missing_longitudes_have_stable_issue_codes() -> None:
    result = calculate_graha_maitri_koota()

    assert _result_issues(result) == [
        ("bride.sidereal_moon_longitude", "moon_longitude_missing"),
        ("groom.sidereal_moon_longitude", "moon_longitude_missing"),
    ]


def test_structured_result_exposes_required_audit_contract() -> None:
    result = calculate_graha_maitri_koota(
        bride_moon_longitude=90.0,
        groom_moon_longitude=60.0,
    )

    assert result["koota"] == GRAHA_MAITRI_KOOTA_ID
    assert result["compatibility_domain"] == GRAHA_MAITRI_COMPATIBILITY_DOMAIN
    assert result["status"] == "complete"
    assert result["score"] == 1.0
    assert result["maximum_score"] == 5.0
    assert result["bride_moon_rashi"]["lord"] == "moon"
    assert result["groom_moon_rashi"]["lord"] == "mercury"
    assert result["bride_to_groom_relationship"] == "friend"
    assert result["groom_to_bride_relationship"] == "enemy"
    assert result["combined_relationship"] == "friend_enemy"
    assert result["direction"] == {"row_role": "bride", "column_role": "groom"}
    assert result["metadata"]["relationship_type"] == "natural_permanent"


def test_calculator_inputs_are_keyword_only() -> None:
    signature = inspect.signature(calculate_graha_maitri_koota)

    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    with pytest.raises(TypeError):
        calculate_graha_maitri_koota(0.0, 30.0)  # type: ignore[misc]


def test_results_are_deterministic_json_safe_and_independent() -> None:
    inputs = {"bride_moon_longitude": 90.0, "groom_moon_longitude": 60.0}
    original = dict(inputs)
    first = calculate_graha_maitri_koota(**inputs)
    second = calculate_graha_maitri_koota(**inputs)

    assert first == second
    assert inputs == original
    json.dumps(first, allow_nan=False)
    first["factors"].append({"changed": True})
    first["bride_moon_rashi"]["warnings"].append(_issue_for_mutation())
    first["references"].append("changed")
    assert len(second["factors"]) == 1
    assert second["bride_moon_rashi"]["warnings"] == []
    assert "changed" not in second["references"]


def test_only_permanent_relationship_inputs_are_present() -> None:
    result = calculate_graha_maitri_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )
    serialized = json.dumps(result)

    for excluded in (
        "temporary",
        "panchadha",
        "lagna",
        "navamsha",
        "nakshatra",
        "bhava",
        "dignity",
        "strength",
        "varna",
        "vashya",
        "tara",
        "yoni",
        "judgement",
        "remedy",
    ):
        assert excluded not in serialized.casefold()


def test_existing_matchmaking_foundation_remains_usable() -> None:
    result = create_empty_matchmaking_result("pair-1")

    assert result["matchmaking_id"] == "pair-1"
    assert result["status"] == "not_evaluated"
    assert result["factors"] == []


def test_public_exports_are_available() -> None:
    assert "moon_longitude_invalid" in MATCHMAKING_GRAHA_MAITRI_ISSUE_CODES
    assert set(GRAHA_MAITRI_COMBINED_SCORES.values()) == {
        ("mutual_friend", 5.0),
        ("friend_neutral", 4.0),
        ("mutual_neutral", 3.0),
        ("friend_enemy", 1.0),
        ("neutral_enemy", 0.5),
        ("mutual_enemy", 0.0),
    }
    assert MatchmakingGrahaMaitriIdentity
    assert MatchmakingGrahaMaitriIssue
    assert MatchmakingGrahaMaitriKootaResult
    assert MatchmakingGrahaMaitriRelationship
    assert classify_graha_maitri_lord
    assert get_graha_maitri_relationship
    assert calculate_graha_maitri_koota


def _result_issues(
    result: MatchmakingGrahaMaitriKootaResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _issue_for_mutation() -> MatchmakingGrahaMaitriIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
