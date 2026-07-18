"""Tests for strict deterministic matchmaking serialization hardening."""

from __future__ import annotations

from collections import UserDict
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum
import inspect
import json
import math
from types import MappingProxyType
from typing import Any, Callable

import pytest

import backend.app.matchmaking as matchmaking
from backend.app.matchmaking import ASHTAKOOTA_KOOTA_ORDER
from backend.app.matchmaking import MATCHMAKING_SCHEMA_VERSION
from backend.app.matchmaking import MATCHMAKING_SERIALIZATION_FAMILIES
from backend.app.matchmaking import MATCHMAKING_SERIALIZATION_SCHEMA_VERSION
from backend.app.matchmaking import MatchmakingAshtakootaResult
from backend.app.matchmaking import MatchmakingNakshatraIdentity
from backend.app.matchmaking import MatchmakingNakshatraPairContext
from backend.app.matchmaking import MatchmakingPair
from backend.app.matchmaking import MatchmakingPairValidationResult
from backend.app.matchmaking import MatchmakingPerson
from backend.app.matchmaking import MatchmakingPersonValidationResult
from backend.app.matchmaking import MatchmakingResult
from backend.app.matchmaking import calculate_ashtakoota
from backend.app.matchmaking import classify_manglik
from backend.app.matchmaking import compare_manglik_classifications
from backend.app.matchmaking import compose_compatibility_report
from backend.app.matchmaking import create_empty_matchmaking_pair
from backend.app.matchmaking import create_empty_matchmaking_result
from backend.app.matchmaking import create_matchmaking_pair
from backend.app.matchmaking import create_matchmaking_person
from backend.app.matchmaking import normalize_matchmaking_nakshatra
from backend.app.matchmaking import serialize_ashtakoota_result
from backend.app.matchmaking import serialize_compatibility_report
from backend.app.matchmaking import serialize_koota_result
from backend.app.matchmaking import serialize_manglik_classification_result
from backend.app.matchmaking import serialize_manglik_compatibility_result
from backend.app.matchmaking import serialize_matchmaking_nakshatra_identity
from backend.app.matchmaking import serialize_matchmaking_nakshatra_pair_context
from backend.app.matchmaking import serialize_matchmaking_pair
from backend.app.matchmaking import serialize_matchmaking_pair_validation
from backend.app.matchmaking import serialize_matchmaking_person
from backend.app.matchmaking import serialize_matchmaking_person_validation
from backend.app.matchmaking import serialize_matchmaking_result
from backend.app.matchmaking import validate_matchmaking_pair
from backend.app.matchmaking import validate_matchmaking_person

