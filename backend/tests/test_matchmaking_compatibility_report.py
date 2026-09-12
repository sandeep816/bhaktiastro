"""Tests for deterministic compatibility report composition."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import math
from typing import Any

import pytest

import backend.app.matchmaking as matchmaking
import backend.app.matchmaking.compatibility_report as report_module
from backend.app.matchmaking import ASHTAKOOTA_KOOTA_ORDER
from backend.app.matchmaking import COMPATIBILITY_REPORT_COMPONENT_ORDER
from backend.app.matchmaking import COMPATIBILITY_REPORT_NOTES
from backend.app.matchmaking import COMPATIBILITY_REPORT_SCHEMA_VERSION
from backend.app.matchmaking import COMPATIBILITY_REPORT_SECTIONS
from backend.app.matchmaking import COMPATIBILITY_REPORT_TYPE
from backend.app.matchmaking import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking import MatchmakingCompatibilityAshtakootaSummary
from backend.app.matchmaking import MatchmakingCompatibilityManglikSummary
from backend.app.matchmaking import MatchmakingCompatibilityPersonSummary
from backend.app.matchmaking import MatchmakingCompatibilityReport
from backend.app.matchmaking import MatchmakingCompatibilityReportIssue
from backend.app.matchmaking import MatchmakingCompatibilityReportMetadata
from backend.app.matchmaking import MatchmakingCompatibilityValidation
from backend.app.matchmaking import aggregate_ashtakoota_results
from backend.app.matchmaking import calculate_ashtakoota
from backend.app.matchmaking import classify_manglik
from backend.app.matchmaking import compare_manglik_classifications
from backend.app.matchmaking import compose_compatibility_report
from backend.app.matchmaking import compose_compatibility_report_from_results
from backend.app.matchmaking import serialize_compatibility_report

REPORT_FIELDS = (
    "schema_version",
    "report_type",
    "status",
    "bride",
    "groom",
    "ashtakoota",
    "koota_results",
    "manglik",
    "validation",
    "errors",
    "warnings",
    "notes",
    "sections",
    "metadata",
)
EXPECTED_MAXIMUMS = {
    "varna": 1.0,
    "vashya": 2.0,
    "tara": 3.0,
    "yoni": 4.0,
    "graha_maitri": 5.0,
    "gana": 6.0,
    "bhakoot": 7.0,
    "nadi": 8.0,
}


def _components(
    bride_moon_longitude: float = 0.0,
    groom_moon_longitude: float = 30.0,
) -> list[dict[str, Any]]:
    return calculate_ashtakoota(
        bride_moon_longitude=bride_moon_longitude,
        groom_moon_longitude=groom_moon_longitude,
    )["koota_results"]


def _aggregate(
    scores: dict[str, float] | None = None,
) -> dict[str, Any]:
    components = deepcopy(_components())
    if scores is not None:
        for component in components:
            component["score"] = scores[component["koota"]]
    return aggregate_ashtakoota_results(
        components,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )


def _manglik(bride_house: int = 1, groom_house: int = 2) -> dict[str, Any]:
    bride = classify_manglik(
        lagna_sidereal_longitude=1.0,
        mars_sidereal_longitude=(bride_house - 1) * 30.0 + 1.0,
    )
    groom = classify_manglik(
        lagna_sidereal_longitude=1.0,
        mars_sidereal_longitude=(groom_house - 1) * 30.0 + 1.0,
    )
    return compare_manglik_classifications(bride=bride, groom=groom)


def _raw(**overrides: object) -> MatchmakingCompatibilityReport:
    values: dict[str, object] = {
        "bride_moon_longitude": 0.0,
        "groom_moon_longitude": 30.0,
        "bride_lagna_longitude": 1.0,
        "groom_lagna_longitude": 1.0,
        "bride_mars_longitude": 1.0,
        "groom_mars_longitude": 31.0,
    }
    values.update(overrides)
    return compose_compatibility_report(**values)


def test_raw_composition_uses_real_components_and_canonical_order() -> None:
    result = _raw()

    assert tuple(result) == REPORT_FIELDS
    assert result["status"] == "complete"
    assert result["schema_version"] == MATCHMAKING_SCHEMA_VERSION
    assert result["report_type"] == COMPATIBILITY_REPORT_TYPE
    assert result["sections"] == list(COMPATIBILITY_REPORT_SECTIONS)
    assert result["notes"] == list(COMPATIBILITY_REPORT_NOTES)
    assert result["metadata"]["component_order"] == list(
        COMPATIBILITY_REPORT_COMPONENT_ORDER
    )
    assert [item["koota"] for item in result["koota_results"]] == list(
        ASHTAKOOTA_KOOTA_ORDER
    )
    assert result["ashtakoota"]["maximum_score_by_koota"] == EXPECTED_MAXIMUMS
    assert result["ashtakoota"]["total_maximum_score"] == 36.0


def test_raw_dependencies_execute_once_in_exact_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    real_ashtakoota = report_module.calculate_ashtakoota
    real_classify = report_module.classify_manglik
    real_compare = report_module.compare_manglik_classifications

    def aggregate(**kwargs: object) -> object:
        calls.append("ashtakoota")
        return real_ashtakoota(**kwargs)

    def classify(**kwargs: object) -> object:
        calls.append("classify")
        return real_classify(**kwargs)

    def compare(**kwargs: object) -> object:
        calls.append("compare")
        return real_compare(**kwargs)

    monkeypatch.setattr(report_module, "calculate_ashtakoota", aggregate)
    monkeypatch.setattr(report_module, "classify_manglik", classify)
    monkeypatch.setattr(report_module, "compare_manglik_classifications", compare)

    assert _raw()["status"] == "complete"
    assert calls == ["ashtakoota", "classify", "classify", "compare"]


@pytest.mark.parametrize(
    ("bride_house", "groom_house", "pair", "comparison"),
    [
        (1, 4, "both_manglik", "same_status"),
        (2, 3, "both_non_manglik", "same_status"),
        (1, 2, "bride_manglik_groom_non_manglik", "mixed_status"),
        (2, 1, "bride_non_manglik_groom_manglik", "mixed_status"),
    ],
)
def test_precomputed_composition_preserves_all_manglik_pair_categories(
    bride_house: int,
    groom_house: int,
    pair: str,
    comparison: str,
) -> None:
    result = compose_compatibility_report_from_results(
        ashtakoota=_aggregate(),
        manglik=_manglik(bride_house, groom_house),
    )

    assert result["manglik"]["pair_classification"] == pair
    assert result["manglik"]["comparison_status"] == comparison
    assert "score" not in result["manglik"]


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ({name: maximum for name, maximum in EXPECTED_MAXIMUMS.items()}, 36.0),
        ({name: 0.0 for name in EXPECTED_MAXIMUMS}, 0.0),
        (
            {
                "varna": 1.0,
                "vashya": 1.5,
                "tara": 1.5,
                "yoni": 2.0,
                "graha_maitri": 3.5,
                "gana": 4.0,
                "bhakoot": 7.0,
                "nadi": 0.0,
            },
            20.5,
        ),
    ],
)
def test_full_zero_and_fractional_aggregate_scores_are_copied_exactly(
    scores: dict[str, float], expected: float
) -> None:
    aggregate = _aggregate(scores)
    result = compose_compatibility_report_from_results(
        ashtakoota=aggregate, manglik=_manglik()
    )

    assert result["ashtakoota"]["total_score"] == expected
    assert result["ashtakoota"]["total_score"] == math.fsum(scores.values())
    assert result["ashtakoota"]["score_by_koota"] == scores
    assert "percentage" not in result
    assert "percentage" not in result["ashtakoota"]


@pytest.mark.parametrize(
    ("raw_values", "normalized"),
    [
        ((360.0, -360.0, 361.0, -1.0, 721.0, -359.0), (0.0, 0.0, 1.0, 359.0, 1.0, 1.0)),
        ((-1.0, 721.0, 30.0, 60.0, 90.0, 120.0), (359.0, 1.0, 30.0, 60.0, 90.0, 120.0)),
    ],
)
def test_raw_longitudes_are_normalized_only_by_existing_calculators(
    raw_values: tuple[float, ...], normalized: tuple[float, ...]
) -> None:
    result = compose_compatibility_report(
        bride_moon_longitude=raw_values[0],
        groom_moon_longitude=raw_values[1],
        bride_lagna_longitude=raw_values[2],
        groom_lagna_longitude=raw_values[3],
        bride_mars_longitude=raw_values[4],
        groom_mars_longitude=raw_values[5],
    )

    observed = (
        result["bride"]["moon_sidereal_longitude"],
        result["groom"]["moon_sidereal_longitude"],
        result["bride"]["lagna_sidereal_longitude"],
        result["groom"]["lagna_sidereal_longitude"],
        result["bride"]["mars_sidereal_longitude"],
        result["groom"]["mars_sidereal_longitude"],
    )
    assert observed == normalized


@pytest.mark.parametrize("boundary", [float(value) for value in range(0, 360, 30)])
def test_exact_rashi_boundaries_preserve_authoritative_mars_house(
    boundary: float,
) -> None:
    result = _raw(
        bride_lagna_longitude=boundary,
        bride_mars_longitude=boundary,
    )

    assert result["manglik"]["bride_mars_house"] == 1
    assert result["manglik"]["bride_classification"] == "manglik"


@pytest.mark.parametrize(
    "field",
    [
        "bride_moon_longitude",
        "groom_moon_longitude",
        "bride_lagna_longitude",
        "groom_lagna_longitude",
        "bride_mars_longitude",
        "groom_mars_longitude",
    ],
)
@pytest.mark.parametrize("value", [None, True, "1", float("nan"), float("inf")])
def test_invalid_raw_inputs_return_json_safe_invalid_reports(
    field: str, value: object
) -> None:
    result = _raw(**{field: value})

    assert result["status"] == "invalid"
    assert result["validation"]["is_valid"] is False
    assert result["validation"]["error_count"] == len(result["errors"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("failing_call", [0, 1, 2, 3])
def test_dependency_exceptions_propagate_fail_fast(
    monkeypatch: pytest.MonkeyPatch, failing_call: int
) -> None:
    calls: list[int] = []
    real_ashtakoota = report_module.calculate_ashtakoota
    real_classify = report_module.classify_manglik
    real_compare = report_module.compare_manglik_classifications

    def check(index: int) -> None:
        calls.append(index)
        if index == failing_call:
            raise RuntimeError(f"failure-{index}")

    def aggregate(**kwargs: object) -> object:
        check(0)
        return real_ashtakoota(**kwargs)

    classify_index = iter((1, 2))

    def classify(**kwargs: object) -> object:
        index = next(classify_index)
        check(index)
        return real_classify(**kwargs)

    def compare(**kwargs: object) -> object:
        check(3)
        return real_compare(**kwargs)

    monkeypatch.setattr(report_module, "calculate_ashtakoota", aggregate)
    monkeypatch.setattr(report_module, "classify_manglik", classify)
    monkeypatch.setattr(report_module, "compare_manglik_classifications", compare)

    with pytest.raises(RuntimeError, match=f"failure-{failing_call}"):
        _raw()
    assert calls == list(range(failing_call + 1))


@pytest.mark.parametrize("argument", ["ashtakoota", "manglik"])
@pytest.mark.parametrize("value", [None, [], "result"])
def test_strict_composer_rejects_wrong_outer_types(
    argument: str, value: object
) -> None:
    inputs: dict[str, object] = {"ashtakoota": _aggregate(), "manglik": _manglik()}
    inputs[argument] = value

    with pytest.raises(TypeError):
        compose_compatibility_report_from_results(**inputs)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("status",), "invalid"),
        (("total_score",), 37.0),
        (("total_maximum_score",), 35.0),
        (("metadata", "schema_version"), "2.0"),
        (("metadata", "execution_mode"), "unknown"),
        (("score_by_koota", "varna"), 2.0),
        (("maximum_score_by_koota", "varna"), 2.0),
    ],
)
def test_strict_composer_rejects_malformed_ashtakoota(
    path: tuple[str, ...], value: object
) -> None:
    aggregate = _aggregate()
    target: dict[str, Any] = aggregate
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(ValueError):
        compose_compatibility_report_from_results(
            ashtakoota=aggregate, manglik=_manglik()
        )


def test_strict_composer_rejects_wrong_koota_count_name_and_order() -> None:
    for mutate in (
        lambda items: items.pop(),
        lambda items: items[0].__setitem__("koota", "unexpected"),
        lambda items: items.reverse(),
    ):
        aggregate = _aggregate()
        mutate(aggregate["koota_results"])
        with pytest.raises(ValueError):
            compose_compatibility_report_from_results(
                ashtakoota=aggregate, manglik=_manglik()
            )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("status",), "invalid"),
        (("bride_classification",), "unknown"),
        (("bride_reference_point",), "moon"),
        (("bride_mars_house",), 13),
        (("applicable_manglik_houses",), [1, 2, 4, 7, 8, 12]),
        (("pair_classification",), "both_non_manglik"),
        (("comparison_status",), "same_status"),
        (("metadata", "schema_version"), "2.0"),
        (("metadata", "scoring_included"), True),
    ],
)
def test_strict_composer_rejects_malformed_manglik(
    path: tuple[str, ...], value: object
) -> None:
    manglik = _manglik()
    target: dict[str, Any] = manglik
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(ValueError):
        compose_compatibility_report_from_results(
            ashtakoota=_aggregate(), manglik=manglik
        )


def test_strict_inputs_reject_non_json_values_non_finite_and_aliasing() -> None:
    aggregate = _aggregate()
    aggregate["references"] = [float("nan")]
    with pytest.raises(ValueError):
        compose_compatibility_report_from_results(
            ashtakoota=aggregate, manglik=_manglik()
        )

    aggregate = _aggregate()
    aggregate["references"] = [("not", "json")]
    with pytest.raises(ValueError):
        compose_compatibility_report_from_results(
            ashtakoota=aggregate, manglik=_manglik()
        )

    aggregate = _aggregate()
    shared: list[str] = []
    aggregate["warnings"] = shared
    aggregate["references"] = shared
    with pytest.raises(ValueError, match="aliasing"):
        compose_compatibility_report_from_results(
            ashtakoota=aggregate, manglik=_manglik()
        )


def test_serializer_returns_equal_independent_json_safe_mapping() -> None:
    report = _raw()
    original = deepcopy(report)

    serialized = serialize_compatibility_report(report=report)

    assert serialized == report == original
    assert serialized is not report
    assert serialized["bride"] is not report["bride"]
    assert serialized["koota_results"] is not report["koota_results"]
    assert serialized["koota_results"][0] is not report["koota_results"][0]
    json.dumps(serialized, allow_nan=False)
    serialized["koota_results"][0]["score"] = -1.0
    assert report == original


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("schema_version",), "2.0"),
        (("report_type",), "other"),
        (("status",), "invalid"),
        (("sections",), []),
        (("notes",), []),
        (("ashtakoota", "total_score"), 99.0),
        (("manglik", "bride_mars_house"), 13),
        (("validation", "validated_component_count"), 1),
        (("metadata", "combined_score_included"), True),
    ],
)
def test_serializer_rejects_malformed_reports(
    path: tuple[str, ...], value: object
) -> None:
    report: dict[str, Any] = _raw()
    target = report
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(ValueError):
        serialize_compatibility_report(report=report)


def test_repeated_calls_and_mutable_collections_are_independent() -> None:
    first = _raw()
    second = _raw()

    assert first == second
    first["notes"].append("mutated")
    first["ashtakoota"]["score_by_koota"]["varna"] = -1.0
    first["manglik"]["reasons"].append("mutated")
    assert second == _raw()


def test_public_api_is_keyword_only_and_exports_are_stable() -> None:
    assert COMPATIBILITY_REPORT_SCHEMA_VERSION == MATCHMAKING_SCHEMA_VERSION == "1.0"
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(
            compose_compatibility_report
        ).parameters.values()
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(
            compose_compatibility_report_from_results
        ).parameters.values()
    )
    assert list(inspect.signature(serialize_compatibility_report).parameters) == [
        "report"
    ]
    for name in (
        "MatchmakingCompatibilityAshtakootaSummary",
        "MatchmakingCompatibilityManglikSummary",
        "MatchmakingCompatibilityPersonSummary",
        "MatchmakingCompatibilityReport",
        "MatchmakingCompatibilityReportIssue",
        "MatchmakingCompatibilityReportMetadata",
        "MatchmakingCompatibilityValidation",
        "compose_compatibility_report",
        "compose_compatibility_report_from_results",
        "serialize_compatibility_report",
    ):
        assert name in matchmaking.__all__
        assert getattr(matchmaking, name) is globals()[name]
    assert not hasattr(matchmaking, "compose_compatibility_report_from_charts")


def test_no_interpretation_combined_score_or_rendering_fields_exist() -> None:
    text = json.dumps(_raw(), sort_keys=True)
    for forbidden in (
        "overall_compatibility",
        "pass_fail",
        "marriage_suitability",
        "combined_score",
        "recommendation",
        "remedy",
        "prediction",
        "narrative",
        "pdf",
    ):
        assert f'"{forbidden}"' not in text


def test_task_11_12_and_11_13_direct_outputs_remain_unchanged() -> None:
    aggregate = _aggregate()
    manglik = _manglik()
    aggregate_before = deepcopy(aggregate)
    manglik_before = deepcopy(manglik)

    compose_compatibility_report_from_results(ashtakoota=aggregate, manglik=manglik)

    assert aggregate == aggregate_before
    assert manglik == manglik_before
