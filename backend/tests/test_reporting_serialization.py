"""Serialization, ordering, and mutation-safety tests for Reporting."""

from __future__ import annotations

import json
import math
from types import MappingProxyType

import pytest

from backend.app.reporting import (
    create_report_block,
    create_report_document,
    create_report_field,
    create_report_issue,
    create_report_metadata,
    create_report_section,
    create_report_source,
    create_report_subject,
    serialize_report_document,
)


def _report():
    metadata = create_report_metadata(
        schema_id="report.metadata",
        source_component="reporting.tests",
        source_version="1.0",
        attributes={"first": 1, "second": 2.5},
    )
    subject = create_report_subject(
        subject_id="subject_1",
        role="subject",
        label="Subject",
        input_schema="report.input.summary",
        input_summary={"name": "Anita", "values": [1, True, None, -0.0]},
        metadata=metadata,
    )
    field = create_report_field(
        field_id="summary",
        label="Summary",
        value={"ordered": {"first": 1, "second": 2}},
        metadata=metadata,
    )
    source = create_report_source(
        source_id="source_1", source_type="runtime", version="1.0"
    )
    warning = create_report_issue(
        code="source_warning",
        message_key="report.validation.source_warning",
        path=["sources", 0],
        category="warning",
        details={"available": True},
    )
    blocks = [
        create_report_block(
            block_id="fields",
            kind="key_value",
            payload_schema="report.block.key_value.v1",
            payload={"fields": [field]},
            metadata=metadata,
        ),
        create_report_block(
            block_id="score",
            kind="score",
            payload_schema="report.block.score.v1",
            payload={
                "score": 0.123456789012345,
                "maximum_score": 1.0,
                "unit": "points",
            },
        ),
        create_report_block(
            block_id="status",
            kind="status",
            payload_schema="report.block.status.v1",
            payload={"status_id": "complete", "label": "Complete"},
        ),
        create_report_block(
            block_id="items",
            kind="list",
            payload_schema="report.block.list.v1",
            payload={"items": ["first", {"second": [2]}]},
        ),
        create_report_block(
            block_id="table",
            kind="table",
            payload_schema="report.block.table.v1",
            payload={
                "columns": [{"column_id": "name", "label": "Name", "unit": ""}],
                "rows": [["Anita"]],
            },
        ),
        create_report_block(
            block_id="note",
            kind="note",
            payload_schema="report.block.note.v1",
            payload={"text": "Technical note."},
        ),
        create_report_block(
            block_id="reference",
            kind="reference",
            payload_schema="report.block.reference.v1",
            payload={"source_id": "source_1"},
        ),
    ]
    section = create_report_section(
        section_id="summary",
        title="Summary",
        blocks=blocks,
        warnings=[warning],
        notes=["Section note."],
        metadata=metadata,
    )
    return create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="report_1",
        title="Foundation Report",
        subjects=[subject],
        sections=[section],
        sources=[source],
        metadata=metadata,
        warnings=[warning],
        notes=["Document note."],
    )


def test_serialized_root_and_nested_field_order_is_exact() -> None:
    serialized = serialize_report_document(report=_report())

    assert tuple(serialized) == (
        "schema_id",
        "schema_version",
        "report_type",
        "report_version",
        "report_id",
        "title",
        "status",
        "subjects",
        "sections",
        "sources",
        "metadata",
        "errors",
        "warnings",
        "notes",
    )
    assert tuple(serialized["subjects"][0]) == (
        "subject_id",
        "role",
        "label",
        "input_schema",
        "input_summary",
        "metadata",
    )
    assert tuple(serialized["sections"][0]) == (
        "section_id",
        "title",
        "status",
        "blocks",
        "errors",
        "warnings",
        "notes",
        "metadata",
    )
    assert tuple(serialized["sections"][0]["blocks"][0]) == (
        "block_id",
        "kind",
        "title",
        "payload_schema",
        "payload",
        "metadata",
    )
    assert tuple(serialized["metadata"]) == (
        "schema_id",
        "source_component",
        "source_version",
        "deterministic",
        "attributes",
    )
    assert tuple(serialized["warnings"][0]) == (
        "code",
        "message_key",
        "path",
        "category",
        "details",
    )


def test_serialization_is_json_safe_deterministic_and_builtin_only() -> None:
    report = _report()
    first = serialize_report_document(report=report)
    second = serialize_report_document(report=report)

    assert first == second
    assert first is not second
    assert json.loads(json.dumps(first, allow_nan=False)) == first
    _assert_json_builtins(first)
    assert first["sections"][0]["blocks"][1]["payload"]["score"] == (0.123456789012345)
    assert type(first["metadata"]["attributes"]["first"]) is int
    assert type(first["metadata"]["attributes"]["second"]) is float
    normalized_zero = first["subjects"][0]["input_summary"]["values"][3]
    assert math.copysign(1.0, normalized_zero) == 1.0


def test_serialization_allocates_every_mutable_path_independently() -> None:
    report = _report()
    first = serialize_report_document(report=report)
    second = serialize_report_document(report=report)

    first["subjects"][0]["input_summary"]["values"].append("changed")
    first["sections"][0]["blocks"][0]["payload"]["fields"][0]["value"]["ordered"][
        "changed"
    ] = True
    first["metadata"]["attributes"]["changed"] = True

    assert first != second
    assert serialize_report_document(report=report) == second


def test_caller_input_mutation_does_not_affect_runtime_or_serialization() -> None:
    nested = {"values": [1, {"deep": [2]}]}
    field = create_report_field(field_id="data", label="Data", value=nested)
    block = create_report_block(
        block_id="data",
        kind="key_value",
        payload_schema="report.block.key_value.v1",
        payload={"fields": [field]},
    )
    section = create_report_section(section_id="data", title="Data", blocks=[block])
    report = create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="report_1",
        title="Report",
        sections=[section],
    )

    nested["values"].append(3)
    nested["values"][1]["deep"].append(4)

    serialized = serialize_report_document(report=report)
    assert serialized["sections"][0]["blocks"][0]["payload"]["fields"][0]["value"] == {
        "values": [1, {"deep": [2]}]
    }


def test_empty_collections_and_null_values_serialize_without_omission() -> None:
    report = create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="empty",
        title="Empty",
    )
    serialized = serialize_report_document(report=report)

    assert serialized["subjects"] == []
    assert serialized["sections"] == []
    assert serialized["sources"] == []
    assert serialized["errors"] == []
    assert serialized["warnings"] == []
    assert serialized["notes"] == []
    assert serialized["metadata"]["attributes"] == {}


def test_serializer_rejects_wrong_type_and_tampered_non_finite_value() -> None:
    with pytest.raises(TypeError):
        serialize_report_document(report={})

    report = _report()
    metadata = report.metadata
    object.__setattr__(metadata, "attributes", MappingProxyType({"bad": float("nan")}))
    with pytest.raises(ValueError, match="NaN or infinity"):
        serialize_report_document(report=report)

    object.__setattr__(metadata, "attributes", MappingProxyType({"bad": -0.0}))
    with pytest.raises(ValueError, match="negative zero"):
        serialize_report_document(report=report)


def _assert_json_builtins(value: object) -> None:
    if value is None or type(value) in (str, bool, int, float):
        return
    if type(value) is list:
        for item in value:
            _assert_json_builtins(item)
        return
    if type(value) is dict:
        assert all(type(key) is str for key in value)
        for item in value.values():
            _assert_json_builtins(item)
        return
    raise AssertionError(f"non-JSON runtime type escaped: {type(value)!r}")