EXPECTED_FAMILIES = (
    "matchmaking_person",
    "matchmaking_pair",
    "matchmaking_result",
    "matchmaking_person_validation",
    "matchmaking_pair_validation",
    "matchmaking_nakshatra_identity",
    "matchmaking_nakshatra_pair_context",
    "varna",
    "vashya",
    "tara",
    "yoni",
    "graha_maitri",
    "gana",
    "bhakoot",
    "nadi",
    "ashtakoota_aggregation",
    "manglik_classification",
    "manglik_compatibility",
    "matchmaking_compatibility_report",
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


def _person(person_id: str = "bride") -> dict[str, Any]:
    return create_matchmaking_person(
        person_id=person_id,
        name="Anita" if person_id == "bride" else "Bharat",
        birth_date="1992-04-10",
        birth_time="08:15:00",
        latitude=28.6139,
        longitude=77.209,
        timezone="Asia/Kolkata",
        rashi="mesha",
        nakshatra="ashwini",
        nakshatra_pada=2,
        lagna="karka",
        metadata={"source_components": ["kundali"]},
    )


def _pair() -> dict[str, Any]:
    return create_matchmaking_pair(_person(), _person("groom"))


def _nakshatra_pair() -> dict[str, Any]:
    bride = normalize_matchmaking_nakshatra(0, pada=1, source_person_id="bride")
    groom = normalize_matchmaking_nakshatra(1, pada=2, source_person_id="groom")
    return matchmaking.build_nakshatra_pair_context(bride, groom)


def _aggregate() -> dict[str, Any]:
    return calculate_ashtakoota(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
    )


def _manglik_classification(house: int = 1) -> dict[str, Any]:
    return classify_manglik(
        lagna_sidereal_longitude=1.0,
        mars_sidereal_longitude=(house - 1) * 30.0 + 1.0,
    )


def _manglik_compatibility() -> dict[str, Any]:
    return compare_manglik_classifications(
        bride=_manglik_classification(1),
        groom=_manglik_classification(2),
    )


def _report() -> dict[str, Any]:
    return compose_compatibility_report(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
        bride_lagna_longitude=1.0,
        groom_lagna_longitude=1.0,
        bride_mars_longitude=1.0,
        groom_mars_longitude=31.0,
    )


def _serializer_cases() -> list[tuple[Callable[..., Any], dict[str, Any]]]:
    person = _person()
    pair = _pair()
    identity = normalize_matchmaking_nakshatra(0, pada=1, source_person_id="bride")
    return [
        (serialize_matchmaking_person, person),
        (serialize_matchmaking_pair, pair),
        (
            serialize_matchmaking_result,
            create_empty_matchmaking_result("bride-groom"),
        ),
        (serialize_matchmaking_person_validation, validate_matchmaking_person(person)),
        (serialize_matchmaking_pair_validation, validate_matchmaking_pair(pair)),
        (serialize_matchmaking_nakshatra_identity, identity),
        (serialize_matchmaking_nakshatra_pair_context, _nakshatra_pair()),
        (serialize_ashtakoota_result, _aggregate()),
        (serialize_manglik_classification_result, _manglik_classification()),
        (serialize_manglik_compatibility_result, _manglik_compatibility()),
    ]


def test_schema_version_and_family_registry_are_exact_and_immutable() -> None:
    assert MATCHMAKING_SCHEMA_VERSION == "1.0"
    assert MATCHMAKING_SERIALIZATION_SCHEMA_VERSION == MATCHMAKING_SCHEMA_VERSION
    assert MATCHMAKING_SERIALIZATION_FAMILIES == EXPECTED_FAMILIES
    assert isinstance(MATCHMAKING_SERIALIZATION_FAMILIES, tuple)


@pytest.mark.parametrize(("serializer", "result"), _serializer_cases())
def test_every_public_result_serializer_returns_equal_json_safe_copy(
    serializer: Callable[..., dict[str, Any]], result: dict[str, Any]
) -> None:
    original = deepcopy(result)

    serialized = serializer(result=result)

    assert serialized == original
    assert serialized is not result
    assert result == original
    assert json.loads(json.dumps(serialized, allow_nan=False)) == serialized


@pytest.mark.parametrize("component", _aggregate()["koota_results"])
def test_all_eight_kootas_serialize_with_exact_order_and_maximum(
    component: dict[str, Any],
) -> None:
    serialized = serialize_koota_result(result=component)

    assert tuple(serialized) == tuple(component)
    assert serialized["koota"] in ASHTAKOOTA_KOOTA_ORDER
    assert serialized["maximum_score"] == EXPECTED_MAXIMUMS[serialized["koota"]]
    assert serialized == component


def test_exact_top_level_field_order_for_foundation_context_and_aggregate() -> None:
    cases = (
        (serialize_matchmaking_person(result=_person()), MatchmakingPerson),
        (serialize_matchmaking_pair(result=_pair()), MatchmakingPair),
        (
            serialize_matchmaking_result(
                result=create_empty_matchmaking_result("pair")
            ),
            MatchmakingResult,
        ),
        (
            serialize_matchmaking_person_validation(
                result=validate_matchmaking_person(_person())
            ),
            MatchmakingPersonValidationResult,
        ),
        (
            serialize_matchmaking_pair_validation(
                result=validate_matchmaking_pair(_pair())
            ),
            MatchmakingPairValidationResult,
        ),
        (
            serialize_matchmaking_nakshatra_identity(
                result=normalize_matchmaking_nakshatra(0, pada=1)
            ),
            MatchmakingNakshatraIdentity,
        ),
        (
            serialize_matchmaking_nakshatra_pair_context(result=_nakshatra_pair()),
            MatchmakingNakshatraPairContext,
        ),
        (serialize_ashtakoota_result(result=_aggregate()), MatchmakingAshtakootaResult),
    )
    for result, contract in cases:
        assert tuple(result) == tuple(contract.__annotations__)


def test_existing_invalid_states_remain_serializable() -> None:
    assert serialize_ashtakoota_result(result=calculate_ashtakoota())["status"] == (
        "invalid"
    )
    invalid_classification = classify_manglik()
    assert (
        serialize_manglik_classification_result(result=invalid_classification)
        == invalid_classification
    )
    invalid_comparison = compare_manglik_classifications(
        bride=invalid_classification,
        groom=invalid_classification,
    )
    assert (
        serialize_manglik_compatibility_result(result=invalid_comparison)
        == invalid_comparison
    )


def test_all_eight_existing_invalid_koota_shapes_are_supported() -> None:
    pair = create_empty_matchmaking_pair()
    invalid = [
        matchmaking.calculate_varna_koota(
            pair, subject_role="person_a", comparison_role="person_b"
        ),
        matchmaking.calculate_vashya_koota(),
        matchmaking.calculate_tara_koota(
            pair, bride_role="person_a", groom_role="person_b"
        ),
        matchmaking.calculate_yoni_koota(
            pair, bride_role="person_a", groom_role="person_b"
        ),
        matchmaking.calculate_graha_maitri_koota(),
        matchmaking.calculate_gana_koota(
            pair, bride_role="person_a", groom_role="person_b"
        ),
        matchmaking.calculate_bhakoot_koota(),
        matchmaking.calculate_nadi_koota(
            pair, bride_role="person_a", groom_role="person_b"
        ),
    ]

    assert [serialize_koota_result(result=item)["status"] for item in invalid] == [
        "invalid"
    ] * 8


def test_mapping_proxy_mapping_subclass_and_list_subclass_become_builtins() -> None:
    class ListSubclass(list[str]):
        pass

    runtime = _person()
    runtime["metadata"] = UserDict(runtime["metadata"])
    runtime["metadata"]["source_components"] = ListSubclass(["kundali"])

    serialized = serialize_matchmaking_person(result=MappingProxyType(runtime))

    assert type(serialized) is dict
    assert type(serialized["metadata"]) is dict
    assert type(serialized["metadata"]["source_components"]) is list


def test_repeated_serialization_allocates_every_mutable_path_independently() -> None:
    runtime = _aggregate()
    first = serialize_ashtakoota_result(result=runtime)
    second = serialize_ashtakoota_result(result=runtime)

    first["koota_results"][0]["factors"].append({"mutated": True})
    first["metadata"]["koota_order"].append("mutated")

    assert second == runtime
    assert (
        runtime["koota_results"][0]["factors"] != first["koota_results"][0]["factors"]
    )
    assert runtime["metadata"]["koota_order"] != first["metadata"]["koota_order"]


def test_serialization_preserves_fractional_scores_without_rounding() -> None:
    result = create_empty_matchmaking_result("fractional")
    result["status"] = "complete"
    result["score"] = 0.123456789012345
    result["maximum_score"] = 1.0
    result["percentage"] = 12.3456789012345
    result["metadata"]["calculation_complete"] = True

    serialized = serialize_matchmaking_result(result=result)

    assert serialized["score"] == 0.123456789012345
    assert serialized["percentage"] == 12.3456789012345


def test_negative_zero_is_canonicalized_recursively_without_mutating_input() -> None:
    result = create_empty_matchmaking_result("zero")
    result["score"] = -0.0
    result["maximum_score"] = -0.0
    result["percentage"] = -0.0
    result["notes"] = [{"nested": -0.0}]

    serialized = serialize_matchmaking_result(result=result)

    assert math.copysign(1.0, serialized["score"]) == 1.0
    assert math.copysign(1.0, serialized["notes"][0]["nested"]) == 1.0
    assert math.copysign(1.0, result["score"]) == -1.0


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_values_are_rejected_at_any_depth(bad: float) -> None:
    result = create_empty_matchmaking_result("unsafe")
    result["notes"] = [{"nested": [bad]}]

    with pytest.raises(ValueError, match="NaN or infinity"):
        serialize_matchmaking_result(result=result)


@dataclass
class _UnsupportedDataclass:
    value: str


class _UnsupportedEnum(Enum):
    VALUE = "value"


@pytest.mark.parametrize(
    "bad",
    [
        ("tuple",),
        {"set"},
        frozenset({"frozen"}),
        _UnsupportedEnum.VALUE,
        _UnsupportedDataclass("value"),
        b"bytes",
        bytearray(b"bytes"),
        memoryview(b"bytes"),
        date(2026, 1, 1),
        time(1, 2, 3),
        datetime(2026, 1, 1),
        ValueError("error"),
        lambda: None,
        object(),
    ],
)
def test_non_json_python_values_are_rejected(bad: object) -> None:
    result = create_empty_matchmaking_result("unsafe")
    result["notes"] = [bad]

    with pytest.raises(TypeError):
        serialize_matchmaking_result(result=result)


def test_boolean_is_rejected_for_numeric_fields() -> None:
    result = create_empty_matchmaking_result("boolean-score")
    result["score"] = True

    with pytest.raises(TypeError, match="real number"):
        serialize_matchmaking_result(result=result)


def test_non_string_mapping_key_is_rejected() -> None:
    result = create_empty_matchmaking_result("bad-key")
    result["notes"] = [{1: "value"}]

    with pytest.raises(ValueError, match="non-string key"):
        serialize_matchmaking_result(result=result)


def test_direct_and_indirect_cycles_are_rejected() -> None:
    direct = create_empty_matchmaking_result("direct")
    direct["notes"].append(direct["notes"])
    with pytest.raises(ValueError, match="cycle"):
        serialize_matchmaking_result(result=direct)

    indirect = create_empty_matchmaking_result("indirect")
    wrapper: dict[str, Any] = {"back": indirect["notes"]}
    indirect["notes"].append(wrapper)
    with pytest.raises(ValueError, match="cycle"):
        serialize_matchmaking_result(result=indirect)


def test_shared_mutable_paths_and_cross_component_aliases_are_rejected() -> None:
    result = create_empty_matchmaking_result("alias")
    shared: list[str] = []
    result["warnings"] = shared
    result["references"] = shared
    with pytest.raises(ValueError, match="shares a mutable collection"):
        serialize_matchmaking_result(result=result)

    aggregate = _aggregate()
    aggregate["koota_results"][1]["warnings"] = aggregate["koota_results"][0][
        "warnings"
    ]
    with pytest.raises(ValueError, match="shares a mutable collection"):
        serialize_ashtakoota_result(result=aggregate)


@pytest.mark.parametrize("mutation", ["missing", "unexpected", "reordered"])
def test_exact_field_shape_and_order_are_enforced(mutation: str) -> None:
    result = _person()
    if mutation == "missing":
        del result["name"]
    elif mutation == "unexpected":
        result["deprecated_name"] = result["name"]
    else:
        result["name"] = result.pop("name")

    with pytest.raises(ValueError, match="fields or field order"):
        serialize_matchmaking_person(result=result)


def test_nested_field_order_and_schema_identifiers_are_enforced() -> None:
    result = _person()
    result["metadata"]["component"] = "person"
    with pytest.raises(ValueError, match="component"):
        serialize_matchmaking_person(result=result)

    result = _person()
    result["metadata"]["schema_version"] = "2.0"
    with pytest.raises(ValueError, match="schema_version"):
        serialize_matchmaking_person(result=result)

    result = _person()
    result["metadata"]["component"] = result["metadata"].pop("component")
    with pytest.raises(ValueError, match="fields or field order"):
        serialize_matchmaking_person(result=result)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "partial"),
        ("maximum_score", 9.0),
        ("score", -1.0),
        ("score", 9.0),
    ],
)
def test_invalid_koota_status_score_and_maximum_are_rejected(
    field: str, value: object
) -> None:
    result = deepcopy(_aggregate()["koota_results"][-1])
    result[field] = value

    with pytest.raises(ValueError):
        serialize_koota_result(result=result)


