"""Strict deterministic serialization for Sprint 11 matchmaking results."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import is_dataclass
from datetime import date, datetime, time
from enum import Enum
import math
from numbers import Integral, Real
from typing import TypedDict, cast

from backend.app.matchmaking.ashtakoota import (
    ASHTAKOOTA_CALCULATION_NAME,
    ASHTAKOOTA_EXPECTED_KOOTA_COUNT,
    ASHTAKOOTA_KOOTA_ORDER,
    ASHTAKOOTA_TOTAL_MAXIMUM_SCORE,
    MatchmakingAshtakootaMetadata,
    MatchmakingAshtakootaResult,
    aggregate_ashtakoota_results,
)
from backend.app.matchmaking.bhakoot import (
    BHAKOOT_COMPATIBILITY_DOMAIN,
    BHAKOOT_KOOTA_ID,
    BHAKOOT_KOOTA_MAXIMUM_SCORE,
    MatchmakingBhakootIdentity,
    MatchmakingBhakootKootaResult,
    MatchmakingBhakootMetadata,
)
from backend.app.matchmaking.foundation import (
    MATCHMAKING_SCHEMA_VERSION,
    MATCHMAKING_STATUSES,
    MatchmakingJsonValue,
    MatchmakingMetadata,
    MatchmakingPair,
    MatchmakingPerson,
    MatchmakingResult,
)
from backend.app.matchmaking.gana import (
    GANA_CATEGORIES,
    GANA_COMPATIBILITY_DOMAIN,
    GANA_KOOTA_ID,
    GANA_KOOTA_MAXIMUM_SCORE,
    MatchmakingGanaIdentity,
    MatchmakingGanaKootaResult,
    MatchmakingGanaMetadata,
)
from backend.app.matchmaking.graha_maitri import (
    GRAHA_MAITRI_COMPATIBILITY_DOMAIN,
    GRAHA_MAITRI_KOOTA_ID,
    GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
    GRAHA_MAITRI_LORDS,
    MatchmakingGrahaMaitriIdentity,
    MatchmakingGrahaMaitriKootaResult,
    MatchmakingGrahaMaitriMetadata,
)
from backend.app.matchmaking.manglik import (
    MANGLIK_CALCULATION_NAME,
    MANGLIK_CLASSIFICATIONS,
    MANGLIK_COMPARISON_STATUSES,
    MANGLIK_COMPATIBILITY_CALCULATION_NAME,
    MANGLIK_HOUSES,
    MANGLIK_PAIR_CLASSIFICATIONS,
    MANGLIK_REFERENCE_POINT,
    ManglikClassificationResult,
    ManglikCompatibilityResult,
    MatchmakingManglikCompatibilityMetadata,
    MatchmakingManglikMetadata,
    classify_manglik,
    compare_manglik_classifications,
)
from backend.app.matchmaking.nakshatra import (
    MATCHMAKING_NAKSHATRA_CALCULATION_SCOPE,
    MATCHMAKING_NAKSHATRA_INDEX_BASE,
    MatchmakingNakshatraIdentity,
    MatchmakingNakshatraMetadata,
    MatchmakingNakshatraPairContext,
)
from backend.app.matchmaking.nadi import (
    NADI_CATEGORIES,
    NADI_COMPATIBILITY_DOMAIN,
    NADI_KOOTA_ID,
    NADI_KOOTA_MAXIMUM_SCORE,
    MatchmakingNadiIdentity,
    MatchmakingNadiKootaResult,
    MatchmakingNadiMetadata,
)
from backend.app.matchmaking.tara import (
    TARA_CLASSIFICATIONS,
    TARA_COMPATIBILITY_DOMAIN,
    TARA_KOOTA_ID,
    TARA_KOOTA_MAXIMUM_SCORE,
    MatchmakingTaraDirectionalResult,
    MatchmakingTaraKootaResult,
    MatchmakingTaraMetadata,
)
from backend.app.matchmaking.validation import (
    MatchmakingPairValidationResult,
    MatchmakingPersonValidationResult,
    MatchmakingValidationMetadata,
)
from backend.app.matchmaking.varna import (
    VARNA_KOOTA_ID,
    VARNA_KOOTA_MAXIMUM_SCORE,
    VARNA_RANKS,
    MatchmakingVarnaIdentity,
    MatchmakingVarnaKootaResult,
    MatchmakingVarnaMetadata,
)
from backend.app.matchmaking.vashya import (
    VASHYA_CATEGORIES,
    VASHYA_COMPATIBILITY_DOMAIN,
    VASHYA_KOOTA_ID,
    VASHYA_KOOTA_MAXIMUM_SCORE,
    MatchmakingVashyaIdentity,
    MatchmakingVashyaKootaResult,
    MatchmakingVashyaMetadata,
)
from backend.app.matchmaking.yoni import (
    YONI_CATEGORIES,
    YONI_COMPATIBILITY_DOMAIN,
    YONI_KOOTA_ID,
    YONI_KOOTA_MAXIMUM_SCORE,
    YONI_RELATIONSHIP_BY_SCORE,
    YONI_SEXES,
    MatchmakingYoniIdentity,
    MatchmakingYoniKootaResult,
    MatchmakingYoniMetadata,
)

MATCHMAKING_SERIALIZATION_SCHEMA_VERSION = MATCHMAKING_SCHEMA_VERSION
MATCHMAKING_SERIALIZATION_FAMILIES = (
    "matchmaking_person",
    "matchmaking_pair",
    "matchmaking_result",
    "matchmaking_person_validation",
    "matchmaking_pair_validation",
    "matchmaking_nakshatra_identity",
    "matchmaking_nakshatra_pair_context",
    VARNA_KOOTA_ID,
    VASHYA_KOOTA_ID,
    TARA_KOOTA_ID,
    YONI_KOOTA_ID,
    GRAHA_MAITRI_KOOTA_ID,
    GANA_KOOTA_ID,
    BHAKOOT_KOOTA_ID,
    NADI_KOOTA_ID,
    ASHTAKOOTA_CALCULATION_NAME,
    MANGLIK_CALCULATION_NAME,
    MANGLIK_COMPATIBILITY_CALCULATION_NAME,
    "matchmaking_compatibility_report",
)

_ISSUE_FIELDS = ("field", "code", "message_key", "severity", "value", "metadata")
_VALIDATION_RESULT_FIELDS = tuple(MatchmakingPersonValidationResult.__annotations__)
_FOUNDATION_METADATA_FIELDS = tuple(MatchmakingMetadata.__annotations__)
_VALIDATION_METADATA_FIELDS = tuple(MatchmakingValidationMetadata.__annotations__)
_NAKSHATRA_METADATA_FIELDS = tuple(MatchmakingNakshatraMetadata.__annotations__)
_MANGLIK_CLASSIFICATION_FIELDS = tuple(ManglikClassificationResult.__annotations__)
_MANGLIK_COMPATIBILITY_FIELDS = tuple(ManglikCompatibilityResult.__annotations__)


class _KootaContract(TypedDict):
    result_fields: tuple[str, ...]
    metadata_fields: tuple[str, ...]
    maximum_score: float
    compatibility_domain: str | None
    calculation: str
    metadata: dict[str, MatchmakingJsonValue]
    direction_fields: tuple[str, str]


_KOOTA_CONTRACTS: dict[str, _KootaContract] = {
    VARNA_KOOTA_ID: {
        "result_fields": tuple(MatchmakingVarnaKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingVarnaMetadata.__annotations__),
        "maximum_score": VARNA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": None,
        "calculation": "varna_koota",
        "metadata": {
            "component": "matchmaking_varna_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "varna_koota",
            "maximum_score": VARNA_KOOTA_MAXIMUM_SCORE,
            "directional": True,
        },
        "direction_fields": ("subject_role", "comparison_role"),
    },
    VASHYA_KOOTA_ID: {
        "result_fields": tuple(MatchmakingVashyaKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingVashyaMetadata.__annotations__),
        "maximum_score": VASHYA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": VASHYA_COMPATIBILITY_DOMAIN,
        "calculation": "vashya_koota",
        "metadata": {
            "component": "matchmaking_vashya_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "vashya_koota",
            "maximum_score": VASHYA_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": VASHYA_COMPATIBILITY_DOMAIN,
            "directional": True,
        },
        "direction_fields": ("row_role", "column_role"),
    },
    TARA_KOOTA_ID: {
        "result_fields": tuple(MatchmakingTaraKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingTaraMetadata.__annotations__),
        "maximum_score": TARA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": TARA_COMPATIBILITY_DOMAIN,
        "calculation": "tara_koota",
        "metadata": {
            "component": "matchmaking_tara_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "tara_koota",
            "maximum_score": TARA_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": TARA_COMPATIBILITY_DOMAIN,
            "directional": True,
            "nakshatra_count": 27,
            "index_base": 0,
        },
        "direction_fields": ("bride_role", "groom_role"),
    },
    YONI_KOOTA_ID: {
        "result_fields": tuple(MatchmakingYoniKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingYoniMetadata.__annotations__),
        "maximum_score": YONI_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": YONI_COMPATIBILITY_DOMAIN,
        "calculation": "yoni_koota",
        "metadata": {
            "component": "matchmaking_yoni_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "yoni_koota",
            "maximum_score": YONI_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": YONI_COMPATIBILITY_DOMAIN,
            "directional": False,
            "symmetric": True,
            "nakshatra_count": 27,
            "index_base": 0,
        },
        "direction_fields": ("bride_role", "groom_role"),
    },
    GRAHA_MAITRI_KOOTA_ID: {
        "result_fields": tuple(MatchmakingGrahaMaitriKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingGrahaMaitriMetadata.__annotations__),
        "maximum_score": GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": GRAHA_MAITRI_COMPATIBILITY_DOMAIN,
        "calculation": "graha_maitri_koota",
        "metadata": {
            "component": "matchmaking_graha_maitri_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "graha_maitri_koota",
            "maximum_score": GRAHA_MAITRI_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": GRAHA_MAITRI_COMPATIBILITY_DOMAIN,
            "directional": False,
            "symmetric": True,
            "relationship_type": "natural_permanent",
            "rashi_count": 12,
            "index_base": 1,
        },
        "direction_fields": ("row_role", "column_role"),
    },
    GANA_KOOTA_ID: {
        "result_fields": tuple(MatchmakingGanaKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingGanaMetadata.__annotations__),
        "maximum_score": GANA_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": GANA_COMPATIBILITY_DOMAIN,
        "calculation": "gana_koota",
        "metadata": {
            "component": "matchmaking_gana_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "gana_koota",
            "maximum_score": GANA_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": GANA_COMPATIBILITY_DOMAIN,
            "directional": True,
            "symmetric": False,
            "nakshatra_count": 27,
            "index_base": 0,
        },
        "direction_fields": ("bride_role", "groom_role"),
    },
    BHAKOOT_KOOTA_ID: {
        "result_fields": tuple(MatchmakingBhakootKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingBhakootMetadata.__annotations__),
        "maximum_score": BHAKOOT_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": BHAKOOT_COMPATIBILITY_DOMAIN,
        "calculation": "bhakoot_koota",
        "metadata": {
            "component": "matchmaking_bhakoot_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "bhakoot_koota",
            "maximum_score": BHAKOOT_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": BHAKOOT_COMPATIBILITY_DOMAIN,
            "directional": False,
            "symmetric": True,
            "relationship_type": "inclusive_circular_rashi_distance",
            "rashi_count": 12,
            "index_base": 1,
        },
        "direction_fields": ("row_role", "column_role"),
    },
    NADI_KOOTA_ID: {
        "result_fields": tuple(MatchmakingNadiKootaResult.__annotations__),
        "metadata_fields": tuple(MatchmakingNadiMetadata.__annotations__),
        "maximum_score": NADI_KOOTA_MAXIMUM_SCORE,
        "compatibility_domain": NADI_COMPATIBILITY_DOMAIN,
        "calculation": "nadi_koota",
        "metadata": {
            "component": "matchmaking_nadi_koota",
            "schema_version": MATCHMAKING_SCHEMA_VERSION,
            "deterministic": True,
            "calculation": "nadi_koota",
            "maximum_score": NADI_KOOTA_MAXIMUM_SCORE,
            "compatibility_domain": NADI_COMPATIBILITY_DOMAIN,
            "directional": False,
            "symmetric": True,
            "nakshatra_count": 27,
            "index_base": 0,
        },
        "direction_fields": ("bride_role", "groom_role"),
    },
}


def serialize_matchmaking_person(*, result: object) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical matchmaking person snapshot."""

    copied = _prepare(result, tuple(MatchmakingPerson.__annotations__), "person")
    _validate_person(copied, "person")
    return copied


