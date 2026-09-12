"""Tests for deterministic Vashya Koota matchmaking."""

from __future__ import annotations

import json

import pytest

from backend.app.matchmaking import MATCHMAKING_VASHYA_ISSUE_CODES
from backend.app.matchmaking import VASHYA_CATEGORIES
from backend.app.matchmaking import VASHYA_COMPATIBILITY_DOMAIN
from backend.app.matchmaking import VASHYA_KOOTA_ID
from backend.app.matchmaking import VASHYA_KOOTA_MAXIMUM_SCORE
from backend.app.matchmaking import VASHYA_SCORING_MATRIX
from backend.app.matchmaking import MatchmakingVashyaIdentity
from backend.app.matchmaking import MatchmakingVashyaIssue
from backend.app.matchmaking import MatchmakingVashyaKootaResult
from backend.app.matchmaking import calculate_vashya_koota
from backend.app.matchmaking import classify_vashya
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import get_vashya_score


EXPECTED_SCORING_MATRIX = {
    "chatushpada": {
        "chatushpada": 2.0,
        "manava": 1.0,
        "jalachara": 1.0,
        "vanachara": 1.5,
        "keeta": 1.0,
    },
    "manava": {
        "chatushpada": 1.0,
        "manava": 2.0,
        "jalachara": 1.5,
        "vanachara": 0.0,
        "keeta": 1.0,
    },
    "jalachara": {
        "chatushpada": 1.0,
        "manava": 1.5,
        "jalachara": 2.0,
        "vanachara": 1.0,
        "keeta": 1.0,
    },
    "vanachara": {
        "chatushpada": 0.0,
        "manava": 0.0,
        "jalachara": 0.0,
        "vanachara": 2.0,
        "keeta": 0.0,
    },
    "keeta": {
        "chatushpada": 1.0,
        "manava": 1.0,
        "jalachara": 1.0,
        "vanachara": 0.0,
        "keeta": 2.0,
    },
}


@pytest.mark.parametrize(
    ("longitude", "rashi", "category"),
    [
        (1.0, "Mesha", "chatushpada"),
        (31.0, "Vrishabha", "chatushpada"),
        (61.0, "Mithuna", "manava"),
        (91.0, "Karka", "jalachara"),
        (121.0, "Simha", "vanachara"),
        (151.0, "Kanya", "manava"),
        (181.0, "Tula", "manava"),
        (211.0, "Vrishchika", "keeta"),
        (241.0, "Dhanu", "manava"),
        (271.0, "Makara", "chatushpada"),
        (301.0, "Kumbha", "manava"),
        (331.0, "Meena", "jalachara"),
    ],
)
def test_all_twelve_rashis_classify_deterministically(
    longitude: float,
    rashi: str,
    category: str,
) -> None:
    identity = classify_vashya(longitude)

    assert identity["is_valid"] is True
    assert identity["rashi"] == rashi
    assert identity["vashya"] == category
    assert identity["errors"] == []


@pytest.mark.parametrize(
    ("longitude", "degree_in_rashi", "category"),
    [
        (254.999999, 14.999999, "manava"),
        (255.0, 15.0, "chatushpada"),
        (255.000001, 15.000001, "chatushpada"),
        (284.999999, 14.999999, "chatushpada"),
        (285.0, 15.0, "jalachara"),
        (285.000001, 15.000001, "jalachara"),
    ],
)
def test_split_sign_boundaries_are_exact(
    longitude: float,
    degree_in_rashi: float,
    category: str,
) -> None:
    identity = classify_vashya(longitude)

    assert identity["degree_in_rashi"] == degree_in_rashi
    assert identity["vashya"] == category


@pytest.mark.parametrize(
    ("longitude", "normalized", "category"),
    [
        (0.0, 0.0, "chatushpada"),
        (360.0, 0.0, "chatushpada"),
        (-105.0, 255.0, "chatushpada"),
        (645.0, 285.0, "jalachara"),
    ],
)
def test_longitudes_reuse_canonical_normalization(
    longitude: float,
    normalized: float,
    category: str,
) -> None:
    identity = classify_vashya(longitude)

    assert identity["sidereal_moon_longitude"] == normalized
    assert identity["vashya"] == category


@pytest.mark.parametrize(
    ("bride", "groom", "expected"),
    [
        (bride, groom, score)
        for bride, row in EXPECTED_SCORING_MATRIX.items()
        for groom, score in row.items()
    ],
)
def test_every_scoring_matrix_cell(
    bride: str,
    groom: str,
    expected: float,
) -> None:
    assert VASHYA_SCORING_MATRIX == EXPECTED_SCORING_MATRIX
    assert get_vashya_score(bride, groom) == expected