def test_unknown_koota_category_direction_and_metadata_are_rejected() -> None:
    result = deepcopy(_aggregate()["koota_results"][-1])
    result["bride_nadi"]["nadi"] = "unknown"
    with pytest.raises(ValueError, match="nadi"):
        serialize_koota_result(result=result)

    result = deepcopy(_aggregate()["koota_results"][-1])
    result["direction"]["groom_role"] = "person_a"
    with pytest.raises(ValueError):
        serialize_koota_result(result=result)

    result = deepcopy(_aggregate()["koota_results"][-1])
    result["metadata"]["calculation"] = "other"
    with pytest.raises(ValueError, match="metadata"):
        serialize_koota_result(result=result)


@pytest.mark.parametrize(
    ("koota", "field", "value"),
    [
        ("yoni", "same_yoni", True),
        ("gana", "same_gana", True),
        ("bhakoot", "bhakoot_dosha", False),
        ("nadi", "nadi_dosha", True),
        ("graha_maitri", "same_lord", True),
    ],
)
def test_inconsistent_duplicated_koota_summaries_are_rejected(
    koota: str, field: str, value: object
) -> None:
    result = next(
        deepcopy(component)
        for component in _aggregate()["koota_results"]
        if component["koota"] == koota
    )
    result[field] = value

    with pytest.raises(ValueError, match="inconsistent"):
        serialize_koota_result(result=result)