def serialize_matchmaking_pair(*, result: object) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical ordered matchmaking pair."""

    copied = _prepare(result, tuple(MatchmakingPair.__annotations__), "pair")
    _validate_person(_mapping(copied["person_a"], "pair.person_a"), "pair.person_a")
    _validate_person(_mapping(copied["person_b"], "pair.person_b"), "pair.person_b")
    _validate_foundation_metadata(copied["metadata"], "matchmaking_pair", "pair")
    return copied


def serialize_matchmaking_result(*, result: object) -> dict[str, MatchmakingJsonValue]:
    """Serialize one generic matchmaking result envelope."""

    copied = _prepare(result, tuple(MatchmakingResult.__annotations__), "result")
    _string(copied, "matchmaking_id", "result")
    status = _string(copied, "status", "result")
    if status not in MATCHMAKING_STATUSES:
        raise ValueError("result.status is invalid")
    score = _optional_float(copied, "score", "result")
    maximum = _optional_float(copied, "maximum_score", "result")
    percentage = _optional_float(copied, "percentage", "result")
    if score is not None and score < 0.0:
        raise ValueError("result.score must not be negative")
    if maximum is not None and maximum < 0.0:
        raise ValueError("result.maximum_score must not be negative")
    if score is not None and maximum is not None and score > maximum:
        raise ValueError("result.score exceeds maximum_score")
    if percentage is not None and not 0.0 <= percentage <= 100.0:
        raise ValueError("result.percentage must be between 0.0 and 100.0")
    _list(copied["factors"], "result.factors")
    _string_list(copied["warnings"], "result.warnings")
    _string_list(copied["references"], "result.references")
    _list(copied["notes"], "result.notes")
    _validate_foundation_metadata(copied["metadata"], "matchmaking_result", "result")
    metadata = _mapping(copied["metadata"], "result.metadata")
    if metadata["calculation_complete"] is not (status == "complete"):
        raise ValueError("result.metadata.calculation_complete is inconsistent")
    return copied


def serialize_matchmaking_person_validation(
    *, result: object
) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical person-validation result."""

    copied = _prepare(result, _VALIDATION_RESULT_FIELDS, "person_validation")
    _validate_validation_result(copied, "person_validation", pair=False)
    return copied


