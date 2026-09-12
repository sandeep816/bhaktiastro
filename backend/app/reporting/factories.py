"""Strict public factories for immutable Reporting models."""

from __future__ import annotations

from typing import cast

from backend.app.reporting.constants import (
    DEFAULT_METADATA_SCHEMA_ID,
    DEFAULT_METADATA_SOURCE_COMPONENT,
    DEFAULT_METADATA_SOURCE_VERSION,
    REPORT_BLOCK_KINDS,
    REPORT_SCHEMA_ID,
    REPORT_SCHEMA_VERSION,
)
from backend.app.reporting.models import (
    ReportBlock,
    ReportDocument,
    ReportField,
    ReportIssue,
    ReportMetadata,
    ReportSection,
    ReportSource,
    ReportSubject,
    _create_model,
)
from backend.app.reporting.validation import (
    _CopyContext,
    _freeze_block_payload,
    _freeze_metadata_attributes,
    _freeze_model_sequence,
    _freeze_notes,
    _freeze_path,
    _freeze_report_value,
    _freeze_value_mapping,
    _require_identifier,
    _require_opaque_string,
    _require_optional_identifier,
    _require_status,
    _require_text,
    _require_version,
    _validate_issue,
    _validate_metadata,
    _validate_source,
    _validate_subject,
    validate_report_block,
    validate_report_document,
    validate_report_section,
)


def create_report_metadata(
    *,
    schema_id: object,
    source_component: object,
    source_version: object = "",
    deterministic: object = True,
    attributes: object = None,
) -> ReportMetadata:
    """Create one strictly validated immutable metadata value."""

    if type(deterministic) is not bool:
        raise TypeError("deterministic must be a boolean")
    if deterministic is not True:
        raise ValueError("deterministic must be true")
    result = cast(
        ReportMetadata,
        _create_model(
            ReportMetadata,
            schema_id=_require_identifier(schema_id, field="schema_id"),
            source_component=_require_identifier(
                source_component, field="source_component"
            ),
            source_version=_require_version(
                source_version, field="source_version", allow_empty=True
            ),
            deterministic=True,
            attributes=_freeze_metadata_attributes(
                {} if attributes is None else attributes
            ),
        ),
    )
    return _validate_metadata(result, field="metadata")


def create_report_source(
    *,
    source_id: object,
    source_type: object,
    reference: object = "",
    version: object = "",
    note: object = "",
) -> ReportSource:
    """Create one immutable factual provenance value."""

    result = cast(
        ReportSource,
        _create_model(
            ReportSource,
            source_id=_require_identifier(source_id, field="source_id"),
            source_type=_require_identifier(source_type, field="source_type"),
            reference=_require_opaque_string(reference, field="reference"),
            version=_require_version(version, field="version", allow_empty=True),
            note=_require_text(note, field="note", required=False),
        ),
    )
    return _validate_source(result, field="source")


def create_report_issue(
    *,
    code: object,
    message_key: object,
    path: object = (),
    category: object = "error",
    details: object = None,
) -> ReportIssue:
    """Create one immutable localization-ready technical issue."""

    if type(category) is not str:
        raise TypeError("category must be a string")
    if category not in ("error", "warning"):
        raise ValueError("category must be error or warning")
    result = cast(
        ReportIssue,
        _create_model(
            ReportIssue,
            code=_require_identifier(code, field="code"),
            message_key=_require_identifier(message_key, field="message_key"),
            path=_freeze_path(path),
            category=category,
            details=_freeze_value_mapping(
                {} if details is None else details, field="details"
            ),
        ),
    )
    return _validate_issue(result, field="issue")