def test_missing_score_on_complete_and_score_on_invalid_are_rejected() -> None:
    complete = deepcopy(_aggregate()["koota_results"][0])
    complete["score"] = None
    with pytest.raises(ValueError, match="score"):
        serialize_koota_result(result=complete)

    invalid = deepcopy(matchmaking.calculate_vashya_koota())
    invalid["score"] = 0.0
    with pytest.raises(ValueError):
        serialize_koota_result(result=invalid)


@pytest.mark.parametrize("mutation", ["order", "duplicate", "maximum", "total"])
def test_malformed_ashtakoota_aggregate_is_rejected(mutation: str) -> None:
    result = _aggregate()
    if mutation == "order":
        result["koota_results"][0], result["koota_results"][1] = (
            result["koota_results"][1],
            result["koota_results"][0],
        )
    elif mutation == "duplicate":
        result["koota_results"][1] = deepcopy(result["koota_results"][0])
    elif mutation == "maximum":
        result["maximum_score_by_koota"]["nadi"] = 9.0
    else:
        result["total_score"] += 1.0

    with pytest.raises(ValueError):
        serialize_ashtakoota_result(result=result)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("classification", "partial_manglik"),
        ("reference_point", "moon"),
        ("mars_house", 13),
        ("applicable_manglik_houses", [1, 2, 4, 7, 8, 12]),
    ],
)
def test_malformed_manglik_classification_is_rejected(
    field: str, value: object
) -> None:
    result = _manglik_classification()
    result[field] = value

    with pytest.raises((TypeError, ValueError)):
        serialize_manglik_classification_result(result=result)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("bride_classification", "non_manglik"),
        ("pair_classification", "both_manglik"),
        ("comparison_status", "same_status"),
        ("bride_reference_point", "moon"),
        ("bride_mars_house", 12),
        ("reasons", ["invented"]),
    ],
)
def test_malformed_manglik_comparison_is_rejected(field: str, value: object) -> None:
    result = _manglik_compatibility()
    result[field] = value

    with pytest.raises((TypeError, ValueError)):
        serialize_manglik_compatibility_result(result=result)


