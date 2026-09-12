"""Canonical JSON-safe serialization for Reporting documents."""

from __future__ import annotations

from collections.abc import Mapping

from backend.app.reporting.models import (
    ReportBlock,
    ReportDocument,
    ReportField,
    ReportIssue,
    ReportJsonValue,
    ReportMetadata,
    ReportSection,
    ReportSource,
    ReportSubject,
)
from backend.app.reporting.validation import validate_report_document


def serialize_report_document(*, report: object) -> dict[str, ReportJsonValue]:
    """Validate and serialize a report into a fresh JSON-safe built-in tree."""

    validated = validate_report_document(report=report)
    return {
        "schema_id": validated.schema_id,
        "schema_version": validated.schema_version,
        "report_type": validated.report_type,
        "report_version": validated.report_version,
        "report_id": validated.report_id,
        "title": validated.title,
        "status": validated.status,
        "subjects": [_serialize_subject(item) for item in validated.subjects],
        "sections": [_serialize_section(item) for item in validated.sections],
        "sources": [_serialize_source(item) for item in validated.sources],
        "metadata": _serialize_metadata(validated.metadata),
        "errors": [_serialize_issue(item) for item in validated.errors],
        "warnings": [_serialize_issue(item) for item in validated.warnings],
        "notes": list(validated.notes),
    }


def _serialize_metadata(value: ReportMetadata) -> dict[str, ReportJsonValue]:
    return {
        "schema_id": value.schema_id,
        "source_component": value.source_component,
        "source_version": value.source_version,
        "deterministic": value.deterministic,
        "attributes": {
            key: _serialize_value(item) for key, item in value.attributes.items()
        },
    }


def _serialize_source(value: ReportSource) -> dict[str, ReportJsonValue]:
    return {
        "source_id": value.source_id,
        "source_type": value.source_type,
        "reference": value.reference,
        "version": value.version,
        "note": value.note,
    }


def _serialize_issue(value: ReportIssue) -> dict[str, ReportJsonValue]:
    return {
        "code": value.code,
        "message_key": value.message_key,
        "path": list(value.path),
        "category": value.category,
        "details": {key: _serialize_value(item) for key, item in value.details.items()},
    }


def _serialize_field(value: ReportField) -> dict[str, ReportJsonValue]:
    return {
        "field_id": value.field_id,
        "label": value.label,
        "value": _serialize_value(value.value),
        "unit": value.unit,
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_subject(value: ReportSubject) -> dict[str, ReportJsonValue]:
    return {
        "subject_id": value.subject_id,
        "role": value.role,
        "label": value.label,
        "input_schema": value.input_schema,
        "input_summary": {
            key: _serialize_value(item) for key, item in value.input_summary.items()
        },
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_block(value: ReportBlock) -> dict[str, ReportJsonValue]:
    return {
        "block_id": value.block_id,
        "kind": value.kind,
        "title": value.title,
        "payload_schema": value.payload_schema,
        "payload": _serialize_block_payload(value),
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_block_payload(value: ReportBlock) -> dict[str, ReportJsonValue]:
    payload = value.payload
    if value.kind == "key_value":
        return {"fields": [_serialize_field(item) for item in payload["fields"]]}
    if value.kind == "score":
        return {
            "score": _serialize_value(payload["score"]),
            "maximum_score": _serialize_value(payload["maximum_score"]),
            "unit": payload["unit"],
        }
    if value.kind == "status":
        return {"status_id": payload["status_id"], "label": payload["label"]}
    if value.kind == "list":
        return {"items": [_serialize_value(item) for item in payload["items"]]}
    if value.kind == "table":
        return {
            "columns": [
                {
                    "column_id": column["column_id"],
                    "label": column["label"],
                    "unit": column["unit"],
                }
                for column in payload["columns"]
            ],
            "rows": [
                [_serialize_value(item) for item in row] for row in payload["rows"]
            ],
        }
    if value.kind == "note":
        return {"text": payload["text"]}
    return {"source_id": payload["source_id"]}


def _serialize_section(value: ReportSection) -> dict[str, ReportJsonValue]:
    return {
        "section_id": value.section_id,
        "title": value.title,
        "status": value.status,
        "blocks": [_serialize_block(item) for item in value.blocks],
        "errors": [_serialize_issue(item) for item in value.errors],
        "warnings": [_serialize_issue(item) for item in value.warnings],
        "notes": list(value.notes),
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_value(value: object) -> ReportJsonValue:
    if value is None or type(value) in (str, bool, int):
        return value  # type: ignore[return-value]
    if type(value) is float:
        return 0.0 if value == 0.0 else value
    if type(value) is tuple:
        return [_serialize_value(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _serialize_value(item) for key, item in value.items()}
    raise TypeError("validated report contains an unsupported serialized value")
