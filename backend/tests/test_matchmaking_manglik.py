"""Tests for the deterministic Manglik compatibility foundation."""

from __future__ import annotations

import copy
import inspect
import json
from typing import Any

import pytest

import backend.app.matchmaking as matchmaking
import backend.app.matchmaking.manglik as manglik_module
from backend.app.kundali.placement import get_planet_house_placement
from backend.app.kundali.rashi import get_rashi
from backend.app.matchmaking import BOTH_MANGLIK
from backend.app.matchmaking import BOTH_NON_MANGLIK
from backend.app.matchmaking import BRIDE_MANGLIK_GROOM_NON_MANGLIK
from backend.app.matchmaking import BRIDE_NON_MANGLIK_GROOM_MANGLIK
from backend.app.matchmaking import MANGLIK_CLASSIFICATION
from backend.app.matchmaking import MANGLIK_CLASSIFICATIONS
from backend.app.matchmaking import MANGLIK_COMPARISON_STATUSES
from backend.app.matchmaking import MANGLIK_HOUSES
from backend.app.matchmaking import MANGLIK_PAIR_CLASSIFICATIONS
from backend.app.matchmaking import MATCHMAKING_MANGLIK_ISSUE_CODES
from backend.app.matchmaking import MIXED_MANGLIK_STATUS
from backend.app.matchmaking import NON_MANGLIK_CLASSIFICATION
from backend.app.matchmaking import SAME_MANGLIK_STATUS
from backend.app.matchmaking import ManglikClassificationResult
from backend.app.matchmaking import ManglikCompatibilityResult
from backend.app.matchmaking import MatchmakingManglikCompatibilityMetadata
from backend.app.matchmaking import MatchmakingManglikIssue
from backend.app.matchmaking import MatchmakingManglikMetadata
from backend.app.matchmaking import classify_manglik
from backend.app.matchmaking import classify_manglik_from_chart
from backend.app.matchmaking import compare_manglik_classifications

ALL_HOUSES = tuple(range(1, 13))
NON_MANGLIK_HOUSES = (2, 3, 5, 6, 9, 10, 11)
EXPECTED_CLASSIFICATION_FIELDS = (
    "calculation",
    "status",
    "classification",
    "reference_point",
    "lagna_sidereal_longitude",
    "mars_sidereal_longitude",
    "lagna_rashi_index",
    "mars_rashi_index",
    "mars_house",
    "applicable_manglik_houses",
    "reason",
    "errors",
    "warnings",
    "references",
    "metadata",
)


def _longitude_for_rashi(rashi_index: int, degree: float = 1.0) -> float:
    return (rashi_index - 1) * 30.0 + degree


def _chart(
    lagna_longitude: float = 1.0,
    mars_longitude: float = 1.0,
    *,
    include_redundant: bool = True,
) -> dict[str, Any]:
    lagna_rashi = get_rashi(lagna_longitude)
    placement = get_planet_house_placement(lagna_rashi["index"], mars_longitude)
    lagna: dict[str, Any] = {
        "sidereal_longitude": lagna_longitude,
        "rashi_index": lagna_rashi["index"],
    }
    mars: dict[str, Any] = {
        "planet": "mars",
        "sidereal_longitude": mars_longitude,
    }
    if include_redundant:
        lagna.update(
            {
                "rashi": dict(lagna_rashi),
                "rashi_degree": lagna_rashi["degree_in_rashi"],
            }
        )
        mars.update(
            {
                "rashi_index": placement["rashi_index"],
                "rashi": dict(placement["rashi"]),
                "rashi_degree": placement["rashi_degree"],
                "house_index": placement["house_index"],
                "house_number": placement["house_number"],
            }
        )
    return {"lagna": lagna, "planets": [mars], "houses": []}


def _classify_house(house_number: int) -> ManglikClassificationResult:
    return classify_manglik(
        lagna_sidereal_longitude=1.0,
        mars_sidereal_longitude=(house_number - 1) * 30.0 + 1.0,
    )


def _issues(result: MappingResult) -> list[tuple[str, str]]:
    return [(issue["field"], issue["code"]) for issue in result["errors"]]


MappingResult = ManglikClassificationResult | ManglikCompatibilityResult