def test_existing_report_serializer_remains_strict_json_safe_and_independent() -> None:
    runtime = _report()
    first = serialize_compatibility_report(report=runtime)
    second = serialize_compatibility_report(report=runtime)

    assert first == runtime == second
    assert first is not runtime
    assert json.loads(json.dumps(first, allow_nan=False)) == first
    first["sections"].append("mutated")
    assert second == runtime


def test_serializers_are_keyword_only_and_publicly_exported() -> None:
    functions = (
        serialize_matchmaking_person,
        serialize_matchmaking_pair,
        serialize_matchmaking_result,
        serialize_matchmaking_person_validation,
        serialize_matchmaking_pair_validation,
        serialize_matchmaking_nakshatra_identity,
        serialize_matchmaking_nakshatra_pair_context,
        serialize_koota_result,
        serialize_ashtakoota_result,
        serialize_manglik_classification_result,
        serialize_manglik_compatibility_result,
    )
    for function in functions:
        parameter = next(iter(inspect.signature(function).parameters.values()))
        assert parameter.name == "result"
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert getattr(matchmaking, function.__name__) is function
        assert function.__name__ in matchmaking.__all__
    report_parameter = next(
        iter(inspect.signature(serialize_compatibility_report).parameters.values())
    )
    assert report_parameter.name == "report"
    assert report_parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_calculator_outputs_are_unchanged_by_serialization() -> None:
    aggregate = _aggregate()
    manglik = _manglik_compatibility()
    report = _report()
    originals = deepcopy((aggregate, manglik, report))

    serialize_ashtakoota_result(result=aggregate)
    serialize_manglik_compatibility_result(result=manglik)
    serialize_compatibility_report(report=report)

    assert (aggregate, manglik, report) == originals
    assert aggregate["total_maximum_score"] == 36.0
    assert manglik["metadata"]["classification_mode"] == "binary"
    assert report["metadata"]["structured_only"] is True
    assert report["metadata"]["combined_score_included"] is False