def serialize_matchmaking_pair_validation(
    *, result: object
) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical pair-validation result."""

    copied = _prepare(
        result,
        tuple(MatchmakingPairValidationResult.__annotations__),
        "pair_validation",
    )
    _validate_validation_result(copied, "pair_validation", pair=True)
    return copied


def serialize_matchmaking_nakshatra_identity(
    *, result: object
) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical Nakshatra identity."""

    copied = _prepare(
        result,
        tuple(MatchmakingNakshatraIdentity.__annotations__),
        "nakshatra_identity",
    )
    _validate_nakshatra_identity(copied, "nakshatra_identity")
    return copied


def serialize_matchmaking_nakshatra_pair_context(
    *, result: object
) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical ordered Nakshatra pair context."""

    copied = _prepare(
        result,
        tuple(MatchmakingNakshatraPairContext.__annotations__),
        "nakshatra_pair_context",
    )
    _boolean(copied, "is_valid", "nakshatra_pair_context")
    for role in ("person_a", "person_b"):
        identity = _mapping(copied[role], f"nakshatra_pair_context.{role}")
        _validate_nakshatra_identity(identity, f"nakshatra_pair_context.{role}")
    for field in ("forward_distance", "reverse_distance"):
        _optional_integer(copied, field, "nakshatra_pair_context", 0, 26)
    for field in ("same_nakshatra", "same_pada"):
        _optional_boolean(copied, field, "nakshatra_pair_context")
    errors = _issues(copied["errors"], "nakshatra_pair_context.errors")
    _issues(copied["warnings"], "nakshatra_pair_context.warnings")
    _validate_nakshatra_metadata(
        copied["metadata"],
        "matchmaking_nakshatra_pair_context",
        "nakshatra_pair_context",
    )
    if copied["is_valid"] is not (not errors):
        raise ValueError("nakshatra_pair_context.is_valid is inconsistent")
    return copied


def serialize_koota_result(*, result: object) -> dict[str, MatchmakingJsonValue]:
    """Serialize one of the eight canonical individual Koota results."""

    if not isinstance(result, Mapping):
        raise TypeError("koota_result must be a mapping")
    koota = result.get("koota")
    if not isinstance(koota, str):
        raise TypeError("koota_result.koota must be a string")
    if koota not in _KOOTA_CONTRACTS:
        raise ValueError(f"unsupported Koota identifier: {koota!r}")
    contract = _KOOTA_CONTRACTS[koota]
    copied = _prepare(result, contract["result_fields"], f"koota.{koota}")
    _validate_koota(copied, koota, contract)
    return copied


def serialize_ashtakoota_result(*, result: object) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical complete or invalid Ashtakoota aggregate."""

    copied = _prepare(
        result,
        tuple(MatchmakingAshtakootaResult.__annotations__),
        "ashtakoota",
    )
    if copied["calculation"] != ASHTAKOOTA_CALCULATION_NAME:
        raise ValueError("ashtakoota.calculation is invalid")
    status = _string(copied, "status", "ashtakoota")
    if status not in ("complete", "invalid"):
        raise ValueError("ashtakoota.status is invalid")
    _optional_float(copied, "bride_moon_longitude", "ashtakoota")
    _optional_float(copied, "groom_moon_longitude", "ashtakoota")
    koota_results = _list(copied["koota_results"], "ashtakoota.koota_results")
    serialized_kootas = [serialize_koota_result(result=item) for item in koota_results]
    copied["koota_results"] = serialized_kootas
    score_by = _mapping(copied["score_by_koota"], "ashtakoota.score_by_koota")
    maximum_by = _mapping(
        copied["maximum_score_by_koota"],
        "ashtakoota.maximum_score_by_koota",
    )
    _optional_float(copied, "total_score", "ashtakoota")
    total_maximum = _float(copied, "total_maximum_score", "ashtakoota")
    if total_maximum != ASHTAKOOTA_TOTAL_MAXIMUM_SCORE:
        raise ValueError("ashtakoota.total_maximum_score must equal 36.0")
    errors = _issues(copied["errors"], "ashtakoota.errors")
    _issues(copied["warnings"], "ashtakoota.warnings")
    _string_list(copied["references"], "ashtakoota.references")
    metadata = _validate_ashtakoota_metadata(copied["metadata"])

    if status == "complete":
        if errors:
            raise ValueError("complete ashtakoota.errors must be empty")
        if [item["koota"] for item in serialized_kootas] != list(
            ASHTAKOOTA_KOOTA_ORDER
        ):
            raise ValueError("ashtakoota Koota order is invalid")
        regenerated = aggregate_ashtakoota_results(
            serialized_kootas,
            bride_moon_longitude=copied["bride_moon_longitude"],
            groom_moon_longitude=copied["groom_moon_longitude"],
        )
        regenerated["metadata"]["execution_mode"] = cast(
            str, metadata["execution_mode"]
        )
        if copied != regenerated:
            raise ValueError("ashtakoota does not match authoritative aggregation")
        return cast(dict[str, MatchmakingJsonValue], regenerated)

    if not errors:
        raise ValueError("invalid ashtakoota must contain errors")
    if len(serialized_kootas) not in (0, ASHTAKOOTA_EXPECTED_KOOTA_COUNT):
        raise ValueError("invalid ashtakoota must contain zero or eight Kootas")
    if copied["total_score"] is not None:
        raise ValueError("invalid ashtakoota.total_score must be None")
    _validate_koota_key_mapping(score_by, allow_empty=not serialized_kootas)
    _validate_maximum_mapping(maximum_by)
    return copied