def test_directional_asymmetric_pair_uses_bride_row() -> None:
    forward = calculate_vashya_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=120.0,
    )
    reverse = calculate_vashya_koota(
        bride_moon_longitude=120.0,
        groom_moon_longitude=0.0,
    )

    assert forward["score"] == 1.5
    assert reverse["score"] == 0.0
    assert forward["direction"] == {
        "row_role": "bride",
        "column_role": "groom",
    }


@pytest.mark.parametrize("category", VASHYA_CATEGORIES)
def test_same_category_receives_maximum_score(category: str) -> None:
    assert get_vashya_score(category, category) == VASHYA_KOOTA_MAXIMUM_SCORE


@pytest.mark.parametrize("value", [True, False, "15", None, object()])
def test_classification_rejects_non_real_values(value: object) -> None:
    with pytest.raises(TypeError):
        classify_vashya(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_classification_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError):
        classify_vashya(value)


@pytest.mark.parametrize(
    ("bride", "groom", "exception"),
    [
        (None, "manava", TypeError),
        ("manava", None, TypeError),
        ("", "manava", ValueError),
        ("Manava", "manava", ValueError),
        ("human", "manava", ValueError),
        ("manava", "unknown", ValueError),
    ],
)
def test_category_lookup_rejects_malformed_values(
    bride: object,
    groom: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        get_vashya_score(bride, groom)  # type: ignore[arg-type]


def test_high_level_calculator_returns_safe_ordered_invalid_result() -> None:
    result = calculate_vashya_koota(
        bride_moon_longitude=True,
        groom_moon_longitude=float("nan"),
    )

    assert result["status"] == "invalid"
    assert result["score"] is None
    assert _result_issues(result) == [
        ("bride.sidereal_moon_longitude", "moon_longitude_invalid"),
        ("groom.sidereal_moon_longitude", "moon_longitude_invalid"),
    ]
    assert result["bride_vashya"]["sidereal_moon_longitude"] is None
    assert result["groom_vashya"]["sidereal_moon_longitude"] is None


def test_missing_longitudes_have_stable_issue_codes() -> None:
    result = calculate_vashya_koota()

    assert _result_issues(result) == [
        ("bride.sidereal_moon_longitude", "moon_longitude_missing"),
        ("groom.sidereal_moon_longitude", "moon_longitude_missing"),
    ]


def test_structured_result_exposes_required_contract() -> None:
    result = calculate_vashya_koota(
        bride_moon_longitude=60.0,
        groom_moon_longitude=90.0,
    )

    assert result["koota"] == VASHYA_KOOTA_ID
    assert result["compatibility_domain"] == VASHYA_COMPATIBILITY_DOMAIN
    assert result["status"] == "complete"
    assert result["score"] == 1.5
    assert result["maximum_score"] == 2.0
    assert result["bride_vashya"]["vashya"] == "manava"
    assert result["groom_vashya"]["vashya"] == "jalachara"
    assert result["factors"] == [
        {
            "factor": "vashya_directional_matrix",
            "row_role": "bride",
            "column_role": "groom",
            "bride_vashya": "manava",
            "groom_vashya": "jalachara",
            "awarded_score": 1.5,
        }
    ]


def test_results_are_deterministic_json_safe_and_independent() -> None:
    first = calculate_vashya_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=120.0,
    )
    second = calculate_vashya_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=120.0,
    )

    assert first == second
    json.dumps(first, allow_nan=False)
    first["factors"].append({"changed": True})
    first["bride_vashya"]["warnings"].append(_issue_for_mutation())
    assert len(second["factors"]) == 1
    assert second["bride_vashya"]["warnings"] == []


def test_existing_matchmaking_foundation_contract_remains_usable() -> None:
    result = create_empty_matchmaking_result("pair-1")

    assert result["matchmaking_id"] == "pair-1"
    assert result["status"] == "not_evaluated"
    assert result["factors"] == []


def test_no_other_koota_or_compatibility_prose_is_included() -> None:
    result = calculate_vashya_koota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=120.0,
    )

    assert "varna" not in result
    assert "tara" not in result
    assert "ashtakoota" not in result
    assert "summary" not in result
    assert "judgement" not in result
    assert result["references"] == []


def test_public_imports_work_from_matchmaking_package() -> None:
    assert "moon_longitude_invalid" in MATCHMAKING_VASHYA_ISSUE_CODES
    assert MatchmakingVashyaIdentity
    assert MatchmakingVashyaIssue
    assert MatchmakingVashyaKootaResult
    assert classify_vashya
    assert get_vashya_score
    assert calculate_vashya_koota


def _result_issues(
    result: MatchmakingVashyaKootaResult,
) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


def _issue_for_mutation() -> MatchmakingVashyaIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
