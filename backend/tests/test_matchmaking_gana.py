"""Tests for deterministic Gana Koota matchmaking."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from backend.app.astrology.nakshatra import NAKSHATRA_SPAN_FOR_LOOKUP
from backend.app.astrology.nakshatra import get_nakshatra
from backend.app.constants.nakshatra import NAKSHATRA_LIST
from backend.app.matchmaking import GANA_BY_NAKSHATRA_INDEX
from backend.app.matchmaking import GANA_CATEGORIES
from backend.app.matchmaking import GANA_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import GANA_KOOTA_ID
from backend.app.matchmaking import GANA_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import GANA_SCORING_MATRIX
from backend.app.matchmaking import MATCHMAKING_GANA_ISSUE_CODES
from backend.app.matchmaking import MatchmakingGanaIdentity
from backend.app.matchmaking import MatchmakingGanaIssue
from backend.app.matchmaking import MatchmakingGanaKootaResult
from backend.app.matchmaking import MatchmakingGanaRelationship
from backend.app.matchmaking import calculate_gana_koota
from backend.app.matchmaking import calculate_yoni_koota
from backend.app.matchmaking import classify_gana
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import get_gana_relationship

EXPECTED_NAKSHATRA_MAPPING = (
    ("Ashwini", "deva"),
    ("Bharani", "manushya"),
    ("Krittika", "rakshasa"),
    ("Rohini", "manushya"),
    ("Mrigashira", "deva"),
    ("Ardra", "manushya"),
    ("Punarvasu", "deva"),
    ("Pushya", "deva"),
    ("Ashlesha", "rakshasa"),
    ("Magha", "rakshasa"),
    ("Purva Phalguni", "manushya"),
    ("Uttara Phalguni", "manushya"),
    ("Hasta", "deva"),
    ("Chitra", "rakshasa"),
    ("Swati", "deva"),
    ("Vishakha", "rakshasa"),
    ("Anuradha", "deva"),
    ("Jyeshtha", "rakshasa"),
    ("Moola", "rakshasa"),
    ("Purva Ashadha", "manushya"),
    ("Uttara Ashadha", "manushya"),
    ("Shravana", "deva"),
    ("Dhanishtha", "rakshasa"),
    ("Shatabhisha", "rakshasa"),
    ("Purva Bhadrapada", "manushya"),
    ("Uttara Bhadrapada", "manushya"),
    ("Revati", "deva"),
)

EXPECTED_SCORING_MATRIX = {
    "deva": {"deva": 6.0, "manushya": 6.0, "rakshasa": 0.0},
    "manushya": {"deva": 5.0, "manushya": 6.0, "rakshasa": 0.0},
    "rakshasa": {"deva": 1.0, "manushya": 0.0, "rakshasa": 6.0},
}


@pytest.mark.parametrize(
    ("index", "name", "gana"),
    [
        (index, name, gana)
        for index, (name, gana) in enumerate(EXPECTED_NAKSHATRA_MAPPING)
    ],
)
def test_all_twenty_seven_nakshatras_classify_by_name_and_index(
    index: int,
    name: str,
    gana: str,
) -> None:
    by_name = classify_gana(name)
    by_index = classify_gana(index)

    assert by_name["is_valid"] is True
    assert by_name["nakshatra"] == by_index["nakshatra"] == name
    assert by_name["nakshatra_index"] == by_index["nakshatra_index"] == index
    assert by_name["gana"] == by_index["gana"] == gana
    assert GANA_BY_NAKSHATRA_INDEX[index] == gana


def test_mapping_has_exactly_nine_members_per_gana() -> None:
    assert tuple(GANA_BY_NAKSHATRA_INDEX) == tuple(range(27))
    assert tuple(item.name_en for item in NAKSHATRA_LIST) == tuple(
        name for name, _ in EXPECTED_NAKSHATRA_MAPPING
    )
    assert {
        gana: tuple(GANA_BY_NAKSHATRA_INDEX.values()).count(gana)
        for gana in GANA_CATEGORIES
    } == {"deva": 9, "manushya": 9, "rakshasa": 9}


@pytest.mark.parametrize("index", range(27))
def test_every_core_lower_cusp_reuses_nakshatra_derivation(index: int) -> None:
    longitude = NAKSHATRA_LIST[index].start_degree
    core_identity = get_nakshatra(longitude)
    gana_identity = classify_gana(core_identity)

    assert core_identity["index"] == index
    assert gana_identity["nakshatra_index"] == index
    assert gana_identity["gana"] == EXPECTED_NAKSHATRA_MAPPING[index][1]


@pytest.mark.parametrize("index", range(27))
def test_values_immediately_below_each_next_cusp_remain_in_nakshatra(
    index: int,
) -> None:
    next_cusp = (index + 1) * NAKSHATRA_SPAN_FOR_LOOKUP
    longitude = round(next_cusp - 0.000001, 6)
    core_identity = get_nakshatra(longitude)

    assert core_identity["index"] == index
    assert classify_gana(core_identity)["gana"] == EXPECTED_NAKSHATRA_MAPPING[index][1]


@pytest.mark.parametrize(
    ("longitude", "expected_index"),
    [(0.0, 0), (360.0, 0), (-1.0, 26), (370.0, 0), (733.333333, 1)],
)
def test_core_longitude_normalization_feeds_gana_without_duplication(
    longitude: float,
    expected_index: int,
) -> None:
    core_identity = get_nakshatra(longitude)
    gana_identity = classify_gana(core_identity)

    assert core_identity["index"] == expected_index
    assert gana_identity["nakshatra_index"] == expected_index


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
def test_every_directional_scoring_matrix_cell(
    bride: str,
    groom: str,
    score: float,
) -> None:
    lookup = get_gana_relationship(bride, groom)

    assert GANA_SCORING_MATRIX == EXPECTED_SCORING_MATRIX
    assert lookup["bride_gana"] == bride
    assert lookup["groom_gana"] == groom
    assert lookup["score"] == score
    assert lookup["relationship"] == ("same_gana" if bride == groom else "mixed_gana")


@pytest.mark.parametrize("gana", GANA_CATEGORIES)
def test_same_gana_categories_receive_maximum(gana: str) -> None:
    lookup = get_gana_relationship(gana, gana)

    assert lookup["relationship"] == "same_gana"
    assert lookup["score"] == GANA_KOOTA_MAXIMUM_SCORE


@pytest.mark.parametrize(
    ("first", "second"),
    [(0, 4), (1, 3), (2, 8)],
)
def test_different_nakshatras_in_same_gana_receive_maximum(
    first: int,
    second: int,
) -> None:
    result = calculate_gana_koota(
        _pair(first, second),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["same_nakshatra"] is False
    assert result["same_gana"] is True
    assert result["score"] == 6.0


@pytest.mark.parametrize(
    ("bride", "groom", "forward", "reverse"),
    [(0, 1, 6.0, 5.0), (0, 2, 0.0, 1.0)],
)
def test_directional_asymmetric_pairs_transpose_exactly(
    bride: int,
    groom: int,
    forward: float,
    reverse: float,
) -> None:
    pair = _pair(bride, groom)
    first = calculate_gana_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    second = calculate_gana_koota(
        pair,
        bride_role="person_b",
        groom_role="person_a",
    )

    assert first["score"] == forward
    assert second["score"] == reverse
    assert first["bride_gana"]["gana"] == second["groom_gana"]["gana"]
    assert first["groom_gana"]["gana"] == second["bride_gana"]["gana"]


def test_manushya_rakshasa_scores_zero_in_both_orders() -> None:
    assert get_gana_relationship("manushya", "rakshasa")["score"] == 0.0
    assert get_gana_relationship("rakshasa", "manushya")["score"] == 0.0


@pytest.mark.parametrize(
    ("bride_pada", "groom_pada", "same_pada"),
    [(2, 2, True), (2, 3, False), (None, None, False)],
)
def test_same_nakshatra_always_scores_maximum(
    bride_pada: int | None,
    groom_pada: int | None,
    same_pada: bool,
) -> None:
    result = calculate_gana_koota(
        {
            "person_a": _person("a", 15, bride_pada),
            "person_b": _person("b", 15, groom_pada),
        },
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["same_nakshatra"] is True
    assert result["same_pada"] is same_pada
    assert result["same_gana"] is True
    assert result["score"] == 6.0


@pytest.mark.parametrize(
    "value",
    [None, "", True, False, -1, 27, 1.5, object(), "Abhijit", "not-a-star"],
)
def test_gana_classification_reuses_invalid_nakshatra_behavior(value: object) -> None:
    identity = classify_gana(value)

    assert identity["is_valid"] is False
    assert identity["gana"] == ""
    assert identity["errors"]


@pytest.mark.parametrize(
    ("bride", "groom", "exception"),
    [
        (None, "deva", TypeError),
        ("deva", None, TypeError),
        ("", "deva", ValueError),
        ("Deva", "manushya", ValueError),
        ("divine", "manushya", ValueError),
        ("deva ", "manushya", ValueError),
        ("asura", "manushya", ValueError),
        ("deva", "unknown", ValueError),
    ],
)
def test_category_lookup_rejects_noncanonical_values(
    bride: object,
    groom: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        get_gana_relationship(bride, groom)  # type: ignore[arg-type]


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
    result = calculate_gana_koota(
        _pair(0, 1),
        bride_role=bride_role,
        groom_role=groom_role,
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["factors"] == []
    assert result["errors"][-1]["code"] == code


def test_invalid_pair_has_bride_before_groom_issues_and_no_partial_score() -> None:
    result = calculate_gana_koota(
        _pair(True, 27),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert result["factors"] == []
    assert _result_issues(result) == [
        ("bride.nakshatra", "nakshatra_invalid"),
        ("groom.nakshatra", "nakshatra_index_out_of_range"),
    ]


def test_structured_result_exposes_directional_audit_contract() -> None:
    result = calculate_gana_koota(
        _pair(0, 1),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert result["koota"] == GANA_KOOTA_ID
    assert result["compatibility_domain"] == GANA_COMPATIBILITY_DOMAIN
    assert result["status"] == "complete"
    assert result["score"] == 6.0
    assert result["maximum_score"] == 6.0
    assert result["direction"] == {
        "bride_role": "person_a",
        "groom_role": "person_b",
    }
    assert result["bride_gana"]["gana"] == "deva"
    assert result["groom_gana"]["gana"] == "manushya"
    assert result["relationship"] == "mixed_gana"
    assert result["same_gana"] is False
    assert result["factors"] == [
        {
            "factor": "gana_directional_matrix",
            "row_role": "bride",
            "column_role": "groom",
            "bride_gana": "deva",
            "groom_gana": "manushya",
            "relationship": "mixed_gana",
            "awarded_score": 6.0,
        }
    ]
    assert result["metadata"]["directional"] is True
    assert result["metadata"]["symmetric"] is False


def test_pair_is_positional_and_roles_are_keyword_only() -> None:
    signature = inspect.signature(calculate_gana_koota)

    assert signature.parameters["pair"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert signature.parameters["bride_role"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["groom_role"].kind is inspect.Parameter.KEYWORD_ONLY
    assert "bride_moon_longitude" not in signature.parameters
    assert "groom_moon_longitude" not in signature.parameters


def test_results_are_deterministic_json_safe_and_independent() -> None:
    pair = _pair(0, 1)
    original = deepcopy(pair)
    first = calculate_gana_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    second = calculate_gana_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )

    assert pair == original
    assert first == second
    json.dumps(first, allow_nan=False)
    first["factors"].append({"changed": True})
    first["bride_gana"]["warnings"].append(_issue_for_mutation())
    first["person_a_nakshatra"]["warnings"].append(_issue_for_mutation())
    first["references"].append("changed")
    assert len(second["factors"]) == 1
    assert second["bride_gana"]["warnings"] == []
    assert second["person_a_nakshatra"]["warnings"] == []
    assert "changed" not in second["references"]


def test_no_other_koota_or_cancellation_inputs_affect_result() -> None:
    pair = _pair(0, 2)
    pair["rashi"] = "Mesha"
    pair["lagna"] = "Karka"
    pair["navamsha"] = "Tula"
    result = calculate_gana_koota(
        pair,
        bride_role="person_a",
        groom_role="person_b",
    )
    serialized = json.dumps(result).casefold()

    assert result["score"] == 0.0
    for excluded in (
        "varna",
        "vashya",
        "tara",
        "yoni",
        "graha_maitri",
        "nadi",
        "bhakoot",
        "lagna",
        "navamsha",
        "cancellation",
        "judgement",
        "remedy",
    ):
        assert excluded not in serialized


def test_existing_matchmaking_foundation_and_yoni_remain_usable() -> None:
    empty = create_empty_matchmaking_result("pair-1")
    yoni = calculate_yoni_koota(
        _pair(0, 1),
        bride_role="person_a",
        groom_role="person_b",
    )

    assert empty["status"] == "not_evaluated"
    assert empty["factors"] == []
    assert yoni["koota"] == "yoni"
    assert yoni["status"] == "complete"


def test_public_exports_are_available() -> None:
    assert "nakshatra_invalid" in MATCHMAKING_GANA_ISSUE_CODES
    assert GANA_CATEGORIES == ("deva", "manushya", "rakshasa")
    assert MatchmakingGanaIdentity
    assert MatchmakingGanaIssue
    assert MatchmakingGanaKootaResult
    assert MatchmakingGanaRelationship
    assert classify_gana
    assert get_gana_relationship
    assert calculate_gana_koota


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
    result: MatchmakingGanaKootaResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _issue_for_mutation() -> MatchmakingGanaIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
