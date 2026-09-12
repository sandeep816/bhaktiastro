"""Tests for deterministic Nadi Koota matchmaking."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from backend.app.astrology.nakshatra import NAKSHATRA_SPAN_FOR_LOOKUP
from backend.app.astrology.nakshatra import get_nakshatra
from backend.app.constants.nakshatra import NAKSHATRA_LIST
from backend.app.matchmaking import MATCHMAKING_NADI_ISSUE_CODES
from backend.app.matchmaking import NADI_BY_NAKSHATRA_INDEX
from backend.app.matchmaking import NADI_CATEGORIES
from backend.app.matchmaking import NADI_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import NADI_KOOTA_ID
from backend.app.matchmaking import NADI_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import NADI_SCORING_MATRIX
from backend.app.matchmaking import MatchmakingNadiIdentity
from backend.app.matchmaking import MatchmakingNadiIssue
from backend.app.matchmaking import MatchmakingNadiKootaResult
from backend.app.matchmaking import MatchmakingNadiMetadata
from backend.app.matchmaking import MatchmakingNadiRelationship
from backend.app.matchmaking import calculate_bhakoot_koota
from backend.app.matchmaking import calculate_nadi_koota
from backend.app.matchmaking import classify_nadi
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import get_nadi_relationship

EXPECTED_NAKSHATRA_MAPPING = (
    ("Ashwini", "adi"),
    ("Bharani", "madhya"),
    ("Krittika", "antya"),
    ("Rohini", "antya"),
    ("Mrigashira", "madhya"),
    ("Ardra", "adi"),
    ("Punarvasu", "adi"),
    ("Pushya", "madhya"),
    ("Ashlesha", "antya"),
    ("Magha", "antya"),
    ("Purva Phalguni", "madhya"),
    ("Uttara Phalguni", "adi"),
    ("Hasta", "adi"),
    ("Chitra", "madhya"),
    ("Swati", "antya"),
    ("Vishakha", "antya"),
    ("Anuradha", "madhya"),
    ("Jyeshtha", "adi"),
    ("Moola", "adi"),
    ("Purva Ashadha", "madhya"),
    ("Uttara Ashadha", "antya"),
    ("Shravana", "antya"),
    ("Dhanishtha", "madhya"),
    ("Shatabhisha", "adi"),
    ("Purva Bhadrapada", "adi"),
    ("Uttara Bhadrapada", "madhya"),
    ("Revati", "antya"),
)

EXPECTED_SCORING_MATRIX = {
    "adi": {"adi": 0.0, "madhya": 8.0, "antya": 8.0},
    "madhya": {"adi": 8.0, "madhya": 0.0, "antya": 8.0},
    "antya": {"adi": 8.0, "madhya": 8.0, "antya": 0.0},
}


@pytest.mark.parametrize(
    ("index", "name", "nadi"),
    [
        (index, name, nadi)
        for index, (name, nadi) in enumerate(EXPECTED_NAKSHATRA_MAPPING)
    ],
)
def test_all_twenty_seven_nakshatras_classify_by_name_and_index(
    index: int,
    name: str,
    nadi: str,
) -> None:
    by_name = classify_nadi(name)
    by_index = classify_nadi(index)

    assert by_name["is_valid"] is True
    assert by_name["nakshatra"] == by_index["nakshatra"] == name
    assert by_name["nakshatra_index"] == by_index["nakshatra_index"] == index
    assert by_name["nadi"] == by_index["nadi"] == nadi
    assert NADI_BY_NAKSHATRA_INDEX[index] == nadi


def test_mapping_has_exactly_nine_members_per_nadi() -> None:
    assert tuple(NADI_BY_NAKSHATRA_INDEX) == tuple(range(27))
    assert tuple(item.name_en for item in NAKSHATRA_LIST) == tuple(
        name for name, _ in EXPECTED_NAKSHATRA_MAPPING
    )
    assert {
        nadi: tuple(NADI_BY_NAKSHATRA_INDEX.values()).count(nadi)
        for nadi in NADI_CATEGORIES
    } == {"adi": 9, "madhya": 9, "antya": 9}


@pytest.mark.parametrize("index", range(27))
def test_every_core_lower_cusp_reuses_nakshatra_derivation(index: int) -> None:
    core_identity = get_nakshatra(NAKSHATRA_LIST[index].start_degree)
    nadi_identity = classify_nadi(core_identity)

    assert core_identity["index"] == index
    assert nadi_identity["nakshatra_index"] == index
    assert nadi_identity["nadi"] == EXPECTED_NAKSHATRA_MAPPING[index][1]


@pytest.mark.parametrize("index", range(27))
def test_values_immediately_below_each_next_cusp_remain_in_nakshatra(
    index: int,
) -> None:
    next_cusp = (index + 1) * NAKSHATRA_SPAN_FOR_LOOKUP
    core_identity = get_nakshatra(round(next_cusp - 0.000001, 6))

    assert core_identity["index"] == index
    assert classify_nadi(core_identity)["nadi"] == EXPECTED_NAKSHATRA_MAPPING[index][1]


@pytest.mark.parametrize(
    ("longitude", "expected_index"),
    [
        (0.0, 0),
        (360.0, 0),
        (-360.0, 0),
        (-1.0, 26),
        (370.0, 0),
        (733.333333, 1),
    ],
)
def test_core_longitude_normalization_feeds_nadi_without_duplication(
    longitude: float,
    expected_index: int,
) -> None:
    core_identity = get_nakshatra(longitude)
    nadi_identity = classify_nadi(core_identity)

    assert core_identity["index"] == expected_index
    assert nadi_identity["nakshatra_index"] == expected_index


@pytest.mark.parametrize("value", [True, False, "0", None, object()])
def test_core_nakshatra_lookup_rejects_non_real_longitudes(value: object) -> None:
    with pytest.raises(TypeError):
        get_nakshatra(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_core_nakshatra_lookup_rejects_non_finite_longitudes(value: float) -> None:
    with pytest.raises(ValueError):
        get_nakshatra(value)


@pytest.mark.parametrize(
    ("bride", "groom", "score"),
    [
        (bride, groom, score)
        for bride, row in EXPECTED_SCORING_MATRIX.items()
        for groom, score in row.items()
    ],
)
def test_every_symmetric_scoring_matrix_cell(
    bride: str,
    groom: str,
    score: float,
) -> None:
    lookup = get_nadi_relationship(bride, groom)

    assert NADI_SCORING_MATRIX == EXPECTED_SCORING_MATRIX
    assert lookup["score"] == score
    assert lookup["relationship"] == (
        "same_nadi" if bride == groom else "different_nadi"
    )
    assert lookup["same_nadi"] is (bride == groom)
    assert lookup["nadi_dosha"] is (bride == groom)
    assert get_nadi_relationship(groom, bride)["score"] == score


@pytest.mark.parametrize(
    ("bride_index", "groom_index"),
    [(bride, groom) for bride in range(27) for groom in range(27)],
)
def test_all_729_ordered_nakshatra_pairs_follow_exact_symmetric_rule(
    bride_index: int,
    groom_index: int,
) -> None:
    pair = _pair(bride_index, groom_index)
    forward = calculate_nadi_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    reverse = calculate_nadi_koota(
        pair,
        bride_role="person_b",
        groom_role="person_a",
    )
    bride_nadi = EXPECTED_NAKSHATRA_MAPPING[bride_index][1]
    groom_nadi = EXPECTED_NAKSHATRA_MAPPING[groom_index][1]
    same_nadi = bride_nadi == groom_nadi
    expected_score = 0.0 if same_nadi else 8.0

    assert forward["bride_nadi"]["nadi"] == bride_nadi
    assert forward["groom_nadi"]["nadi"] == groom_nadi
    assert forward["same_nakshatra"] is (bride_index == groom_index)
    assert forward["same_nadi"] is same_nadi
    assert forward["nadi_dosha"] is same_nadi
    assert forward["relationship"] == ("same_nadi" if same_nadi else "different_nadi")
    assert forward["score"] == reverse["score"] == expected_score
    assert forward["bride_nadi"]["nadi"] == reverse["groom_nadi"]["nadi"]
    assert forward["groom_nadi"]["nadi"] == reverse["bride_nadi"]["nadi"]


def test_exhaustive_pair_population_has_243_same_and_486_different_nadi_pairs() -> None:
    classifications = tuple(NADI_BY_NAKSHATRA_INDEX.values())
    same_count = sum(
        first == second for first in classifications for second in classifications
    )

    assert same_count == 243
    assert len(classifications) ** 2 - same_count == 486


@pytest.mark.parametrize("index", range(27))
@pytest.mark.parametrize(
    ("bride_pada", "groom_pada", "same_pada"),
    [(2, 2, True), (2, 3, False), (None, None, False)],
)
def test_same_nakshatra_always_has_nadi_dosha_and_zero_score(
    index: int,
    bride_pada: int | None,
    groom_pada: int | None,
    same_pada: bool,
) -> None:
    result = calculate_nadi_koota(
        {
            "person_a": _person("a", index, bride_pada),
            "person_b": _person("b", index, groom_pada),
        },
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["same_nakshatra"] is True
    assert result["same_pada"] is same_pada
    assert result["same_nadi"] is True
    assert result["nadi_dosha"] is True
    assert result["score"] == 0.0


def test_pada_does_not_change_nadi_classification() -> None:
    identities = tuple(classify_nadi(0, pada=pada) for pada in range(1, 5))

    assert {identity["nadi"] for identity in identities} == {"adi"}
    assert tuple(identity["nakshatra_pada"] for identity in identities) == (1, 2, 3, 4)


@pytest.mark.parametrize(
    "value",
    [None, "", True, False, -1, 27, 1.5, object(), "Abhijit", "not-a-star"],
)
def test_nadi_classification_reuses_invalid_nakshatra_behavior(value: object) -> None:
    identity = classify_nadi(value)

    assert identity["is_valid"] is False
    assert identity["nadi"] == ""
    assert identity["errors"]


@pytest.mark.parametrize(
    ("bride", "groom", "exception"),
    [
        (None, "adi", TypeError),
        ("adi", None, TypeError),
        ("", "adi", ValueError),
        ("Adi", "madhya", ValueError),
        ("aadi", "madhya", ValueError),
        ("aadya", "madhya", ValueError),
        ("vata", "madhya", ValueError),
        ("pitta", "madhya", ValueError),
        ("kapha", "madhya", ValueError),
        ("adi ", "madhya", ValueError),
        ("adi", "unknown", ValueError),
    ],
)
def test_category_lookup_rejects_noncanonical_values(
    bride: object,
    groom: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        get_nadi_relationship(bride, groom)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("bride_role", "groom_role", "code"),
    [
        (None, None, "direction_missing"),
        ("unknown", "person_b", "role_invalid"),
        ("person_a", "unknown", "role_invalid"),
        ("person_a", "person_a", "role_invalid"),
    ],
)
def test_invalid_role_assignments_fail_safely(
    bride_role: object,
    groom_role: object,
    code: str,
) -> None:
    result = calculate_nadi_koota(
        _pair(0, 1),
        bride_role=bride_role,
        groom_role=groom_role,
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["bride_nadi"]["nadi"] == ""
    assert result["groom_nadi"]["nadi"] == ""
    assert result["same_nadi"] is None
    assert result["nadi_dosha"] is None
    assert result["factors"] == []
    assert result["errors"][-1]["code"] == code


def test_invalid_pair_has_bride_before_groom_issues_and_no_partial_score() -> None:
    result = calculate_nadi_koota(
        _pair(True, 27),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["bride_nadi"]["nadi"] == ""
    assert result["groom_nadi"]["nadi"] == ""
    assert result["same_nadi"] is None
    assert result["nadi_dosha"] is None
    assert result["factors"] == []
    assert _result_issues(result) == [
        ("bride.nakshatra", "nakshatra_invalid"),
        ("groom.nakshatra", "nakshatra_index_out_of_range"),
    ]


def test_structured_result_exposes_symmetric_audit_contract() -> None:
    result = calculate_nadi_koota(
        _pair(0, 1),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["koota"] == NADI_KOOTA_ID
    assert result["compatibility_domain"] == NADI_COMPATIBILITY_DOMAIN
    assert result["status"] == "complete"
    assert result["score"] == result["maximum_score"] == 8.0
    assert result["direction"] == {
        "bride_role": "person_a",
        "groom_role": "person_b",
    }
    assert result["bride_nadi"]["nadi"] == "adi"
    assert result["groom_nadi"]["nadi"] == "madhya"
    assert result["relationship"] == "different_nadi"
    assert result["same_nadi"] is False
    assert result["nadi_dosha"] is False
    assert result["metadata"]["directional"] is False
    assert result["metadata"]["symmetric"] is True


def test_pair_is_positional_and_roles_are_keyword_only() -> None:
    signature = inspect.signature(calculate_nadi_koota)

    assert signature.parameters["pair"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert signature.parameters["bride_role"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["groom_role"].kind is inspect.Parameter.KEYWORD_ONLY
    assert "bride_moon_longitude" not in signature.parameters
    assert "groom_moon_longitude" not in signature.parameters


def test_results_are_deterministic_json_safe_and_independent() -> None:
    pair = _pair(0, 1)
    original = deepcopy(pair)
    first = calculate_nadi_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    second = calculate_nadi_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )

    assert pair == original
    assert first == second
    json.dumps(first, allow_nan=False)
    first["factors"].append({"changed": True})
    first["bride_nadi"]["warnings"].append(_issue_for_mutation())
    first["person_a_nakshatra"]["warnings"].append(_issue_for_mutation())
    first["references"].append("changed")
    assert len(second["factors"]) == 1
    assert second["bride_nadi"]["warnings"] == []
    assert second["person_a_nakshatra"]["warnings"] == []
    assert "changed" not in second["references"]


def test_no_cancellation_or_exception_inputs_affect_result() -> None:
    pair = _pair(0, 5)
    pair.update(
        {
            "rashi": "Mesha",
            "rashi_lord": "mars",
            "gotra": "test",
            "lagna": "Karka",
            "navamsha": "Tula",
            "cancellation": True,
        }
    )
    result = calculate_nadi_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    serialized = json.dumps(result).casefold()

    assert result["same_nadi"] is True
    assert result["score"] == 0.0
    for excluded in (
        "rashi_lord",
        "gotra",
        "lagna",
        "navamsha",
        "cancellation",
        "exception",
        "judgement",
        "remedy",
    ):
        assert excluded not in serialized


def test_existing_matchmaking_foundation_and_bhakoot_remain_usable() -> None:
    empty = create_empty_matchmaking_result("pair-1")
    bhakoot = calculate_bhakoot_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert empty["status"] == "not_evaluated"
    assert empty["factors"] == []
    assert bhakoot["koota"] == "bhakoot"
    assert bhakoot["status"] == "complete"


def test_public_exports_are_available() -> None:
    assert "nakshatra_invalid" in MATCHMAKING_NADI_ISSUE_CODES
    assert NADI_CATEGORIES == ("adi", "madhya", "antya")
    assert NADI_KOOTA_MAXIMUM_SCORE == 8.0
    assert MatchmakingNadiIdentity
    assert MatchmakingNadiIssue
    assert MatchmakingNadiKootaResult
    assert MatchmakingNadiMetadata
    assert MatchmakingNadiRelationship
    assert classify_nadi
    assert get_nadi_relationship
    assert calculate_nadi_koota


def _pair(first: object, second: object) -> dict[str, object]:
    return {
        "person_a": _person("a", first),
        "person_b": _person("b", second),
    }


def _person(
    person_id: str,
    nakshatra: object,
    pada: object = None,
) -> dict[str, object]:
    return {
        "person_id": person_id,
        "nakshatra": nakshatra,
        "nakshatra_pada": pada,
    }


def _result_issues(
    result: MatchmakingNadiKootaResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _issue_for_mutation() -> MatchmakingNadiIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
