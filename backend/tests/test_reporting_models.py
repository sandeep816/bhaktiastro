"""Focused model and factory tests for the Reporting foundation."""

from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields
from types import MappingProxyType

import pytest

from backend.app.reporting import (
    REPORT_BLOCK_KINDS,
    REPORT_SCHEMA_ID,
    REPORT_SCHEMA_VERSION,
    REPORT_TECHNICAL_STATUSES,
    ReportBlock,
    ReportDocument,
    ReportField,
    ReportIssue,
    ReportMetadata,
    ReportSection,
    ReportSource,
    ReportSubject,
    create_report_block,
    create_report_document,
    create_report_field,
    create_report_issue,
    create_report_metadata,
    create_report_section,
    create_report_source,
    create_report_subject,
)


def _field(field_id: str = "name") -> ReportField:
    return create_report_field(field_id=field_id, label="Name", value="Anita")


def _source() -> ReportSource:
    return create_report_source(
        source_id="source_1",
        source_type="calculation",
        reference="calculation:1",
        version="1.0",
        note="Caller-provided source.",
    )


def _all_blocks() -> tuple[ReportBlock, ...]:
    return (
        create_report_block(
            block_id="key_values",
            kind="key_value",
            payload_schema="report.block.key_value.v1",
            payload={"fields": [_field()]},
        ),
        create_report_block(
            block_id="score",
            kind="score",
            payload_schema="report.block.score.v1",
            payload={"score": 1.5, "maximum_score": 2, "unit": "points"},
        ),
        create_report_block(
            block_id="status",
            kind="status",
            payload_schema="report.block.status.v1",
            payload={"status_id": "ready", "label": "Ready"},
        ),
        create_report_block(
            block_id="items",
            kind="list",
            payload_schema="report.block.list.v1",
            payload={"items": ["one", {"nested": [2, True, None]}]},
        ),
        create_report_block(
            block_id="table",
            kind="table",
            payload_schema="report.block.table.v1",
            payload={
                "columns": [
                    {"column_id": "name", "label": "Name", "unit": ""},
                    {"column_id": "score", "label": "Score", "unit": "points"},
                ],
                "rows": [["Anita", 1.5], ["Bharat", None]],
            },
        ),
        create_report_block(
            block_id="note",
            kind="note",
            payload_schema="report.block.note.v1",
            payload={"text": "Caller-provided note."},
        ),
        create_report_block(
            block_id="source",
            kind="reference",
            payload_schema="report.block.reference.v1",
            payload={"source_id": "source_1"},
        ),
    )


def test_public_models_have_exact_field_order() -> None:
    assert tuple(field.name for field in fields(ReportMetadata)) == (
        "schema_id",
        "source_component",
        "source_version",
        "deterministic",
        "attributes",
    )
    assert tuple(field.name for field in fields(ReportSource)) == (
        "source_id",
        "source_type",
        "reference",
        "version",
        "note",
    )
    assert tuple(field.name for field in fields(ReportIssue)) == (
        "code",
        "message_key",
        "path",
        "category",
        "details",
    )
    assert tuple(field.name for field in fields(ReportField)) == (
        "field_id",
        "label",
        "value",
        "unit",
        "metadata",
    )
    assert tuple(field.name for field in fields(ReportSubject)) == (
        "subject_id",
        "role",
        "label",
        "input_schema",
        "input_summary",
        "metadata",
    )
    assert tuple(field.name for field in fields(ReportBlock)) == (
        "block_id",
        "kind",
        "title",
        "payload_schema",
        "payload",
        "metadata",
    )
    assert tuple(field.name for field in fields(ReportSection)) == (
        "section_id",
        "title",
        "status",
        "blocks",
        "errors",
        "warnings",
        "notes",
        "metadata",
    )
    assert tuple(field.name for field in fields(ReportDocument)) == (
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


def test_constants_and_private_construction_are_exact() -> None:
    assert REPORT_SCHEMA_ID == "bhaktiastro.reporting.document"
    assert REPORT_SCHEMA_VERSION == "1.0"
    assert REPORT_TECHNICAL_STATUSES == ("complete", "incomplete", "invalid")
    assert REPORT_BLOCK_KINDS == (
        "key_value",
        "score",
        "status",
        "list",
        "table",
        "note",
        "reference",
    )
    for model in (
        ReportDocument,
        ReportSubject,
        ReportSection,
        ReportBlock,
        ReportField,
        ReportIssue,
        ReportMetadata,
        ReportSource,
    ):
        with pytest.raises(TypeError, match="must be created by a factory"):
            model()


def test_zero_subject_and_empty_complete_section_are_supported() -> None:
    empty_section = create_report_section(section_id="empty", title="Empty")
    report = create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="report_1",
        title="Foundation",
        sections=[empty_section],
    )

    assert report.schema_id == REPORT_SCHEMA_ID
    assert report.schema_version == REPORT_SCHEMA_VERSION
    assert report.subjects == ()
    assert report.sections == (empty_section,)
    assert report.status == "complete"