def serialize_manglik_classification_result(
    *, result: object
) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical Manglik classification result."""

    copied = _prepare(
        result,
        _MANGLIK_CLASSIFICATION_FIELDS,
        "manglik_classification",
    )
    _validate_manglik_classification(copied, "manglik_classification")
    if copied["status"] == "complete":
        expected = classify_manglik(
            lagna_sidereal_longitude=copied["lagna_sidereal_longitude"],
            mars_sidereal_longitude=copied["mars_sidereal_longitude"],
        )
        if copied != expected:
            raise ValueError("Manglik classification is inconsistent")
    return copied


def serialize_manglik_compatibility_result(
    *, result: object
) -> dict[str, MatchmakingJsonValue]:
    """Serialize one canonical Manglik bride/groom comparison."""

    copied = _prepare(
        result,
        _MANGLIK_COMPATIBILITY_FIELDS,
        "manglik_compatibility",
    )
    if copied["calculation"] != MANGLIK_COMPATIBILITY_CALCULATION_NAME:
        raise ValueError("manglik_compatibility.calculation is invalid")
    status = _string(copied, "status", "manglik_compatibility")
    if status not in ("complete", "invalid"):
        raise ValueError("manglik_compatibility.status is invalid")
    bride = _mapping(copied["bride_manglik"], "manglik_compatibility.bride")
    groom = _mapping(copied["groom_manglik"], "manglik_compatibility.groom")
    _validate_manglik_classification(bride, "manglik_compatibility.bride")
    _validate_manglik_classification(groom, "manglik_compatibility.groom")
    for field in (
        "bride_classification",
        "groom_classification",
        "bride_reference_point",
        "groom_reference_point",
        "pair_classification",
        "comparison_status",
    ):
        _string(copied, field, "manglik_compatibility")
    _optional_integer(copied, "bride_mars_house", "manglik_compatibility", 1, 12)
    _optional_integer(copied, "groom_mars_house", "manglik_compatibility", 1, 12)
    _integer_list(
        copied["applicable_manglik_houses"],
        "manglik_compatibility.applicable_manglik_houses",
    )
    _string_list(copied["reasons"], "manglik_compatibility.reasons")
    errors = _issues(copied["errors"], "manglik_compatibility.errors")
    _issues(copied["warnings"], "manglik_compatibility.warnings")
    _string_list(copied["references"], "manglik_compatibility.references")
    _validate_manglik_metadata(copied["metadata"], comparison=True)

    if status == "complete":
        if errors:
            raise ValueError("complete Manglik comparison must have no errors")
        regenerated = compare_manglik_classifications(bride=bride, groom=groom)
        if copied != regenerated:
            raise ValueError("Manglik comparison is inconsistent")
    else:
        if not errors:
            raise ValueError("invalid Manglik comparison must contain errors")
        if any(
            copied[field] not in ("", None, [])
            for field in (
                "bride_classification",
                "groom_classification",
                "bride_reference_point",
                "groom_reference_point",
                "bride_mars_house",
                "groom_mars_house",
                "pair_classification",
                "comparison_status",
                "reasons",
            )
        ):
            raise ValueError("invalid Manglik comparison placeholders are malformed")
    return copied


def _prepare(
    result: object,
    fields: tuple[str, ...],
    path: str,
) -> dict[str, MatchmakingJsonValue]:
    if not isinstance(result, Mapping):
        raise TypeError(f"{path} must be a mapping")
    copied = _copy_json_value(result, path, {}, set())
    if not isinstance(copied, dict):
        raise TypeError(f"{path} must be a mapping")
    _exact_fields(copied, fields, path)
    return copied


def _copy_json_value(
    value: object,
    path: str,
    seen: dict[int, str],
    active: set[int],
) -> MatchmakingJsonValue:
    if isinstance(value, Enum) or is_dataclass(value) and not isinstance(value, type):
        raise TypeError(f"{path} contains an unsupported object")
    if value is None or type(value) in (str, bool, int):
        return value  # type: ignore[return-value]
    if isinstance(value, Real) and not isinstance(value, bool):
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError(f"{path} must not contain NaN or infinity")
        return 0.0 if numeric == 0.0 else numeric
    if isinstance(value, (datetime, date, time)):
        raise TypeError(f"{path} contains an unsupported date/time object")
    if isinstance(value, Mapping) or isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise ValueError(f"{path} contains a cycle through {seen[identity]}")
        if identity in seen:
            raise ValueError(
                f"{path} shares a mutable collection with {seen[identity]}"
            )
        seen[identity] = path
        active.add(identity)
        try:
            if isinstance(value, Mapping):
                copied_mapping: dict[str, MatchmakingJsonValue] = {}
                for key, item in value.items():
                    if not isinstance(key, str):
                        raise ValueError(f"{path} contains a non-string key")
                    copied_mapping[key] = _copy_json_value(
                        item, f"{path}.{key}", seen, active
                    )
                return copied_mapping
            return [
                _copy_json_value(item, f"{path}[{index}]", seen, active)
                for index, item in enumerate(value)
            ]
        finally:
            active.remove(identity)
    raise TypeError(f"{path} contains a non-JSON-safe value")


def _validate_person(value: Mapping[str, MatchmakingJsonValue], path: str) -> None:
    _exact_fields(value, tuple(MatchmakingPerson.__annotations__), path)
    for field in (
        "person_id",
        "name",
        "birth_date",
        "birth_time",
        "timezone",
        "rashi",
        "nakshatra",
        "lagna",
    ):
        _string(value, field, path)
    _optional_float(value, "latitude", path)
    _optional_float(value, "longitude", path)
    _optional_integer(value, "nakshatra_pada", path, 1, 4)
    _validate_foundation_metadata(value["metadata"], "matchmaking_person", path)


def _validate_foundation_metadata(value: object, component: str, path: str) -> None:
    metadata = _mapping(value, f"{path}.metadata")
    _exact_fields(metadata, _FOUNDATION_METADATA_FIELDS, f"{path}.metadata")
    if metadata["component"] != component:
        raise ValueError(f"{path}.metadata.component is invalid")
    _validate_schema_and_determinism(metadata, f"{path}.metadata")
    _boolean(metadata, "calculation_complete", f"{path}.metadata")
    _string_list(metadata["source_components"], f"{path}.metadata.source_components")


def _validate_validation_result(
    value: dict[str, MatchmakingJsonValue], path: str, *, pair: bool
) -> None:
    _boolean(value, "is_valid", path)
    errors = _issues(value["errors"], f"{path}.errors")
    warnings = _issues(value["warnings"], f"{path}.warnings")
    normalized = _mapping(value["normalized_value"], f"{path}.normalized_value")
    if pair:
        _exact_fields(
            normalized,
            tuple(MatchmakingPair.__annotations__),
            f"{path}.normalized_value",
        )
        _validate_person(
            _mapping(normalized["person_a"], f"{path}.normalized_value.person_a"),
            f"{path}.normalized_value.person_a",
        )
        _validate_person(
            _mapping(normalized["person_b"], f"{path}.normalized_value.person_b"),
            f"{path}.normalized_value.person_b",
        )
        _validate_foundation_metadata(
            normalized["metadata"],
            "matchmaking_pair",
            f"{path}.normalized_value",
        )
        component = "matchmaking_pair_validation"
    else:
        _validate_person(normalized, f"{path}.normalized_value")
        component = "matchmaking_person_validation"
    metadata = _mapping(value["metadata"], f"{path}.metadata")
    _exact_fields(metadata, _VALIDATION_METADATA_FIELDS, f"{path}.metadata")
    if metadata["component"] != component:
        raise ValueError(f"{path}.metadata.component is invalid")
    _validate_schema_and_determinism(metadata, f"{path}.metadata")
    count = _integer(metadata, "issue_count", f"{path}.metadata", 0)
    if count != len(errors) + len(warnings):
        raise ValueError(f"{path}.metadata.issue_count is inconsistent")
    if value["is_valid"] is not (not errors):
        raise ValueError(f"{path}.is_valid is inconsistent")


def _validate_nakshatra_identity(
    value: Mapping[str, MatchmakingJsonValue], path: str
) -> None:
    _exact_fields(value, tuple(MatchmakingNakshatraIdentity.__annotations__), path)
    _boolean(value, "is_valid", path)
    _string(value, "name", path)
    _optional_integer(value, "index", path, 0, 26)
    _optional_integer(value, "pada", path, 1, 4)
    _string(value, "source_person_id", path)
    errors = _issues(value["errors"], f"{path}.errors")
    _issues(value["warnings"], f"{path}.warnings")
    _validate_nakshatra_metadata(
        value["metadata"], "matchmaking_nakshatra_identity", path
    )
    if value["is_valid"] is not (not errors):
        raise ValueError(f"{path}.is_valid is inconsistent")
    if value["is_valid"] and (value["index"] is None or not value["name"]):
        raise ValueError(f"{path} complete identity is missing Nakshatra data")


def _validate_nakshatra_metadata(value: object, component: str, path: str) -> None:
    metadata = _mapping(value, f"{path}.metadata")
    _exact_fields(metadata, _NAKSHATRA_METADATA_FIELDS, f"{path}.metadata")
    expected = {
        "component": component,
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "nakshatra_count": 27,
        "index_base": MATCHMAKING_NAKSHATRA_INDEX_BASE,
        "calculation_scope": MATCHMAKING_NAKSHATRA_CALCULATION_SCOPE,
    }
    if metadata != expected:
        raise ValueError(f"{path}.metadata is invalid")


def _validate_koota(
    value: dict[str, MatchmakingJsonValue],
    koota: str,
    contract: _KootaContract,
) -> None:
    path = f"koota.{koota}"
    if value["koota"] != koota:
        raise ValueError(f"{path}.koota is invalid")
    domain = contract["compatibility_domain"]
    if domain is not None and value.get("compatibility_domain") != domain:
        raise ValueError(f"{path}.compatibility_domain is invalid")
    status = _string(value, "status", path)
    if status not in ("complete", "invalid"):
        raise ValueError(f"{path}.status is invalid")
    maximum = _float(value, "maximum_score", path)
    if maximum != contract["maximum_score"]:
        raise ValueError(f"{path}.maximum_score is invalid")
    score = _optional_float(value, "score", path)
    errors = _issues(value["errors"], f"{path}.errors")
    _issues(value["warnings"], f"{path}.warnings")
    _list(value["factors"], f"{path}.factors")
    _string_list(value["references"], f"{path}.references")
    direction = _mapping(value["direction"], f"{path}.direction")
    _exact_fields(direction, contract["direction_fields"], f"{path}.direction")
    for field in contract["direction_fields"]:
        if not isinstance(direction[field], str) or not direction[field]:
            raise ValueError(f"{path}.direction.{field} is invalid")
    if contract["direction_fields"] in (
        ("subject_role", "comparison_role"),
        ("bride_role", "groom_role"),
    ):
        roles = tuple(direction[field] for field in contract["direction_fields"])
        if set(roles) != {"person_a", "person_b"}:
            raise ValueError(f"{path}.direction roles are invalid")
    elif tuple(direction.values()) != ("bride", "groom"):
        raise ValueError(f"{path}.direction roles are invalid")
    metadata = _mapping(value["metadata"], f"{path}.metadata")
    _exact_fields(metadata, contract["metadata_fields"], f"{path}.metadata")
    if metadata != contract["metadata"]:
        raise ValueError(f"{path}.metadata is invalid")
    _validate_koota_nested(value, koota, status == "complete", path)
    if status == "complete":
        if errors or score is None:
            raise ValueError(f"complete {path} must have a score and no errors")
        if not 0.0 <= score <= maximum:
            raise ValueError(f"{path}.score is outside the canonical range")
    elif score is not None or not errors:
        raise ValueError(f"invalid {path} must have no score and contain errors")


def _validate_koota_nested(
    value: Mapping[str, MatchmakingJsonValue],
    koota: str,
    complete: bool,
    path: str,
) -> None:
    if koota == VARNA_KOOTA_ID:
        for field in ("person_a_varna", "person_b_varna"):
            identity = _validate_identity(
                value[field],
                MatchmakingVarnaIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
            if complete:
                category = _category(identity, "varna", VARNA_RANKS, f"{path}.{field}")
                if identity["varna_rank"] != VARNA_RANKS[category]:
                    raise ValueError(f"{path}.{field}.varna_rank is inconsistent")
        return
    if koota == VASHYA_KOOTA_ID:
        for field in ("bride_vashya", "groom_vashya"):
            identity = _validate_identity(
                value[field],
                MatchmakingVashyaIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
            if complete:
                _category(identity, "vashya", VASHYA_CATEGORIES, f"{path}.{field}")
        return

    if koota in (TARA_KOOTA_ID, YONI_KOOTA_ID, GANA_KOOTA_ID, NADI_KOOTA_ID):
        for field in ("person_a_nakshatra", "person_b_nakshatra"):
            identity = _mapping(value[field], f"{path}.{field}")
            _validate_nakshatra_identity(identity, f"{path}.{field}")
            if complete and not identity["is_valid"]:
                raise ValueError(
                    f"{path}.{field}.is_valid must be true for a complete Koota"
                )
    if koota == TARA_KOOTA_ID:
        identifiers = {
            cast(str, item["identifier"]) for item in TARA_CLASSIFICATIONS.values()
        }
        for field in ("bride_to_groom", "groom_to_bride"):
            directional = _mapping(value[field], f"{path}.{field}")
            _exact_fields(
                directional,
                tuple(MatchmakingTaraDirectionalResult.__annotations__),
                f"{path}.{field}",
            )
            directional_path = f"{path}.{field}"
            for role_field in ("source_role", "destination_role"):
                _string(directional, role_field, directional_path)
            for name_field in (
                "source_nakshatra",
                "destination_nakshatra",
                "tara",
                "tara_name",
            ):
                _string(directional, name_field, directional_path)
            for index_field in (
                "source_index",
                "destination_index",
                "circular_distance",
            ):
                _optional_integer(directional, index_field, directional_path, 0, 26)
            _optional_integer(directional, "inclusive_count", directional_path, 1, 27)
            _optional_integer(directional, "tara_number", directional_path, 1, 9)
            _optional_boolean(directional, "favorable", directional_path)
            directional_score = _optional_float(directional, "score", directional_path)
            if complete:
                if directional["tara"] not in identifiers:
                    raise ValueError(f"{path}.{field}.tara is invalid")
                if directional_score not in (0.0, 1.5):
                    raise ValueError(f"{path}.{field}.score is invalid")
        _optional_boolean(value, "same_nakshatra", path)
        _optional_boolean(value, "same_pada", path)
        return
    if koota == YONI_KOOTA_ID:
        for field in ("bride_yoni", "groom_yoni"):
            identity = _validate_identity(
                value[field],
                MatchmakingYoniIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
            if complete:
                _category(identity, "yoni", YONI_CATEGORIES, f"{path}.{field}")
                _category(identity, "yoni_sex", YONI_SEXES, f"{path}.{field}")
        if complete and value["relationship"] not in set(
            YONI_RELATIONSHIP_BY_SCORE.values()
        ):
            raise ValueError(f"{path}.relationship is invalid")
        _string(value, "relationship", path)
        for field in ("same_nakshatra", "same_pada", "same_yoni"):
            _optional_boolean(value, field, path)
        if complete:
            same_yoni = (
                _mapping(value["bride_yoni"], f"{path}.bride_yoni")["yoni"]
                == _mapping(value["groom_yoni"], f"{path}.groom_yoni")["yoni"]
            )
            if value["same_yoni"] is not same_yoni:
                raise ValueError(f"{path}.same_yoni is inconsistent")
            if (
                value["relationship"]
                != YONI_RELATIONSHIP_BY_SCORE[cast(float, value["score"])]
            ):
                raise ValueError(f"{path}.relationship is inconsistent with score")
        return
    if koota == GRAHA_MAITRI_KOOTA_ID:
        for field in ("bride_moon_rashi", "groom_moon_rashi"):
            identity = _validate_identity(
                value[field],
                MatchmakingGrahaMaitriIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
            if complete:
                _category(identity, "lord", GRAHA_MAITRI_LORDS, f"{path}.{field}")
        if complete:
            for field in (
                "bride_to_groom_relationship",
                "groom_to_bride_relationship",
            ):
                if value[field] not in ("friend", "neutral", "enemy", "same"):
                    raise ValueError(f"{path}.{field} is invalid")
            if value["combined_relationship"] not in (
                "same_lord",
                "mutual_friend",
                "friend_neutral",
                "mutual_neutral",
                "friend_enemy",
                "neutral_enemy",
                "mutual_enemy",
            ):
                raise ValueError(f"{path}.combined_relationship is invalid")
            bride_lord = _mapping(
                value["bride_moon_rashi"], f"{path}.bride_moon_rashi"
            )["lord"]
            groom_lord = _mapping(
                value["groom_moon_rashi"], f"{path}.groom_moon_rashi"
            )["lord"]
            if value["same_lord"] is not (bride_lord == groom_lord):
                raise ValueError(f"{path}.same_lord is inconsistent")
        _string(value, "bride_to_groom_relationship", path)
        _string(value, "groom_to_bride_relationship", path)
        _string(value, "combined_relationship", path)
        _optional_boolean(value, "same_lord", path)
        return
    if koota == GANA_KOOTA_ID:
        for field in ("bride_gana", "groom_gana"):
            identity = _validate_identity(
                value[field],
                MatchmakingGanaIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
            if complete:
                _category(identity, "gana", GANA_CATEGORIES, f"{path}.{field}")
        if complete and value["relationship"] not in ("same_gana", "mixed_gana"):
            raise ValueError(f"{path}.relationship is invalid")
        _string(value, "relationship", path)
        for field in ("same_nakshatra", "same_pada", "same_gana"):
            _optional_boolean(value, field, path)
        if complete:
            same_gana = (
                _mapping(value["bride_gana"], f"{path}.bride_gana")["gana"]
                == _mapping(value["groom_gana"], f"{path}.groom_gana")["gana"]
            )
            expected_relationship = "same_gana" if same_gana else "mixed_gana"
            if value["same_gana"] is not same_gana:
                raise ValueError(f"{path}.same_gana is inconsistent")
            if value["relationship"] != expected_relationship:
                raise ValueError(f"{path}.relationship is inconsistent")
        return
    if koota == BHAKOOT_KOOTA_ID:
        for field in ("bride_moon_rashi", "groom_moon_rashi"):
            _validate_identity(
                value[field],
                MatchmakingBhakootIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
        if complete and value["relationship"] not in ("compatible", "dosha"):
            raise ValueError(f"{path}.relationship is invalid")
        for field in ("bride_to_groom_distance", "groom_to_bride_distance"):
            _optional_integer(value, field, path, 1, 12)
        for field in ("pair_identifier", "position_pair", "relationship"):
            _string(value, field, path)
        _optional_boolean(value, "same_rashi", path)
        _optional_boolean(value, "bhakoot_dosha", path)
        if complete:
            relationship_is_dosha = value["relationship"] == "dosha"
            if value["bhakoot_dosha"] is not relationship_is_dosha:
                raise ValueError(f"{path}.bhakoot_dosha is inconsistent")
        return
    if koota == NADI_KOOTA_ID:
        for field in ("bride_nadi", "groom_nadi"):
            identity = _validate_identity(
                value[field],
                MatchmakingNadiIdentity,
                koota,
                f"{path}.{field}",
                required_valid=complete,
            )
            if complete:
                _category(identity, "nadi", NADI_CATEGORIES, f"{path}.{field}")
        if complete and value["relationship"] not in (
            "same_nadi",
            "different_nadi",
        ):
            raise ValueError(f"{path}.relationship is invalid")
        _string(value, "relationship", path)
        for field in (
            "same_nakshatra",
            "same_pada",
            "same_nadi",
            "nadi_dosha",
        ):
            _optional_boolean(value, field, path)
        if complete:
            same_nadi = (
                _mapping(value["bride_nadi"], f"{path}.bride_nadi")["nadi"]
                == _mapping(value["groom_nadi"], f"{path}.groom_nadi")["nadi"]
            )
            expected_relationship = "same_nadi" if same_nadi else "different_nadi"
            if value["same_nadi"] is not same_nadi:
                raise ValueError(f"{path}.same_nadi is inconsistent")
            if value["nadi_dosha"] is not same_nadi:
                raise ValueError(f"{path}.nadi_dosha is inconsistent")
            if value["relationship"] != expected_relationship:
                raise ValueError(f"{path}.relationship is inconsistent")


def _validate_identity(
    value: object,
    identity_type: type,
    koota: str,
    path: str,
    *,
    required_valid: bool,
) -> dict[str, MatchmakingJsonValue]:
    identity = _mapping(value, path)
    _exact_fields(identity, tuple(identity_type.__annotations__), path)
    _boolean(identity, "is_valid", path)
    for field in (
        "rashi",
        "rashi_english",
        "rashi_hindi",
        "rashi_sanskrit",
        "nakshatra",
        "source_person_id",
        "varna",
        "vashya",
        "yoni",
        "traditional_name",
        "yoni_sex",
        "lord",
        "gana",
        "nadi",
    ):
        if field in identity:
            _string(identity, field, path)
    if "rashi_index" in identity:
        _optional_integer(identity, "rashi_index", path, 1, 12)
    if "nakshatra_index" in identity:
        _optional_integer(identity, "nakshatra_index", path, 0, 26)
    if "nakshatra_pada" in identity:
        _optional_integer(identity, "nakshatra_pada", path, 1, 4)
    if "varna_rank" in identity:
        _optional_integer(identity, "varna_rank", path, 1, 4)
    if "sidereal_moon_longitude" in identity:
        longitude = _optional_float(identity, "sidereal_moon_longitude", path)
        if longitude is not None and not 0.0 <= longitude < 360.0:
            raise ValueError(f"{path}.sidereal_moon_longitude is out of range")
    if "degree_in_rashi" in identity:
        degree = _optional_float(identity, "degree_in_rashi", path)
        if degree is not None and not 0.0 <= degree < 30.0:
            raise ValueError(f"{path}.degree_in_rashi is out of range")
    errors = _issues(identity["errors"], f"{path}.errors")
    _issues(identity["warnings"], f"{path}.warnings")
    metadata = _mapping(identity["metadata"], f"{path}.metadata")
    contract = _KOOTA_CONTRACTS[koota]
    _exact_fields(metadata, contract["metadata_fields"], f"{path}.metadata")
    expected = dict(contract["metadata"])
    expected["component"] = f"matchmaking_{koota}_identity"
    if metadata != expected:
        raise ValueError(f"{path}.metadata is invalid")
    if identity["is_valid"] and errors:
        raise ValueError(f"{path}.is_valid is inconsistent")
    if required_valid and not identity["is_valid"]:
        raise ValueError(f"{path}.is_valid must be true for a complete Koota")
    return identity


def _validate_manglik_classification(
    value: dict[str, MatchmakingJsonValue], path: str
) -> None:
    _exact_fields(value, _MANGLIK_CLASSIFICATION_FIELDS, path)
    if value["calculation"] != MANGLIK_CALCULATION_NAME:
        raise ValueError(f"{path}.calculation is invalid")
    status = _string(value, "status", path)
    if status not in ("complete", "invalid"):
        raise ValueError(f"{path}.status is invalid")
    _string(value, "classification", path)
    _string(value, "reference_point", path)
    _optional_float(value, "lagna_sidereal_longitude", path)
    _optional_float(value, "mars_sidereal_longitude", path)
    _optional_integer(value, "lagna_rashi_index", path, 1, 12)
    _optional_integer(value, "mars_rashi_index", path, 1, 12)
    _optional_integer(value, "mars_house", path, 1, 12)
    houses = _integer_list(
        value["applicable_manglik_houses"], f"{path}.applicable_manglik_houses"
    )
    if houses != list(MANGLIK_HOUSES):
        raise ValueError(f"{path}.applicable_manglik_houses is invalid")
    _string(value, "reason", path)
    errors = _issues(value["errors"], f"{path}.errors")
    _issues(value["warnings"], f"{path}.warnings")
    _string_list(value["references"], f"{path}.references")
    _validate_manglik_metadata(value["metadata"], comparison=False)
    if status == "complete":
        if errors or value["classification"] not in MANGLIK_CLASSIFICATIONS:
            raise ValueError(f"complete {path} is malformed")
        if value["reference_point"] != MANGLIK_REFERENCE_POINT:
            raise ValueError(f"{path}.reference_point is invalid")
    elif not errors or value["classification"] or value["reason"]:
        raise ValueError(f"invalid {path} placeholders are malformed")


def _validate_manglik_metadata(value: object, *, comparison: bool) -> None:
    path = "manglik.metadata"
    metadata = _mapping(value, path)
    fields = tuple(
        (
            MatchmakingManglikCompatibilityMetadata
            if comparison
            else MatchmakingManglikMetadata
        ).__annotations__
    )
    _exact_fields(metadata, fields, path)
    expected: dict[str, MatchmakingJsonValue] = {
        "component": (
            "matchmaking_manglik_compatibility"
            if comparison
            else "matchmaking_manglik_classification"
        ),
        "schema_version": MATCHMAKING_SCHEMA_VERSION,
        "deterministic": True,
        "calculation": (
            MANGLIK_COMPATIBILITY_CALCULATION_NAME
            if comparison
            else MANGLIK_CALCULATION_NAME
        ),
        "house_system": "whole_sign",
        "house_numbering": "one_based",
        "reference_points": [MANGLIK_REFERENCE_POINT],
        "applicable_manglik_houses": list(MANGLIK_HOUSES),
        "classification_mode": "binary",
        "comparison_mode": "structured_only",
        "scoring_included": False,
        "severity_included": False,
        "cancellation_rules_included": False,
        "divisional_charts_included": False,
        "ashtakoota_recalculated": False,
    }
    if comparison:
        expected["role_order"] = ["bride", "groom"]
        expected["same_mixed_comparison_symmetric"] = True
    if metadata != expected:
        raise ValueError("manglik.metadata is invalid")


def _validate_ashtakoota_metadata(
    value: object,
) -> dict[str, MatchmakingJsonValue]:
    metadata = _mapping(value, "ashtakoota.metadata")
    _exact_fields(
        metadata,
        tuple(MatchmakingAshtakootaMetadata.__annotations__),
        "ashtakoota.metadata",
    )
    if metadata.get("component") != "matchmaking_ashtakoota_aggregation":
        raise ValueError("ashtakoota.metadata.component is invalid")
    _validate_schema_and_determinism(metadata, "ashtakoota.metadata")
    if metadata.get("execution_mode") not in (
        "raw_calculators",
        "precomputed_results",
    ):
        raise ValueError("ashtakoota.metadata.execution_mode is invalid")
    if metadata.get("koota_order") != list(ASHTAKOOTA_KOOTA_ORDER):
        raise ValueError("ashtakoota.metadata.koota_order is invalid")
    expected_values = {
        "expected_koota_count": 8,
        "total_maximum_score": 36.0,
        "aggregation_method": "math_fsum",
        "percentage_included": False,
        "interpretation_included": False,
        "cancellation_included": False,
    }
    for field, expected in expected_values.items():
        if metadata.get(field) != expected:
            raise ValueError(f"ashtakoota.metadata.{field} is invalid")
    _integer(metadata, "validated_koota_count", "ashtakoota.metadata", 0, 8)
    return metadata


def _validate_koota_key_mapping(
    value: Mapping[str, MatchmakingJsonValue], *, allow_empty: bool
) -> None:
    if allow_empty and not value:
        return
    if tuple(value) != ASHTAKOOTA_KOOTA_ORDER:
        raise ValueError("ashtakoota.score_by_koota order is invalid")
    for koota, score in value.items():
        if score is not None:
            _finite_real(score, f"ashtakoota.score_by_koota.{koota}")


def _validate_maximum_mapping(value: Mapping[str, MatchmakingJsonValue]) -> None:
    if tuple(value) != ASHTAKOOTA_KOOTA_ORDER:
        raise ValueError("ashtakoota.maximum_score_by_koota order is invalid")
    expected = {
        koota: _KOOTA_CONTRACTS[koota]["maximum_score"]
        for koota in ASHTAKOOTA_KOOTA_ORDER
    }
    if value != expected:
        raise ValueError("ashtakoota.maximum_score_by_koota is invalid")


def _issues(value: object, path: str) -> list[MatchmakingJsonValue]:
    issues = _list(value, path)
    for index, raw_issue in enumerate(issues):
        issue_path = f"{path}[{index}]"
        issue = _mapping(raw_issue, issue_path)
        _exact_fields(issue, _ISSUE_FIELDS, issue_path)
        for field in ("field", "code", "message_key"):
            if not isinstance(issue[field], str):
                raise TypeError(f"{issue_path}.{field} must be a string")
        if issue["severity"] not in ("error", "warning"):
            raise ValueError(f"{issue_path}.severity is invalid")
        _mapping(issue["metadata"], f"{issue_path}.metadata")
    return issues


def _validate_schema_and_determinism(
    metadata: Mapping[str, MatchmakingJsonValue], path: str
) -> None:
    if metadata.get("schema_version") != MATCHMAKING_SCHEMA_VERSION:
        raise ValueError(f"{path}.schema_version is invalid")
    if metadata.get("deterministic") is not True:
        raise ValueError(f"{path}.deterministic must be true")


def _exact_fields(
    value: Mapping[str, MatchmakingJsonValue], fields: tuple[str, ...], path: str
) -> None:
    if tuple(value) != fields:
        raise ValueError(f"{path} fields or field order are invalid")


def _mapping(value: object, path: str) -> dict[str, MatchmakingJsonValue]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be a mapping")
    return value


def _list(value: object, path: str) -> list[MatchmakingJsonValue]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a list")
    return value


def _string(value: Mapping[str, MatchmakingJsonValue], field: str, path: str) -> str:
    raw = value.get(field)
    if not isinstance(raw, str):
        raise TypeError(f"{path}.{field} must be a string")
    return raw


def _boolean(value: Mapping[str, MatchmakingJsonValue], field: str, path: str) -> bool:
    raw = value.get(field)
    if type(raw) is not bool:
        raise TypeError(f"{path}.{field} must be a boolean")
    return raw


def _optional_boolean(
    value: Mapping[str, MatchmakingJsonValue], field: str, path: str
) -> bool | None:
    raw = value.get(field)
    if raw is None:
        return None
    return _boolean(value, field, path)


def _integer(
    value: Mapping[str, MatchmakingJsonValue],
    field: str,
    path: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    raw = value.get(field)
    if isinstance(raw, bool) or not isinstance(raw, Integral):
        raise TypeError(f"{path}.{field} must be an integer")
    numeric = int(raw)
    if minimum is not None and numeric < minimum:
        raise ValueError(f"{path}.{field} is below the minimum")
    if maximum is not None and numeric > maximum:
        raise ValueError(f"{path}.{field} exceeds the maximum")
    return numeric


def _optional_integer(
    value: Mapping[str, MatchmakingJsonValue],
    field: str,
    path: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    if value.get(field) is None:
        return None
    return _integer(value, field, path, minimum, maximum)


def _finite_real(value: object, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{path} must be a real number")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{path} must be finite")
    return 0.0 if numeric == 0.0 else numeric


def _float(value: dict[str, MatchmakingJsonValue], field: str, path: str) -> float:
    numeric = _finite_real(value.get(field), f"{path}.{field}")
    value[field] = numeric
    return numeric


def _optional_float(
    value: dict[str, MatchmakingJsonValue], field: str, path: str
) -> float | None:
    if value.get(field) is None:
        return None
    return _float(value, field, path)


def _string_list(value: object, path: str) -> list[str]:
    items = _list(value, path)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{path} must contain only strings")
    return cast(list[str], items)


def _integer_list(value: object, path: str) -> list[int]:
    items = _list(value, path)
    if any(isinstance(item, bool) or not isinstance(item, Integral) for item in items):
        raise TypeError(f"{path} must contain only integers")
    return [int(item) for item in items]


def _category(
    value: Mapping[str, MatchmakingJsonValue],
    field: str,
    allowed: object,
    path: str,
) -> str:
    category = _string(value, field, path)
    if category not in allowed:  # type: ignore[operator]
        raise ValueError(f"{path}.{field} is invalid")
    return category
