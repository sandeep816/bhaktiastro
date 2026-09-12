"""Canonical JSON-safe serialization for Interpretation documents."""

from __future__ import annotations

from collections.abc import Mapping

from backend.app.interpretation.models import (
    InterpretationDocument,
    InterpretationEvidence,
    InterpretationFinding,
    InterpretationIssue,
    InterpretationJsonValue,
    InterpretationMetadata,
    InterpretationRuleReference,
    InterpretationSource,
    InterpretationSubjectReference,
)
from backend.app.interpretation.validation import validate_interpretation_document


def serialize_interpretation_document(
    *, document: object
) -> dict[str, InterpretationJsonValue]:
    """Validate and serialize a document into a fresh JSON-safe built-in tree."""

    validated = validate_interpretation_document(document=document)
    return {
        "schema_id": validated.schema_id,
        "schema_version": validated.schema_version,
        "interpretation_type": validated.interpretation_type,
        "interpretation_version": validated.interpretation_version,
        "interpretation_id": validated.interpretation_id,
        "status": validated.status,
        "subjects": [_serialize_subject(item) for item in validated.subjects],
        "sources": [_serialize_source(item) for item in validated.sources],
        "rules": [_serialize_rule(item) for item in validated.rules],
        "evidence": [_serialize_evidence(item) for item in validated.evidence],
        "findings": [_serialize_finding(item) for item in validated.findings],
        "metadata": _serialize_metadata(validated.metadata),
        "errors": [_serialize_issue(item) for item in validated.errors],
        "warnings": [_serialize_issue(item) for item in validated.warnings],
    }


def _serialize_metadata(
    value: InterpretationMetadata,
) -> dict[str, InterpretationJsonValue]:
    return {
        "schema_id": value.schema_id,
        "source_component": value.source_component,
        "source_version": value.source_version,
        "deterministic": value.deterministic,
        "attributes": {
            key: _serialize_value(item) for key, item in value.attributes.items()
        },
    }


def _serialize_subject(
    value: InterpretationSubjectReference,
) -> dict[str, InterpretationJsonValue]:
    return {
        "subject_id": value.subject_id,
        "role": value.role,
        "label": value.label,
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_source(
    value: InterpretationSource,
) -> dict[str, InterpretationJsonValue]:
    return {
        "source_id": value.source_id,
        "domain": value.domain,
        "result_family": value.result_family,
        "result_version": value.result_version,
        "reference": value.reference,
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_rule(
    value: InterpretationRuleReference,
) -> dict[str, InterpretationJsonValue]:
    return {
        "rule_id": value.rule_id,
        "owner": value.owner,
        "rule_version": value.rule_version,
        "source_reference": value.source_reference,
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_evidence(
    value: InterpretationEvidence,
) -> dict[str, InterpretationJsonValue]:
    return {
        "evidence_id": value.evidence_id,
        "source_id": value.source_id,
        "source_path": list(value.source_path),
        "relation": value.relation,
        "observed_value": _serialize_value(value.observed_value),
        "subject_ids": list(value.subject_ids),
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_issue(value: InterpretationIssue) -> dict[str, InterpretationJsonValue]:
    return {
        "code": value.code,
        "message_key": value.message_key,
        "path": list(value.path),
        "category": value.category,
        "details": {key: _serialize_value(item) for key, item in value.details.items()},
    }


def _serialize_finding(
    value: InterpretationFinding,
) -> dict[str, InterpretationJsonValue]:
    return {
        "finding_id": value.finding_id,
        "rule_id": value.rule_id,
        "domain": value.domain,
        "topic": value.topic,
        "category": value.category,
        "status": value.status,
        "tendency": value.tendency,
        "subject_ids": list(value.subject_ids),
        "evidence_ids": list(value.evidence_ids),
        "errors": [_serialize_issue(item) for item in value.errors],
        "warnings": [_serialize_issue(item) for item in value.warnings],
        "metadata": _serialize_metadata(value.metadata),
    }


def _serialize_value(value: object) -> InterpretationJsonValue:
    if value is None or type(value) in (str, bool, int):
        return value  # type: ignore[return-value]
    if type(value) is float:
        return 0.0 if value == 0.0 else value
    if type(value) is tuple:
        return [_serialize_value(item) for item in value]
    if isinstance(value, Mapping):
        return {key: _serialize_value(item) for key, item in value.items()}
    raise TypeError("validated interpretation contains an unsupported value")