def test_single_directional_pair_and_multi_subject_order_are_preserved() -> None:
    bride = create_report_subject(
        subject_id="bride_1",
        role="bride",
        label="Bride",
        input_schema="report.input.summary",
        input_summary={"name": "Anita"},
    )
    groom = create_report_subject(
        subject_id="groom_1",
        role="groom",
        label="Groom",
        input_schema="report.input.summary",
        input_summary={"name": "Bharat"},
    )
    witness = create_report_subject(subject_id="witness_1", role="witness")

    single = create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="single",
        title="Single",
        subjects=[bride],
    )
    multi = create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="multi",
        title="Multi",
        subjects=[bride, groom, witness],
    )

    assert single.subjects == (bride,)
    assert [subject.role for subject in multi.subjects] == [
        "bride",
        "groom",
        "witness",
    ]


def test_every_closed_block_kind_builds_immutable_payloads() -> None:
    blocks = _all_blocks()
    assert tuple(block.kind for block in blocks) == REPORT_BLOCK_KINDS
    assert all(type(block.payload) is MappingProxyType for block in blocks)
    assert type(blocks[0].payload["fields"]) is tuple
    assert type(blocks[3].payload["items"]) is tuple
    assert type(blocks[4].payload["columns"]) is tuple
    assert type(blocks[4].payload["columns"][0]) is MappingProxyType
    assert type(blocks[4].payload["rows"]) is tuple


def test_complete_report_with_all_models_is_immutable_and_unhashable() -> None:
    section = create_report_section(
        section_id="summary",
        title="Summary",
        blocks=_all_blocks(),
        notes=["Technical note."],
    )
    report = create_report_document(
        report_type="foundation",
        report_version="1.0",
        report_id="full_report",
        title="Full Report",
        sections=[section],
        sources=[_source()],
    )

    with pytest.raises(FrozenInstanceError):
        report.title = "Changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        report.metadata.attributes["changed"] = True  # type: ignore[index]
    with pytest.raises(TypeError, match="unhashable"):
        hash(report)


def test_structural_equality_includes_mapping_order() -> None:
    first = create_report_metadata(
        schema_id="report.metadata",
        source_component="reporting",
        attributes={"first": 1, "second": 2},
    )
    same = create_report_metadata(
        schema_id="report.metadata",
        source_component="reporting",
        attributes={"first": 1, "second": 2},
    )
    reordered = create_report_metadata(
        schema_id="report.metadata",
        source_component="reporting",
        attributes={"second": 2, "first": 1},
    )

    assert first == same
    assert first != reordered


def test_default_metadata_is_equal_but_independently_allocated() -> None:
    first = _field("first")
    second = _field("second")

    assert first.metadata == second.metadata
    assert first.metadata is not second.metadata
    assert first.metadata.attributes is not second.metadata.attributes


def test_factories_are_keyword_only() -> None:
    factory_names = (
        create_report_metadata,
        create_report_source,
        create_report_issue,
        create_report_field,
        create_report_subject,
        create_report_block,
        create_report_section,
        create_report_document,
    )
    for factory in factory_names:
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(factory).parameters.values()
        )