def test_public_constants_define_only_the_documented_binary_convention() -> None:
    assert MANGLIK_HOUSES == (1, 4, 7, 8, 12)
    assert 2 not in MANGLIK_HOUSES
    assert MANGLIK_CLASSIFICATIONS == ("manglik", "non_manglik")
    assert MANGLIK_PAIR_CLASSIFICATIONS == (
        "both_manglik",
        "both_non_manglik",
        "bride_manglik_groom_non_manglik",
        "bride_non_manglik_groom_manglik",
    )
    assert MANGLIK_COMPARISON_STATUSES == ("same_status", "mixed_status")
    assert MATCHMAKING_MANGLIK_ISSUE_CODES == (
        "manglik_input_missing",
        "manglik_input_invalid",
        "manglik_chart_invalid",
        "manglik_classification_invalid",
    )


@pytest.mark.parametrize("house_number", MANGLIK_HOUSES)
def test_every_supported_house_is_manglik(house_number: int) -> None:
    result = _classify_house(house_number)

    assert result["status"] == "complete"
    assert result["mars_house"] == house_number
    assert result["classification"] == MANGLIK_CLASSIFICATION
    assert result["reason"] == "mars_in_manglik_house"


@pytest.mark.parametrize("house_number", NON_MANGLIK_HOUSES)
def test_every_other_house_is_non_manglik(house_number: int) -> None:
    result = _classify_house(house_number)

    assert result["status"] == "complete"
    assert result["mars_house"] == house_number
    assert result["classification"] == NON_MANGLIK_CLASSIFICATION
    assert result["reason"] == "mars_not_in_manglik_house"


@pytest.mark.parametrize(
    ("lagna_rashi_index", "mars_rashi_index"),
    [
        (lagna_rashi_index, mars_rashi_index)
        for lagna_rashi_index in ALL_HOUSES
        for mars_rashi_index in ALL_HOUSES
    ],
)
def test_all_144_rashi_pairs_use_canonical_whole_sign_placement(
    lagna_rashi_index: int,
    mars_rashi_index: int,
) -> None:
    result = classify_manglik(
        lagna_sidereal_longitude=_longitude_for_rashi(lagna_rashi_index),
        mars_sidereal_longitude=_longitude_for_rashi(mars_rashi_index),
    )
    expected_house = ((mars_rashi_index - lagna_rashi_index) % 12) + 1

    assert result["lagna_rashi_index"] == lagna_rashi_index
    assert result["mars_rashi_index"] == mars_rashi_index
    assert result["mars_house"] == expected_house
    assert (result["classification"] == MANGLIK_CLASSIFICATION) is (
        expected_house in MANGLIK_HOUSES
    )


@pytest.mark.parametrize("rashi_index", ALL_HOUSES)
def test_same_rashi_is_house_one_at_both_ends_of_sign(rashi_index: int) -> None:
    lower = _longitude_for_rashi(rashi_index, 0.0)
    result = classify_manglik(
        lagna_sidereal_longitude=lower + 29.999999,
        mars_sidereal_longitude=lower,
    )

    assert result["lagna_rashi_index"] == rashi_index
    assert result["mars_rashi_index"] == rashi_index
    assert result["mars_house"] == 1
    assert result["classification"] == MANGLIK_CLASSIFICATION


@pytest.mark.parametrize("rashi_index", ALL_HOUSES)
def test_exact_rashi_boundaries_belong_to_new_sign(rashi_index: int) -> None:
    lower = _longitude_for_rashi(rashi_index, 0.0)
    result = classify_manglik(
        lagna_sidereal_longitude=lower,
        mars_sidereal_longitude=lower,
    )

    assert result["lagna_rashi_index"] == rashi_index
    assert result["mars_rashi_index"] == rashi_index