def create_report_field(
    *,
    field_id: object,
    label: object,
    value: object,
    unit: object = "",
    metadata: object = None,
) -> ReportField:
    """Create one immutable already-computed report field."""

    from backend.app.reporting.validation import _validate_field

    result = cast(
        ReportField,
        _create_model(
            ReportField,
            field_id=_require_identifier(field_id, field="field_id"),
            label=_require_text(label, field="label", required=True),
            value=_freeze_report_value(
                value,
                field="value",
                context=_CopyContext(),
                allow_none=True,
            ),
            unit=_require_optional_identifier(unit, field="unit"),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return _validate_field(result, field="field")


def create_report_subject(
    *,
    subject_id: object,
    role: object,
    label: object = "",
    input_schema: object = "",
    input_summary: object = None,
    metadata: object = None,
) -> ReportSubject:
    """Create one immutable subject without deriving domain data."""

    summary = _freeze_value_mapping(
        {} if input_summary is None else input_summary, field="input_summary"
    )
    schema = _require_optional_identifier(input_schema, field="input_schema")
    if summary and not schema:
        raise ValueError("input_schema is required when input_summary is non-empty")
    result = cast(
        ReportSubject,
        _create_model(
            ReportSubject,
            subject_id=_require_identifier(subject_id, field="subject_id"),
            role=_require_identifier(role, field="role"),
            label=_require_text(label, field="label", required=False),
            input_schema=schema,
            input_summary=summary,
            metadata=_metadata_or_default(metadata),
        ),
    )
    return _validate_subject(result, field="subject")


def create_report_block(
    *,
    block_id: object,
    kind: object,
    title: object = "",
    payload_schema: object,
    payload: object,
    metadata: object = None,
) -> ReportBlock:
    """Create one immutable closed-kind report block."""

    if type(kind) is not str:
        raise TypeError("kind must be a string")
    if kind not in REPORT_BLOCK_KINDS:
        raise ValueError("kind is not a supported report block kind")
    schema = _require_identifier(payload_schema, field="payload_schema")
    result = cast(
        ReportBlock,
        _create_model(
            ReportBlock,
            block_id=_require_identifier(block_id, field="block_id"),
            kind=kind,
            title=_require_text(title, field="title", required=False),
            payload_schema=schema,
            payload=_freeze_block_payload(
                kind=kind, payload_schema=schema, payload=payload
            ),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return validate_report_block(block=result)


def create_report_section(
    *,
    section_id: object,
    title: object,
    status: object = "complete",
    blocks: object = (),
    errors: object = (),
    warnings: object = (),
    notes: object = (),
    metadata: object = None,
) -> ReportSection:
    """Create one immutable ordered report section."""

    result = cast(
        ReportSection,
        _create_model(
            ReportSection,
            section_id=_require_identifier(section_id, field="section_id"),
            title=_require_text(title, field="title", required=True),
            status=_require_status(status),
            blocks=cast(
                tuple[ReportBlock, ...],
                _freeze_model_sequence(blocks, field="blocks", model_type=ReportBlock),
            ),
            errors=cast(
                tuple[ReportIssue, ...],
                _freeze_model_sequence(errors, field="errors", model_type=ReportIssue),
            ),
            warnings=cast(
                tuple[ReportIssue, ...],
                _freeze_model_sequence(
                    warnings, field="warnings", model_type=ReportIssue
                ),
            ),
            notes=_freeze_notes(notes),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return validate_report_section(section=result)


def create_report_document(
    *,
    report_type: object,
    report_version: object,
    report_id: object,
    title: object,
    status: object = "complete",
    subjects: object = (),
    sections: object = (),
    sources: object = (),
    metadata: object = None,
    errors: object = (),
    warnings: object = (),
    notes: object = (),
) -> ReportDocument:
    """Create one strictly validated immutable report document."""

    result = cast(
        ReportDocument,
        _create_model(
            ReportDocument,
            schema_id=REPORT_SCHEMA_ID,
            schema_version=REPORT_SCHEMA_VERSION,
            report_type=_require_identifier(report_type, field="report_type"),
            report_version=_require_version(report_version, field="report_version"),
            report_id=_require_identifier(report_id, field="report_id"),
            title=_require_text(title, field="title", required=True),
            status=_require_status(status),
            subjects=cast(
                tuple[ReportSubject, ...],
                _freeze_model_sequence(
                    subjects, field="subjects", model_type=ReportSubject
                ),
            ),
            sections=cast(
                tuple[ReportSection, ...],
                _freeze_model_sequence(
                    sections, field="sections", model_type=ReportSection
                ),
            ),
            sources=cast(
                tuple[ReportSource, ...],
                _freeze_model_sequence(
                    sources, field="sources", model_type=ReportSource
                ),
            ),
            metadata=_metadata_or_default(metadata),
            errors=cast(
                tuple[ReportIssue, ...],
                _freeze_model_sequence(errors, field="errors", model_type=ReportIssue),
            ),
            warnings=cast(
                tuple[ReportIssue, ...],
                _freeze_model_sequence(
                    warnings, field="warnings", model_type=ReportIssue
                ),
            ),
            notes=_freeze_notes(notes),
        ),
    )
    return validate_report_document(report=result)


def _metadata_or_default(value: object) -> ReportMetadata:
    if value is None:
        return create_report_metadata(
            schema_id=DEFAULT_METADATA_SCHEMA_ID,
            source_component=DEFAULT_METADATA_SOURCE_COMPONENT,
            source_version=DEFAULT_METADATA_SOURCE_VERSION,
        )
    return _validate_metadata(value, field="metadata")
