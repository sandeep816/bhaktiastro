"""Serialization and mutation-safety coverage for Interpretation data."""

from __future__ import annotations

import json

from backend.app.interpretation import (
    create_interpretation_evidence,
    serialize_interpretation_document,
)
from backend.tests.interpretation_test_helpers import create_complete_document


def test_serialized_root_and_nested_field_order_is_exact() -> None:
    payload = serialize_interpretation_document(document=create_complete_document())

    assert tuple(payload) == (
        "schema_id",
        "schema_version",
        "interpretation_type",
        "interpretation_version",
        "interpretation_id",
        "status",
        "subjects",
        "sources",
        "rules",
        "evidence",
        "findings",
        "metadata",
        "errors",
        "warnings",
    )
    assert tuple(payload["evidence"][0]) == (
        "evidence_id",
        "source_id",
        "source_path",
        "relation",
        "observed_value",
        "subject_ids",
        "metadata",
    )
    assert tuple(payload["findings"][0]) == (
        "finding_id",
        "rule_id",
        "domain",
        "topic",
        "category",
        "status",
        "tendency",
        "subject_ids",
        "evidence_ids",
        "errors",
        "warnings",
        "metadata",
    )


def test_serialization_is_json_safe_and_contains_no_tuples_or_custom_objects() -> None:
    payload = serialize_interpretation_document(document=create_complete_document())

    json.dumps(payload, allow_nan=False)
    _assert_built_in_json_tree(payload)


def test_repeated_serialization_is_deterministic_and_deeply_independent() -> None:
    document = create_complete_document()
    first = serialize_interpretation_document(document=document)
    second = serialize_interpretation_document(document=document)

    assert first == second
    assert first is not second
    assert first["evidence"] is not second["evidence"]
    assert (
        first["evidence"][0]["observed_value"]
        is not second["evidence"][0]["observed_value"]
    )
    first["evidence"][0]["observed_value"]["available"] = False
    first["metadata"]["attributes"]["mutated"] = True

    assert second["evidence"][0]["observed_value"]["available"] is True
    assert "mutated" not in second["metadata"]["attributes"]
    assert document.evidence[0].observed_value["available"] is True


def test_factory_defensively_copies_recursive_input() -> None:
    nested = {"items": [{"value": 1}]}
    evidence = create_interpretation_evidence(
        evidence_id="evidence",
        source_id="source",
        source_path=("value",),
        relation="contextual",
        observed_value=nested,
    )
    nested["items"][0]["value"] = 99

    assert evidence.observed_value["items"][0]["value"] == 1


def test_negative_zero_is_canonicalized() -> None:
    evidence = create_interpretation_evidence(
        evidence_id="evidence",
        source_id="source",
        source_path=("value",),
        relation="contextual",
        observed_value=-0.0,
    )

    assert evidence.observed_value == 0.0
    assert str(evidence.observed_value) == "0.0"


def _assert_built_in_json_tree(value: object) -> None:
    if value is None or type(value) in (str, bool, int, float):
        return
    if type(value) is list:
        for item in value:
            _assert_built_in_json_tree(item)
        return
    assert type(value) is dict
    for key, item in value.items():
        assert type(key) is str
        _assert_built_in_json_tree(item)