@pytest.mark.parametrize(
    ("lagna", "mars", "normalized_lagna", "normalized_mars"),
    [
        (0.0, 0.0, 0.0, 0.0),
        (360.0, 360.0, 0.0, 0.0),
        (-360.0, -30.0, 0.0, 330.0),
        (721.0, 750.0, 1.0, 30.0),
        (-1.0, 361.0, 359.0, 1.0),
    ],
)
def test_raw_longitudes_reuse_canonical_normalization(
    lagna: float,
    mars: float,
    normalized_lagna: float,
    normalized_mars: float,
) -> None:
    result = classify_manglik(
        lagna_sidereal_longitude=lagna,
        mars_sidereal_longitude=mars,
    )

    assert result["lagna_sidereal_longitude"] == normalized_lagna
    assert result["mars_sidereal_longitude"] == normalized_mars


@pytest.mark.parametrize(
    "field", ("lagna_sidereal_longitude", "mars_sidereal_longitude")
)
@pytest.mark.parametrize("value", (True, False, "1", [], {}, object()))
def test_raw_classification_rejects_invalid_numeric_types(
    field: str,
    value: object,
) -> None:
    inputs: dict[str, object] = {
        "lagna_sidereal_longitude": 1.0,
        "mars_sidereal_longitude": 1.0,
    }
    inputs[field] = value

    result = classify_manglik(**inputs)

    assert result["status"] == "invalid"
    assert result["classification"] == ""
    assert result["mars_house"] is None
    assert result["errors"][0]["field"] == field
    assert result["errors"][0]["code"] == "manglik_input_invalid"


@pytest.mark.parametrize("value", (float("nan"), float("inf"), float("-inf")))
@pytest.mark.parametrize(
    "field", ("lagna_sidereal_longitude", "mars_sidereal_longitude")
)
def test_raw_classification_rejects_non_finite_values(
    field: str,
    value: float,
) -> None:
    inputs = {
        "lagna_sidereal_longitude": 1.0,
        "mars_sidereal_longitude": 1.0,
    }
    inputs[field] = value

    result = classify_manglik(**inputs)

    assert result["status"] == "invalid"
    assert result["errors"][0]["code"] == "manglik_input_invalid"
    json.dumps(result, allow_nan=False)


def test_missing_raw_inputs_are_ordered_and_do_not_partially_classify() -> None:
    result = classify_manglik()

    assert result["status"] == "invalid"
    assert result["classification"] == ""
    assert result["mars_house"] is None
    assert _issues(result) == [
        ("lagna_sidereal_longitude", "manglik_input_missing"),
        ("mars_sidereal_longitude", "manglik_input_missing"),
    ]


def test_raw_classifier_calls_existing_rashi_and_placement_utilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"rashi": 0, "placement": 0}
    real_rashi = manglik_module.get_rashi
    real_placement = manglik_module.get_planet_house_placement

    def tracked_rashi(longitude: float) -> Any:
        calls["rashi"] += 1
        return real_rashi(longitude)

    def tracked_placement(lagna_rashi_index: int, longitude: float) -> Any:
        calls["placement"] += 1
        return real_placement(lagna_rashi_index, longitude)

    monkeypatch.setattr(manglik_module, "get_rashi", tracked_rashi)
    monkeypatch.setattr(manglik_module, "get_planet_house_placement", tracked_placement)

    result = classify_manglik(
        lagna_sidereal_longitude=1.0,
        mars_sidereal_longitude=91.0,
    )

    assert result["mars_house"] == 4
    assert calls == {"rashi": 1, "placement": 1}


def test_chart_adapter_accepts_real_kundali_contract_without_mutation() -> None:
    chart = _chart(301.0, 31.0)
    original = copy.deepcopy(chart)

    result = classify_manglik_from_chart(chart=chart)
    raw = classify_manglik(
        lagna_sidereal_longitude=301.0,
        mars_sidereal_longitude=31.0,
    )

    assert result == raw
    assert chart == original


def test_chart_adapter_allows_absent_optional_redundant_placement() -> None:
    result = classify_manglik_from_chart(
        chart=_chart(1.0, 31.0, include_redundant=False)
    )

    assert result["status"] == "complete"
    assert result["mars_house"] == 2
    assert result["classification"] == NON_MANGLIK_CLASSIFICATION


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("lagna", "rashi_index"), 2),
        (("lagna", "rashi_degree"), 2.0),
        (("planets", 0, "rashi_index"), 2),
        (("planets", 0, "rashi_degree"), 2.0),
        (("planets", 0, "house_index"), 2),
        (("planets", 0, "house_number"), 2),
    ],
)
def test_chart_adapter_rejects_inconsistent_redundant_placement(
    path: tuple[object, ...],
    value: object,
) -> None:
    chart = _chart()
    target: Any = chart
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    result = classify_manglik_from_chart(chart=chart)

    assert result["status"] == "invalid"
    assert result["errors"][0]["code"] == "manglik_chart_invalid"


