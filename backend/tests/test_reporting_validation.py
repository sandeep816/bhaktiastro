"""Strict validation and invalid-input tests for Reporting models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from types import MappingProxyType

import pytest

from backend.app.reporting import (
    ReportBlock,
    ReportDocument,
    create_report_block,
    create_report_document,
    create_report_field,
    create_report_issue,
    create_report_metadata,
    create_report_section,
    create_report_source,
    create_report_subject,
    validate_report_block,
    validate_report_document,
    validate_report_section,
)


def _error(*, path: object = ("sections",)):
    return create_report_issue(
        code="missing_content",
        message_key="report.validation.missing_content",
        path=path,
        category="error",
        details={"expected": "section"},
    )


def _warning():
    return create_report_issue(
        code="source_warning",
        message_key="report.validation.source_warning",
        category="warning",
    )


def _document(**overrides: object) -> ReportDocument:
    values = {
        "report_type": "foundation",
        "report_version": "1.0",
        "report_id": "report_1",
        "title": "Foundation",
    }
    values.update(overrides)
    return create_report_document(**values)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "UPPER",
        " leading",
        "trailing ",
        "has space",
        "bad@value",
        "a" * 129,
        1,
        None,
    ],
)
def test_invalid_identifiers_are_rejected_without_normalization(value: object) -> None:
    exception = TypeError if not isinstance(value, str) else ValueError
    with pytest.raises(exception):
        create_report_subject(subject_id=value, role="subject")


@pytest.mark.parametrize(
    "value",
    ["", "1", "1.", "v1.0", "1.0.0.0", "1.0 ", "1" * 33, 1.0, None],
)
def test_invalid_report_versions_are_rejected(value: object) -> None:
    exception = TypeError if not isinstance(value, str) else ValueError
    with pytest.raises(exception):
        _document(report_version=value)


def test_identifier_length_boundary_is_exact() -> None:
    valid = "a" * 128
    assert create_report_subject(subject_id=valid, role="subject").subject_id == valid
    with pytest.raises(ValueError):
        create_report_subject(subject_id=f"{valid}a", role="subject")


def test_duplicate_document_identifiers_and_roles_are_rejected() -> None:
    first = create_report_subject(subject_id="first", role="subject")
    same_id = create_report_subject(subject_id="first", role="other")
    same_role = create_report_subject(subject_id="second", role="subject")

    with pytest.raises(ValueError, match="duplicate"):
        _document(subjects=[first, same_id])
    with pytest.raises(ValueError, match="duplicate"):
        _document(subjects=[first, same_role])

    section = create_report_section(section_id="summary", title="Summary")
    with pytest.raises(ValueError, match="duplicate"):
        _document(sections=[section, section])

    source = create_report_source(source_id="source_1", source_type="runtime")
    with pytest.raises(ValueError, match="duplicate"):
        _document(sources=[source, source])


def test_duplicate_block_field_column_and_issue_contracts_are_rejected() -> None:
    field = create_report_field(field_id="name", label="Name", value="Anita")
    with pytest.raises(ValueError, match="duplicate"):
        create_report_block(
            block_id="fields",
            kind="key_value",
            payload_schema="report.block.key_value.v1",
            payload={"fields": [field, field]},
        )

    with pytest.raises(ValueError, match="duplicate"):
        create_report_block(
            block_id="table",
            kind="table",
            payload_schema="report.block.table.v1",
            payload={
                "columns": [
                    {"column_id": "name", "label": "Name", "unit": ""},
                    {"column_id": "name", "label": "Again", "unit": ""},
                ],
                "rows": [],
            },
        )

    block = create_report_block(
        block_id="note",
        kind="note",
        payload_schema="report.block.note.v1",
        payload={"text": "Note"},
    )
    with pytest.raises(ValueError, match="duplicate"):
        create_report_section(
            section_id="summary", title="Summary", blocks=[block, block]
        )
    issue = _error()
    with pytest.raises(ValueError, match="duplicate"):
        create_report_section(
            section_id="invalid",
            title="Invalid",
            status="invalid",
            errors=[issue, issue],
        )


def test_issue_categories_and_paths_are_strict() -> None:
    assert _error(path=["sections", 0, "blocks"]).path == (
        "sections",
        0,
        "blocks",
    )
    with pytest.raises(TypeError):
        _error(path=["sections", True])
    with pytest.raises(ValueError):
        _error(path=["sections", -1])
    with pytest.raises(ValueError):
        create_report_issue(code="bad", message_key="report.bad", category="info")
    with pytest.raises(ValueError, match="wrong issue category"):
        create_report_section(
            section_id="summary", title="Summary", warnings=[_error()]
        )


def test_status_consistency_accepts_only_explicit_diagnostic_states() -> None:
    error = _error()
    incomplete_section = create_report_section(
        section_id="partial",
        title="Partial",
        status="incomplete",
        errors=[error],
    )
    invalid_section = create_report_section(
        section_id="invalid",
        title="Invalid",
        status="invalid",
        errors=[error],
    )

    assert _document(status="incomplete", errors=[error]).status == "incomplete"
    assert (
        _document(
            status="incomplete", sections=[incomplete_section], errors=[error]
        ).status
        == "incomplete"
    )
    assert (
        _document(status="invalid", sections=[invalid_section], errors=[error]).status
        == "invalid"
    )
    assert _document(warnings=[_warning()]).status == "complete"

    with pytest.raises(ValueError):
        _document(status="complete", errors=[error])
    with pytest.raises(ValueError):
        _document(status="incomplete")
    with pytest.raises(ValueError, match="omitted content"):
        _document(status="incomplete", errors=[_error(path=())])
    with pytest.raises(ValueError):
        _document(status="incomplete", sections=[invalid_section], errors=[error])
    with pytest.raises(ValueError):
        _document(status="invalid")
    with pytest.raises(ValueError):
        create_report_section(section_id="bad", title="Bad", status="incomplete")


def test_input_summary_requires_an_explicit_schema() -> None:
    with pytest.raises(ValueError, match="input_schema"):
        create_report_subject(
            subject_id="subject", role="subject", input_summary={"name": "Anita"}
        )


def test_reference_blocks_must_resolve_at_document_boundary() -> None:
    block = create_report_block(
        block_id="source",
        kind="reference",
        payload_schema="report.block.reference.v1",
        payload={"source_id": "missing_source"},
    )
    section = create_report_section(
        section_id="sources", title="Sources", blocks=[block]
    )
    with pytest.raises(ValueError, match="resolve"):
        _document(sections=[section])


@pytest.mark.parametrize(
    ("kind", "schema", "payload"),
    [
        ("key_value", "report.block.key_value.v1", {"fields": []}),
        (
            "score",
            "report.block.score.v1",
            {"score": True, "maximum_score": 1, "unit": "points"},
        ),
        (
            "score",
            "report.block.score.v1",
            {"score": 2, "maximum_score": 1, "unit": "points"},
        ),
        (
            "table",
            "report.block.table.v1",
            {
                "columns": [{"column_id": "one", "label": "One", "unit": ""}],
                "rows": [[1, 2]],
            },
        ),
        ("note", "report.block.note.v1", {"text": ""}),
    ],
)
def test_malformed_kind_specific_payloads_are_rejected(
    kind: str, schema: str, payload: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        create_report_block(
            block_id="block", kind=kind, payload_schema=schema, payload=payload
        )


def test_payload_members_schema_and_kind_are_closed() -> None:
    with pytest.raises(ValueError):
        create_report_block(
            block_id="unknown",
            kind="structured",
            payload_schema="report.block.structured.v1",
            payload={},
        )
    with pytest.raises(ValueError, match="payload_schema"):
        create_report_block(
            block_id="note",
            kind="note",
            payload_schema="report.block.list.v1",
            payload={"text": "Note"},
        )
    with pytest.raises(ValueError, match="exactly"):
        create_report_block(
            block_id="note",
            kind="note",
            payload_schema="report.block.note.v1",
            payload={"text": "Note", "icon": "star"},
        )
    with pytest.raises(ValueError, match="in order"):
        create_report_block(
            block_id="score",
            kind="score",
            payload_schema="report.block.score.v1",
            payload={"unit": "points", "score": 1, "maximum_score": 2},
        )


class _UnsupportedEnum(Enum):
    VALUE = "value"


@dataclass
class _UnsupportedDataclass:
    value: str


class _UnsupportedObject:
    pass


@pytest.mark.parametrize(
    "value",
    [
        {1, 2},
        frozenset({1, 2}),
        b"bytes",
        bytearray(b"bytes"),
        memoryview(b"bytes"),
        Decimal("1.5"),
        date(2025, 1, 1),
        datetime(2025, 1, 1),
        _UnsupportedEnum.VALUE,
        _UnsupportedDataclass("value"),
        _UnsupportedObject(),
        (item for item in [1]),
        complex(1, 2),
        ValueError("bad"),
        lambda: None,
    ],
)
def test_unsupported_recursive_values_are_rejected(value: object) -> None:
    with pytest.raises(TypeError):
        create_report_field(field_id="value", label="Value", value=value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_values_are_rejected_at_any_depth(value: float) -> None:
    with pytest.raises(ValueError, match="NaN or infinity"):
        create_report_field(field_id="value", label="Value", value={"nested": [value]})
    with pytest.raises(ValueError, match="NaN or infinity"):
        create_report_metadata(
            schema_id="report.metadata",
            source_component="reporting",
            attributes={"value": value},
        )


def test_bool_is_allowed_as_data_but_rejected_as_a_number() -> None:
    assert create_report_field(field_id="flag", label="Flag", value=True).value is True
    with pytest.raises(TypeError):
        create_report_block(
            block_id="score",
            kind="score",
            payload_schema="report.block.score.v1",
            payload={"score": True, "maximum_score": 1, "unit": "points"},
        )


def test_cycles_and_shared_mutable_aliases_are_rejected() -> None:
    cyclic_list: list[object] = []
    cyclic_list.append(cyclic_list)
    with pytest.raises(ValueError, match="cyclic"):
        create_report_field(field_id="cycle", label="Cycle", value=cyclic_list)

    cyclic_mapping: dict[str, object] = {}
    cyclic_mapping["self"] = cyclic_mapping
    with pytest.raises(ValueError, match="cyclic"):
        create_report_field(field_id="cycle", label="Cycle", value=cyclic_mapping)

    indirect_list: list[object] = []
    indirect_mapping = {"list": indirect_list}
    indirect_list.append(indirect_mapping)
    with pytest.raises(ValueError, match="cyclic"):
        create_report_field(field_id="cycle", label="Cycle", value=indirect_mapping)

    shared: list[object] = [1]
    with pytest.raises(ValueError, match="shared mutable alias"):
        create_report_field(
            field_id="alias",
            label="Alias",
            value={"first": shared, "second": shared},
        )

    shared_row: list[object] = [1]
    with pytest.raises(ValueError, match="shared mutable alias"):
        create_report_block(
            block_id="table",
            kind="table",
            payload_schema="report.block.table.v1",
            payload={
                "columns": [{"column_id": "one", "label": "One", "unit": ""}],
                "rows": [shared_row, shared_row],
            },
        )


def test_mapping_proxy_and_mapping_subclass_inputs_are_copied() -> None:
    class MappingSubclass(dict[str, object]):
        pass

    source = MappingSubclass({"first": [1]})
    proxy = MappingProxyType(source)
    value = create_report_field(field_id="value", label="Value", value=proxy)

    source["first"].append(2)  # type: ignore[union-attr]
    assert value.value["first"] == (1,)  # type: ignore[index]
    assert type(value.value) is MappingProxyType


def test_strict_validators_reject_mappings_and_tampered_models() -> None:
    block = create_report_block(
        block_id="note",
        kind="note",
        payload_schema="report.block.note.v1",
        payload={"text": "Note"},
    )
    section = create_report_section(
        section_id="summary", title="Summary", blocks=[block]
    )
    report = _document(sections=[section])

    assert validate_report_block(block=block) is block
    assert validate_report_section(section=section) is section
    assert validate_report_document(report=report) is report
    with pytest.raises(TypeError):
        validate_report_block(block={"block_id": "note"})
    with pytest.raises(TypeError):
        validate_report_section(section={"section_id": "summary"})
    with pytest.raises(TypeError):
        validate_report_document(report={"report_id": "report_1"})

    object.__setattr__(report, "schema_version", "2.0")
    with pytest.raises(ValueError, match="schema_version"):
        validate_report_document(report=report)


def test_metadata_is_deterministic_scalar_only_and_strict() -> None:
    metadata = create_report_metadata(
        schema_id="report.metadata",
        source_component="reporting",
        source_version="1.0",
        attributes={"text": "value", "flag": True, "count": 1, "ratio": 0.5},
    )
    assert tuple(metadata.attributes) == ("text", "flag", "count", "ratio")
    with pytest.raises(ValueError):
        create_report_metadata(
            schema_id="report.metadata",
            source_component="reporting",
            deterministic=False,
        )
    with pytest.raises(TypeError):
        create_report_metadata(
            schema_id="report.metadata",
            source_component="reporting",
            attributes={"nested": {}},
        )
    with pytest.raises(ValueError):
        create_report_metadata(
            schema_id="report.metadata",
            source_component="reporting",
            attributes={"nullable": None},
        )
