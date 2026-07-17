"""Tests for deterministic Ashtakoota aggregation orchestration."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
import math
from typing import Callable

import pytest

import backend.app.matchmaking.ashtakoota as ashtakoota_module
from backend.app.astrology.nakshatra import get_nakshatra
from backend.app.constants.nakshatra import NAKSHATRA_LIST
from backend.app.matchmaking import ASHTAKOOTA_KOOTA_MANIFEST
from backend.app.matchmaking import ASHTAKOOTA_KOOTA_ORDER
from backend.app.matchmaking import ASHTAKOOTA_TOTAL_MAXIMUM_SCORE
from backend.app.matchmaking import MATCHMAKING_ASHTAKOOTA_ISSUE_CODES
from backend.app.matchmaking import AshtakootaKootaDefinition
from backend.app.matchmaking import MatchmakingAshtakootaIssue
from backend.app.matchmaking import MatchmakingAshtakootaMetadata
from backend.app.matchmaking import MatchmakingAshtakootaResult
from backend.app.matchmaking import aggregate_ashtakoota_results
from backend.app.matchmaking import calculate_ashtakoota
from backend.app.matchmaking import calculate_bhakoot_koota
from backend.app.matchmaking import calculate_gana_koota
from backend.app.matchmaking import calculate_graha_maitri_koota
from backend.app.matchmaking import calculate_nadi_koota
from backend.app.matchmaking import calculate_tara_koota
from backend.app.matchmaking import calculate_varna_koota
from backend.app.matchmaking import calculate_vashya_koota
from backend.app.matchmaking import calculate_yoni_koota

EXPECTED_ORDER = (
    "varna",
    "vashya",
    "tara",
    "yoni",
    "graha_maitri",
    "gana",
    "bhakoot",
    "nadi",
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


def test_raw_api_aggregates_all_eight_real_calculators() -> None:
    result = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )
    direct = _direct_components(0.0, 30.0)

    assert result["status"] == "complete"
    assert result["koota_results"] == direct
    assert result["score_by_koota"] == {
        component["koota"]: component["score"] for component in direct
    }
    assert result["total_score"] == math.fsum(
        component["score"] for component in direct
    )


def test_manifest_order_maximums_and_total_are_canonical() -> None:
    assert ASHTAKOOTA_KOOTA_ORDER == EXPECTED_ORDER
    assert tuple(item.koota for item in ASHTAKOOTA_KOOTA_MANIFEST) == EXPECTED_ORDER
    assert {
        item.koota: item.maximum_score for item in ASHTAKOOTA_KOOTA_MANIFEST
    } == EXPECTED_MAXIMUMS
    assert len({item.koota for item in ASHTAKOOTA_KOOTA_MANIFEST}) == 8
    assert math.fsum(EXPECTED_MAXIMUMS.values()) == 36.0
    assert ASHTAKOOTA_TOTAL_MAXIMUM_SCORE == 36.0


def test_every_calculator_executes_once_in_canonical_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    wrapped_manifest = tuple(
        definition._replace(
            calculator=_recording_calculator(
                definition.koota,
                definition.calculator,
                calls,
            )
        )
        for definition in ASHTAKOOTA_KOOTA_MANIFEST
    )
    monkeypatch.setattr(
        ashtakoota_module,
        "ASHTAKOOTA_KOOTA_MANIFEST",
        wrapped_manifest,
    )

    result = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert calls == list(EXPECTED_ORDER)
    assert [component["koota"] for component in result["koota_results"]] == list(
        EXPECTED_ORDER
    )
    assert list(result["score_by_koota"]) == list(EXPECTED_ORDER)
    assert list(result["maximum_score_by_koota"]) == list(EXPECTED_ORDER)
    assert result["metadata"]["koota_order"] == list(EXPECTED_ORDER)


def test_precomputed_input_is_reordered_without_recalculation() -> None:
    components = list(reversed(_direct_components(0.0, 30.0)))
    original = deepcopy(components)

    result = aggregate_ashtakoota_results(
        components,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert components == original
    assert [component["koota"] for component in result["koota_results"]] == list(
        EXPECTED_ORDER
    )
    assert list(result["score_by_koota"]) == list(EXPECTED_ORDER)
    assert result["metadata"]["execution_mode"] == "precomputed_results"


def test_precomputed_all_zero_scores_total_zero() -> None:
    components = _direct_components(0.0, 30.0)
    for component in components:
        component["score"] = 0.0

    result = aggregate_ashtakoota_results(
        components,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert result["status"] == "complete"
    assert result["total_score"] == 0.0


def test_precomputed_all_maximum_scores_total_thirty_six() -> None:
    components = _direct_components(0.0, 30.0)
    for component in components:
        component["score"] = EXPECTED_MAXIMUMS[component["koota"]]

    result = aggregate_ashtakoota_results(
        components,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert result["status"] == "complete"
    assert result["total_score"] == result["total_maximum_score"] == 36.0


def test_fractional_scores_are_preserved_without_rounding() -> None:
    result = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert result["total_score"] == 16.5
    assert result["score_by_koota"]["tara"] == 1.5
    assert "percentage_score" not in result


def test_math_fsum_receives_component_scores_in_canonical_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[float, ...]] = []
    real_fsum = math.fsum

    def recording_fsum(values: object) -> float:
        copied = tuple(values)  # type: ignore[arg-type]
        calls.append(copied)
        return real_fsum(copied)

    monkeypatch.setattr(ashtakoota_module.math, "fsum", recording_fsum)
    components = _direct_components(0.0, 30.0)
    result = aggregate_ashtakoota_results(
        components,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    expected_scores = tuple(component["score"] for component in components)
    assert calls[-1] == expected_scores
    assert result["total_score"] == real_fsum(expected_scores)


@pytest.mark.parametrize(
    ("bride", "groom", "equivalent_bride", "equivalent_groom"),
    [
        (0.0, 15.0, 360.0, 375.0),
        (0.0, 15.0, -360.0, -345.0),
        (30.0, 45.0, 390.0, 405.0),
        (359.0, 1.0, -1.0, 361.0),
    ],
)
def test_normalized_longitude_equivalents_are_deterministic(
    bride: float,
    groom: float,
    equivalent_bride: float,
    equivalent_groom: float,
) -> None:
    first = calculate_ashtakoota(
        bride_moon_longitude=bride,
        groom_moon_longitude=groom,
    )
    second = calculate_ashtakoota(
        bride_moon_longitude=equivalent_bride,
        groom_moon_longitude=equivalent_groom,
    )

    assert first == second


@pytest.mark.parametrize("rashi_index", range(1, 13))
def test_exact_rashi_lower_boundaries_feed_existing_rashi_kootas(
    rashi_index: int,
) -> None:
    longitude = float((rashi_index - 1) * 30)
    result = calculate_ashtakoota(
        bride_moon_longitude=longitude,
        groom_moon_longitude=0.0,
    )
    components = _components_by_name(result)

    assert components["vashya"]["bride_vashya"]["rashi_index"] == rashi_index
    assert components["graha_maitri"]["bride_moon_rashi"]["rashi_index"] == rashi_index
    assert components["bhakoot"]["bride_moon_rashi"]["rashi_index"] == rashi_index


@pytest.mark.parametrize("nakshatra_index", range(27))
def test_exact_nakshatra_lower_boundaries_feed_existing_nakshatra_kootas(
    nakshatra_index: int,
) -> None:
    longitude = NAKSHATRA_LIST[nakshatra_index].start_degree
    result = calculate_ashtakoota(
        bride_moon_longitude=longitude,
        groom_moon_longitude=0.0,
    )
    components = _components_by_name(result)

    assert get_nakshatra(longitude)["index"] == nakshatra_index
    for koota in ("tara", "yoni", "gana", "nadi"):
        assert components[koota]["person_a_nakshatra"]["index"] == nakshatra_index


@pytest.mark.parametrize(
    "value",
    [None, "", True, False, "0", object(), float("nan"), float("inf"), float("-inf")],
)
def test_raw_invalid_longitudes_return_safe_invalid_result(value: object) -> None:
    result = calculate_ashtakoota(
        bride_moon_longitude=value,
        groom_moon_longitude=0.0,
    )

    assert result["status"] == "invalid"
    assert result["bride_moon_longitude"] is None
    assert result["total_score"] is None
    assert result["koota_results"] == []
    assert result["score_by_koota"] == {}
    assert result["errors"][0]["field"] == "bride.sidereal_moon_longitude"


def test_two_raw_input_issues_are_bride_before_groom() -> None:
    result = calculate_ashtakoota(
        bride_moon_longitude=None,
        groom_moon_longitude=float("nan"),
    )

    assert [(issue["field"], issue["code"]) for issue in result["errors"]] == [
        ("bride.sidereal_moon_longitude", "moon_longitude_missing"),
        ("groom.sidereal_moon_longitude", "moon_longitude_invalid"),
    ]


@pytest.mark.parametrize(
    ("bride", "groom", "exception"),
    [
        (None, 0.0, TypeError),
        (True, 0.0, TypeError),
        ("0", 0.0, TypeError),
        (float("nan"), 0.0, ValueError),
        (0.0, float("inf"), ValueError),
        (0.0, float("-inf"), ValueError),
    ],
)
def test_precomputed_api_strictly_rejects_invalid_audit_longitudes(
    bride: object,
    groom: object,
    exception: type[Exception],
) -> None:
    with pytest.raises(exception):
        aggregate_ashtakoota_results(
            _direct_components(0.0, 30.0),
            bride_moon_longitude=bride,
            groom_moon_longitude=groom,
        )


@pytest.mark.parametrize("missing", EXPECTED_ORDER)
def test_each_missing_precomputed_koota_is_rejected(missing: str) -> None:
    components = [
        component
        for component in _direct_components(0.0, 30.0)
        if component["koota"] != missing
    ]

    with pytest.raises(ValueError, match="missing"):
        _aggregate(components)


@pytest.mark.parametrize("duplicate", EXPECTED_ORDER)
def test_each_duplicate_precomputed_koota_is_rejected(duplicate: str) -> None:
    components = _direct_components(0.0, 30.0)
    duplicate_component = deepcopy(
        next(component for component in components if component["koota"] == duplicate)
    )
    duplicate_index = EXPECTED_ORDER.index(duplicate)
    components[(duplicate_index + 1) % len(components)] = duplicate_component

    with pytest.raises(ValueError, match="duplicates"):
        _aggregate(components)


def test_unexpected_precomputed_koota_is_rejected() -> None:
    components = _direct_components(0.0, 30.0)
    components[-1]["koota"] = "manglik"

    with pytest.raises(ValueError, match="unexpected"):
        _aggregate(components)


def test_non_string_precomputed_koota_identifier_is_rejected() -> None:
    components = _direct_components(0.0, 30.0)
    components[0]["koota"] = 1

    with pytest.raises(TypeError, match="koota must be a string"):
        _aggregate(components)


@pytest.mark.parametrize(
    "results",
    [None, "results", b"results", {}, object()],
)
def test_incorrect_precomputed_outer_type_is_rejected(results: object) -> None:
    with pytest.raises(TypeError):
        _aggregate(results)


def test_incorrect_precomputed_component_type_is_rejected() -> None:
    components: list[object] = _direct_components(0.0, 30.0)
    components[2] = object()

    with pytest.raises(TypeError):
        _aggregate(components)


@pytest.mark.parametrize("koota", EXPECTED_ORDER)
def test_each_incorrect_component_maximum_is_rejected(koota: str) -> None:
    components = _direct_components(0.0, 30.0)
    component = _find_component(components, koota)
    component["maximum_score"] = EXPECTED_MAXIMUMS[koota] + 1.0

    with pytest.raises(ValueError, match="maximum_score"):
        _aggregate(components)


@pytest.mark.parametrize(
    ("score", "exception"),
    [
        (None, ValueError),
        (True, TypeError),
        ("1", TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (-0.5, ValueError),
        (1.5, ValueError),
    ],
)
def test_invalid_varna_scores_are_rejected(
    score: object,
    exception: type[Exception],
) -> None:
    components = _direct_components(0.0, 30.0)
    _find_component(components, "varna")["score"] = score

    with pytest.raises(exception):
        _aggregate(components)


@pytest.mark.parametrize("koota", EXPECTED_ORDER)
def test_mismatched_component_direction_is_rejected(koota: str) -> None:
    components = _direct_components(0.0, 30.0)
    _find_component(components, koota)["direction"] = {"role": "unknown"}

    with pytest.raises(ValueError, match="direction"):
        _aggregate(components)


def test_invalid_status_and_error_bearing_precomputed_results_are_rejected() -> None:
    components = _direct_components(0.0, 30.0)
    component = _find_component(components, "tara")
    component["status"] = "invalid"
    component["score"] = None
    component["errors"] = [_component_issue()]

    with pytest.raises(ValueError, match="status"):
        _aggregate(components)


def test_non_json_safe_precomputed_component_is_rejected() -> None:
    components = _direct_components(0.0, 30.0)
    _find_component(components, "yoni")["unsupported"] = (1, 2)

    with pytest.raises(TypeError, match="non-JSON-safe"):
        _aggregate(components)


class CalculatorFailure(RuntimeError):
    """Unique test exception for fail-fast propagation."""


@pytest.mark.parametrize("failure_index", range(8))
def test_each_calculator_exception_propagates_and_stops_later_execution(
    monkeypatch: pytest.MonkeyPatch,
    failure_index: int,
) -> None:
    calls: list[str] = []
    manifest = []
    for index, definition in enumerate(ASHTAKOOTA_KOOTA_MANIFEST):
        calculator = (
            _raising_calculator(definition.koota, calls)
            if index == failure_index
            else _recording_calculator(
                definition.koota,
                definition.calculator,
                calls,
            )
        )
        manifest.append(definition._replace(calculator=calculator))
    monkeypatch.setattr(
        ashtakoota_module,
        "ASHTAKOOTA_KOOTA_MANIFEST",
        tuple(manifest),
    )

    with pytest.raises(CalculatorFailure, match=EXPECTED_ORDER[failure_index]):
        calculate_ashtakoota(
            bride_moon_longitude=0.0,
            groom_moon_longitude=30.0,
        )

    assert calls == list(EXPECTED_ORDER[: failure_index + 1])


@pytest.mark.parametrize("invalid_index", range(8))
def test_each_safe_invalid_component_prevents_partial_total_but_keeps_audit_results(
    monkeypatch: pytest.MonkeyPatch,
    invalid_index: int,
) -> None:
    calls: list[str] = []
    manifest = []
    for index, definition in enumerate(ASHTAKOOTA_KOOTA_MANIFEST):
        wrapped = _recording_calculator(
            definition.koota,
            definition.calculator,
            calls,
            make_invalid=index == invalid_index,
        )
        manifest.append(definition._replace(calculator=wrapped))
    monkeypatch.setattr(
        ashtakoota_module,
        "ASHTAKOOTA_KOOTA_MANIFEST",
        tuple(manifest),
    )

    result = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    invalid_koota = EXPECTED_ORDER[invalid_index]
    assert calls == list(EXPECTED_ORDER)
    assert result["status"] == "invalid"
    assert result["total_score"] is None
    assert len(result["koota_results"]) == 8
    assert result["score_by_koota"][invalid_koota] is None
    assert result["errors"][0]["field"] == f"koota_results.{invalid_koota}"


def test_structurally_invalid_raw_component_raises_without_partial_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = ASHTAKOOTA_KOOTA_MANIFEST[0]._replace(
        calculator=lambda *_, **__: object()
    )
    monkeypatch.setattr(
        ashtakoota_module,
        "ASHTAKOOTA_KOOTA_MANIFEST",
        (definition, *ASHTAKOOTA_KOOTA_MANIFEST[1:]),
    )

    with pytest.raises(TypeError, match="must be a mapping"):
        calculate_ashtakoota(
            bride_moon_longitude=0.0,
            groom_moon_longitude=30.0,
        )


def test_swapping_inputs_reexecutes_directional_kootas_without_forced_symmetry() -> (
    None
):
    forward = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=15.0,
    )
    reverse = calculate_ashtakoota(
        bride_moon_longitude=15.0,
        groom_moon_longitude=0.0,
    )

    assert forward["score_by_koota"]["gana"] == 6.0
    assert reverse["score_by_koota"]["gana"] == 5.0
    assert forward["total_score"] == 34.0
    assert reverse["total_score"] == 33.0
    assert _components_by_name(forward)["gana"]["direction"] == {
        "bride_role": "person_a",
        "groom_role": "person_b",
    }


def test_results_are_deterministic_json_safe_and_deeply_independent() -> None:
    source = _direct_components(0.0, 30.0)
    original = deepcopy(source)
    first = aggregate_ashtakoota_results(
        source,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )
    second = aggregate_ashtakoota_results(
        source,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert source == original
    assert first == second
    json.dumps(first, allow_nan=False)
    first["koota_results"][0]["factors"].append({"changed": True})
    first["score_by_koota"]["varna"] = 99.0
    first["maximum_score_by_koota"]["varna"] = 99.0
    first["warnings"].append(_aggregate_issue())
    first["references"].append("changed")
    first["metadata"]["koota_order"].append("changed")
    assert source == original
    assert second["koota_results"][0]["factors"] != first["koota_results"][0]["factors"]
    assert second["score_by_koota"]["varna"] != 99.0
    assert second["maximum_score_by_koota"]["varna"] == 1.0
    assert second["warnings"] == []
    assert second["references"] == []
    assert "changed" not in second["metadata"]["koota_order"]


def test_component_warnings_are_prefixed_in_canonical_order_and_deep_copied() -> None:
    source = _direct_components(0.0, 30.0)
    for component in source:
        component["warnings"] = [
            {
                **_component_issue(),
                "severity": "warning",
                "value": {"nested": []},
            }
        ]

    result = _aggregate(list(reversed(source)))

    assert [warning["field"] for warning in result["warnings"]] == [
        f"{koota}.test" for koota in EXPECTED_ORDER
    ]
    result["warnings"][0]["value"]["nested"].append("changed")
    assert source[0]["warnings"][0]["value"] == {"nested": []}


def test_successful_result_has_exact_documented_top_level_fields() -> None:
    result = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert tuple(result) == (
        "calculation",
        "status",
        "bride_moon_longitude",
        "groom_moon_longitude",
        "koota_results",
        "score_by_koota",
        "maximum_score_by_koota",
        "total_score",
        "total_maximum_score",
        "errors",
        "warnings",
        "references",
        "metadata",
    )


def test_result_contains_no_interpretation_or_future_task_output() -> None:
    result = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )

    assert "percentage_score" not in result
    assert result["metadata"]["percentage_included"] is False
    assert result["metadata"]["interpretation_included"] is False
    assert result["metadata"]["cancellation_included"] is False
    serialized = json.dumps(result).casefold()
    for excluded in (
        "pass_fail",
        "compatibility_label",
        "recommendation",
        "remedy",
        "manglik",
        "dasha",
        "marriage_prediction",
    ):
        assert excluded not in serialized


def test_direct_calculator_outputs_remain_unchanged_after_aggregation() -> None:
    before = _direct_components(0.0, 30.0)
    aggregate = calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )
    after = _direct_components(0.0, 30.0)

    assert before == after == aggregate["koota_results"]


def test_public_api_signatures_and_exports_are_stable() -> None:
    raw_signature = inspect.signature(calculate_ashtakoota)
    strict_signature = inspect.signature(aggregate_ashtakoota_results)

    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in raw_signature.parameters.values()
    )
    assert strict_signature.parameters["results"].kind is (
        inspect.Parameter.POSITIONAL_OR_KEYWORD
    )
    assert strict_signature.parameters["bride_moon_longitude"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert "koota_result_invalid" in MATCHMAKING_ASHTAKOOTA_ISSUE_CODES
    assert AshtakootaKootaDefinition
    assert MatchmakingAshtakootaIssue
    assert MatchmakingAshtakootaMetadata
    assert MatchmakingAshtakootaResult
    assert calculate_ashtakoota
    assert aggregate_ashtakoota_results


def _direct_components(bride: float, groom: float) -> list[dict[str, object]]:
    bride_rashi = ashtakoota_module.get_rashi(bride)
    groom_rashi = ashtakoota_module.get_rashi(groom)
    bride_nakshatra = get_nakshatra(bride)
    groom_nakshatra = get_nakshatra(groom)
    pair = {
        "person_a": {
            "person_id": "bride",
            "rashi": bride_rashi["index"],
            "nakshatra": bride_nakshatra["index"],
            "nakshatra_pada": bride_nakshatra["pada"],
        },
        "person_b": {
            "person_id": "groom",
            "rashi": groom_rashi["index"],
            "nakshatra": groom_nakshatra["index"],
            "nakshatra_pada": groom_nakshatra["pada"],
        },
    }
    return [
        calculate_varna_koota(
            pair,
            subject_role="person_a",
            comparison_role="person_b",
        ),
        calculate_vashya_koota(
            bride_moon_longitude=bride,
            groom_moon_longitude=groom,
        ),
        calculate_tara_koota(
            pair,
            bride_role="person_a",
            groom_role="person_b",
        ),
        calculate_yoni_koota(
            pair,
            bride_role="person_a",
            groom_role="person_b",
        ),
        calculate_graha_maitri_koota(
            bride_moon_longitude=bride,
            groom_moon_longitude=groom,
        ),
        calculate_gana_koota(
            pair,
            bride_role="person_a",
            groom_role="person_b",
        ),
        calculate_bhakoot_koota(
            bride_moon_longitude=bride,
            groom_moon_longitude=groom,
        ),
        calculate_nadi_koota(
            pair,
            bride_role="person_a",
            groom_role="person_b",
        ),
    ]


def _aggregate(results: object) -> MatchmakingAshtakootaResult:
    return aggregate_ashtakoota_results(
        results,
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )


def _find_component(
    components: list[dict[str, object]],
    koota: str,
) -> dict[str, object]:
    return next(component for component in components if component["koota"] == koota)


def _components_by_name(
    result: MatchmakingAshtakootaResult,
) -> dict[str, dict[str, object]]:
    return {
        component["koota"]: component  # type: ignore[misc]
        for component in result["koota_results"]
    }


def _recording_calculator(
    koota: str,
    calculator: Callable[..., object],
    calls: list[str],
    *,
    make_invalid: bool = False,
) -> Callable[..., object]:
    def wrapped(*args: object, **kwargs: object) -> object:
        calls.append(koota)
        result = calculator(*args, **kwargs)
        if make_invalid:
            result = deepcopy(result)
            result["status"] = "invalid"
            result["score"] = None
            result["errors"] = [_component_issue()]
        return result

    return wrapped


def _raising_calculator(
    koota: str,
    calls: list[str],
) -> Callable[..., object]:
    def raise_failure(*_: object, **__: object) -> object:
        calls.append(koota)
        raise CalculatorFailure(koota)

    return raise_failure


def _component_issue() -> dict[str, object]:
    return {
        "field": "test",
        "code": "test",
        "message_key": "matchmaking.validation.test",
        "severity": "error",
        "value": None,
        "metadata": {},
    }


def _aggregate_issue() -> MatchmakingAshtakootaIssue:
    return {
        "field": "test",
        "code": "test",
        "message_key": "matchmaking.validation.test",
        "severity": "warning",
        "value": None,
        "metadata": {},
    }