@pytest.mark.parametrize("value", (0, 13, -1, 1.5, "1", True))
def test_chart_house_number_is_never_coerced_or_normalized(value: object) -> None:
    chart = _chart()
    chart["planets"][0]["house_number"] = value

    result = classify_manglik_from_chart(chart=chart)

    assert result["status"] == "invalid"
    assert _issues(result) == [
        ("chart.planets.mars.house_number", "manglik_chart_invalid")
    ]


@pytest.mark.parametrize(
    "chart",
    (
        None,
        [],
        {},
        {"lagna": {}, "planets": []},
        {"lagna": {"sidereal_longitude": 1.0, "rashi_index": 1}},
        {"lagna": {"sidereal_longitude": 1.0, "rashi_index": 1}, "planets": {}},
        {"lagna": {"sidereal_longitude": 1.0, "rashi_index": 1}, "planets": [1]},
    ),
)
def test_chart_adapter_rejects_missing_or_malformed_chart_data(chart: object) -> None:
    result = classify_manglik_from_chart(chart=chart)

    assert result["status"] == "invalid"
    assert result["classification"] == ""
    assert result["errors"]


def test_chart_adapter_rejects_missing_duplicate_and_noncanonical_mars() -> None:
    base = _chart(include_redundant=False)
    missing = {**base, "planets": [{"planet": "sun", "sidereal_longitude": 1.0}]}
    duplicate = {**base, "planets": [base["planets"][0], base["planets"][0]]}
    noncanonical = {
        **base,
        "planets": [{"planet": "Mars", "sidereal_longitude": 1.0}],
    }

    assert ("chart.planets.mars", "manglik_input_missing") in _issues(
        classify_manglik_from_chart(chart=missing)
    )
    assert ("chart.planets.mars", "manglik_chart_invalid") in _issues(
        classify_manglik_from_chart(chart=duplicate)
    )
    noncanonical_result = classify_manglik_from_chart(chart=noncanonical)
    assert (
        "chart.planets.0.planet",
        "manglik_chart_invalid",
    ) in _issues(noncanonical_result)


@pytest.mark.parametrize("value", (None, True, 0, 13, -1, 1.5, "1"))
def test_chart_adapter_rejects_invalid_lagna_rashi_index(value: object) -> None:
    chart = _chart(include_redundant=False)
    if value is None:
        del chart["lagna"]["rashi_index"]
    else:
        chart["lagna"]["rashi_index"] = value

    result = classify_manglik_from_chart(chart=chart)

    assert result["status"] == "invalid"
    assert result["errors"][0]["field"] == "chart.lagna.rashi_index"


@pytest.mark.parametrize(
    ("bride_house", "groom_house", "pair", "comparison"),
    [
        (1, 4, BOTH_MANGLIK, SAME_MANGLIK_STATUS),
        (2, 3, BOTH_NON_MANGLIK, SAME_MANGLIK_STATUS),
        (1, 2, BRIDE_MANGLIK_GROOM_NON_MANGLIK, MIXED_MANGLIK_STATUS),
        (2, 1, BRIDE_NON_MANGLIK_GROOM_MANGLIK, MIXED_MANGLIK_STATUS),
    ],
)
def test_every_documented_bride_groom_comparison(
    bride_house: int,
    groom_house: int,
    pair: str,
    comparison: str,
) -> None:
    result = compare_manglik_classifications(
        bride=_classify_house(bride_house),
        groom=_classify_house(groom_house),
    )

    assert result["status"] == "complete"
    assert result["pair_classification"] == pair
    assert result["comparison_status"] == comparison
    assert result["metadata"]["scoring_included"] is False
    assert "score" not in result
    assert "maximum_score" not in result


@pytest.mark.parametrize(("bride_house", "groom_house"), ((1, 4), (2, 3), (1, 2)))
def test_swapping_roles_preserves_same_or_mixed_status(
    bride_house: int,
    groom_house: int,
) -> None:
    bride = _classify_house(bride_house)
    groom = _classify_house(groom_house)

    forward = compare_manglik_classifications(bride=bride, groom=groom)
    reverse = compare_manglik_classifications(bride=groom, groom=bride)

    assert forward["comparison_status"] == reverse["comparison_status"]
    assert forward["bride_classification"] == reverse["groom_classification"]
    assert forward["groom_classification"] == reverse["bride_classification"]
    assert forward["bride_mars_house"] == reverse["groom_mars_house"]
    assert forward["groom_mars_house"] == reverse["bride_mars_house"]


def test_both_manglik_is_not_cancellation_or_judgement() -> None:
    result = compare_manglik_classifications(
        bride=_classify_house(1), groom=_classify_house(12)
    )

    assert result["pair_classification"] == "both_manglik"
    assert result["comparison_status"] == "same_status"
    assert result["metadata"]["cancellation_rules_included"] is False
    assert set(result).isdisjoint(
        {"compatible", "recommendation", "prediction", "remedy", "score"}
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("calculation",), "other"),
        (("status",), "invalid"),
        (("classification",), "partial_manglik"),
        (("reference_point",), "moon"),
        (("lagna_sidereal_longitude",), 361.0),
        (("lagna_rashi_index",), 2),
        (("mars_rashi_index",), 2),
        (("mars_house",), 2),
        (("applicable_manglik_houses",), [1, 2, 4, 7, 8, 12]),
        (("reason",), "other"),
        (("errors",), [{}]),
        (("warnings",), ["warning"]),
        (("references",), ["source"]),
        (("metadata", "reference_points"), ["moon"]),
        (("metadata", "severity_included"), True),
        (("metadata", "cancellation_rules_included"), True),
    ],
)
def test_precomputed_comparison_rejects_every_malformed_contract(
    path: tuple[str, ...],
    value: object,
) -> None:
    bride: Any = copy.deepcopy(_classify_house(1))
    target = bride
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    result = compare_manglik_classifications(
        bride=bride,
        groom=_classify_house(2),
    )

    assert result["status"] == "invalid"
    assert result["pair_classification"] == ""
    assert result["comparison_status"] == ""
    assert _issues(result)[0] == (
        "bride.manglik",
        "manglik_classification_invalid",
    )


@pytest.mark.parametrize("value", (None, True, "manglik", [], object()))
def test_precomputed_comparison_rejects_non_result_values(value: object) -> None:
    result = compare_manglik_classifications(
        bride=value,
        groom=_classify_house(2),
    )

    assert result["status"] == "invalid"
    assert result["bride_manglik"]["status"] == "invalid"
    json.dumps(result, allow_nan=False)


def test_both_invalid_precomputed_results_report_bride_before_groom() -> None:
    result = compare_manglik_classifications(bride=None, groom=None)

    assert _issues(result) == [
        ("bride.manglik", "manglik_classification_invalid"),
        ("groom.manglik", "manglik_classification_invalid"),
    ]


def test_unexpected_dependency_failure_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class PlacementFailure(Exception):
        pass

    def fail_placement(*args: object, **kwargs: object) -> None:
        raise PlacementFailure

    monkeypatch.setattr(manglik_module, "get_planet_house_placement", fail_placement)

    with pytest.raises(PlacementFailure):
        classify_manglik(
            lagna_sidereal_longitude=1.0,
            mars_sidereal_longitude=1.0,
        )


def test_signatures_are_exactly_keyword_only() -> None:
    for function in (
        classify_manglik,
        classify_manglik_from_chart,
        compare_manglik_classifications,
    ):
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(function).parameters.values()
        )

    with pytest.raises(TypeError):
        classify_manglik(1.0, 1.0)  # type: ignore[misc]
    with pytest.raises(TypeError):
        classify_manglik_from_chart(_chart())  # type: ignore[misc]
    with pytest.raises(TypeError):
        compare_manglik_classifications(_classify_house(1), _classify_house(2))  # type: ignore[misc]


def test_result_contracts_are_exact_deterministic_and_json_safe() -> None:
    identity = _classify_house(1)
    comparison = compare_manglik_classifications(
        bride=identity,
        groom=_classify_house(2),
    )

    assert tuple(identity) == EXPECTED_CLASSIFICATION_FIELDS
    assert identity == _classify_house(1)
    assert comparison == compare_manglik_classifications(
        bride=_classify_house(1),
        groom=_classify_house(2),
    )
    json.dumps(identity, allow_nan=False)
    json.dumps(comparison, allow_nan=False)


def test_results_and_nested_mutable_collections_are_independent() -> None:
    bride = _classify_house(1)
    groom = _classify_house(2)
    first = compare_manglik_classifications(bride=bride, groom=groom)
    second = compare_manglik_classifications(bride=bride, groom=groom)

    first["applicable_manglik_houses"].append(2)
    first["reasons"].append("changed")
    first["errors"].append(_mutation_issue())
    first["metadata"]["reference_points"].append("moon")
    first["bride_manglik"]["applicable_manglik_houses"].append(2)
    first["bride_manglik"]["metadata"]["reference_points"].append("venus")

    assert second["applicable_manglik_houses"] == [1, 4, 7, 8, 12]
    assert len(second["reasons"]) == 3
    assert second["errors"] == []
    assert second["metadata"]["reference_points"] == ["lagna"]
    assert second["bride_manglik"]["applicable_manglik_houses"] == [1, 4, 7, 8, 12]
    assert second["bride_manglik"]["metadata"]["reference_points"] == ["lagna"]
    assert bride["applicable_manglik_houses"] == [1, 4, 7, 8, 12]


def test_output_contains_no_score_interpretation_or_excluded_rule_fields() -> None:
    result = compare_manglik_classifications(
        bride=_classify_house(1),
        groom=_classify_house(2),
    )

    assert set(result).isdisjoint(
        {
            "score",
            "maximum_score",
            "partial_manglik",
            "severity",
            "intensity",
            "cancellation",
            "prediction",
            "recommendation",
            "remedy",
            "advice",
            "narrative",
            "navamsha",
        }
    )
    assert result["metadata"]["severity_included"] is False
    assert result["metadata"]["cancellation_rules_included"] is False
    assert result["metadata"]["divisional_charts_included"] is False
    assert result["metadata"]["ashtakoota_recalculated"] is False


def test_all_documented_public_exports_are_available() -> None:
    expected_exports = {
        "MANGLIK_HOUSES",
        "MANGLIK_CLASSIFICATION",
        "NON_MANGLIK_CLASSIFICATION",
        "MANGLIK_CLASSIFICATIONS",
        "MANGLIK_PAIR_CLASSIFICATIONS",
        "MANGLIK_COMPARISON_STATUSES",
        "MATCHMAKING_MANGLIK_ISSUE_CODES",
        "ManglikClassificationResult",
        "ManglikCompatibilityResult",
        "MatchmakingManglikIssue",
        "MatchmakingManglikMetadata",
        "MatchmakingManglikCompatibilityMetadata",
        "classify_manglik",
        "classify_manglik_from_chart",
        "compare_manglik_classifications",
    }

    assert expected_exports <= set(matchmaking.__all__)
    for name in expected_exports:
        assert getattr(matchmaking, name) is not None


def test_existing_matchmaking_exports_remain_usable() -> None:
    empty = matchmaking.create_empty_matchmaking_result()
    ashtakoota = matchmaking.calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=0.0,
    )

    assert empty["status"] == "not_evaluated"
    assert ashtakoota["status"] == "complete"
    assert ashtakoota["total_maximum_score"] == 36.0


def _mutation_issue() -> MatchmakingManglikIssue:
    return {
        "field": "changed",
        "code": "manglik_input_invalid",
        "message_key": "matchmaking.validation.manglik_input_invalid",
        "severity": "error",
        "value": None,
        "metadata": {},
    }


def test_exported_types_are_runtime_importable() -> None:
    assert ManglikClassificationResult is not None
    assert ManglikCompatibilityResult is not None
    assert MatchmakingManglikIssue is not None
    assert MatchmakingManglikMetadata is not None
    assert MatchmakingManglikCompatibilityMetadata is not None
