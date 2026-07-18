"""Strict public factories for immutable Interpretation models."""

from __future__ import annotations

from typing import cast

from backend.app.interpretation.constants import (
    DEFAULT_METADATA_SCHEMA_ID,
    DEFAULT_METADATA_SOURCE_COMPONENT,
    DEFAULT_METADATA_SOURCE_VERSION,
    INTERPRETATION_SCHEMA_ID,
    INTERPRETATION_SCHEMA_VERSION,
    InterpretationDomain,
    InterpretationEvidenceRelation,
    InterpretationIssueCategory,
    InterpretationTechnicalStatus,
    InterpretationTendency,
)
from backend.app.interpretation.models import (
    InterpretationDocument,
    InterpretationEvidence,
    InterpretationFinding,
    InterpretationIssue,
    InterpretationMetadata,
    InterpretationRuleReference,
    InterpretationSource,
    InterpretationSubjectReference,
    _create_model,
)
from backend.app.interpretation.validation import (
    _CopyContext,
    _freeze_identifier_sequence,
    _freeze_metadata_attributes,
    _freeze_model_sequence,
    _freeze_path,
    _freeze_value,
    _freeze_value_mapping,
    _parse_rule_id,
    _require_choice,
    _require_domain,
    _require_identifier,
    _require_opaque_string,
    _require_relation,
    _require_status,
    _require_tendency,
    _require_text,
    _require_version,
    _validate_issue,
    _validate_metadata,
    _validate_rule,
    _validate_source,
    _validate_subject,
    validate_interpretation_document,
    validate_interpretation_evidence,
    validate_interpretation_finding,
)


def create_interpretation_metadata(
    *,
    schema_id: object,
    source_component: object,
    source_version: object = "",
    deterministic: object = True,
    attributes: object = None,
) -> InterpretationMetadata:
    """Create one strictly validated immutable metadata value."""

    if type(deterministic) is not bool:
        raise TypeError("deterministic must be a boolean")
    if deterministic is not True:
        raise ValueError("deterministic must be true")
    result = cast(
        InterpretationMetadata,
        _create_model(
            InterpretationMetadata,
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


def create_interpretation_subject_reference(
    *,
    subject_id: object,
    role: object,
    label: object = "",
    metadata: object = None,
) -> InterpretationSubjectReference:
    """Create one immutable subject identity and role reference."""

    result = cast(
        InterpretationSubjectReference,
        _create_model(
            InterpretationSubjectReference,
            subject_id=_require_identifier(subject_id, field="subject_id"),
            role=_require_identifier(role, field="role"),
            label=_require_text(label, field="label"),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return _validate_subject(result, field="subject")


def create_interpretation_source(
    *,
    source_id: object,
    domain: object,
    result_family: object,
    result_version: object = "",
    reference: object = "",
    metadata: object = None,
) -> InterpretationSource:
    """Create provenance for one already-validated result family."""

    result = cast(
        InterpretationSource,
        _create_model(
            InterpretationSource,
            source_id=_require_identifier(source_id, field="source_id"),
            domain=cast(InterpretationDomain, _require_domain(domain)),
            result_family=_require_identifier(result_family, field="result_family"),
            result_version=_require_version(
                result_version, field="result_version", allow_empty=True
            ),
            reference=_require_opaque_string(reference, field="reference"),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return _validate_source(result, field="source")


def create_interpretation_rule_reference(
    *,
    rule_id: object,
    owner: object,
    rule_version: object,
    source_reference: object = "",
    metadata: object = None,
) -> InterpretationRuleReference:
    """Create one stable versioned interpretation-rule reference."""

    valid_rule_id = _require_identifier(rule_id, field="rule_id")
    _parse_rule_id(valid_rule_id, field="rule_id")
    result = cast(
        InterpretationRuleReference,
        _create_model(
            InterpretationRuleReference,
            rule_id=valid_rule_id,
            owner=_require_identifier(owner, field="owner"),
            rule_version=_require_version(rule_version, field="rule_version"),
            source_reference=_require_opaque_string(
                source_reference, field="source_reference"
            ),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return _validate_rule(result, field="rule")


def create_interpretation_evidence(
    *,
    evidence_id: object,
    source_id: object,
    source_path: object,
    relation: object,
    observed_value: object,
    subject_ids: object = (),
    metadata: object = None,
) -> InterpretationEvidence:
    """Create one immutable reference to a validated source field."""

    result = cast(
        InterpretationEvidence,
        _create_model(
            InterpretationEvidence,
            evidence_id=_require_identifier(evidence_id, field="evidence_id"),
            source_id=_require_identifier(source_id, field="source_id"),
            source_path=_freeze_path(source_path, field="source_path", required=True),
            relation=cast(InterpretationEvidenceRelation, _require_relation(relation)),
            observed_value=_freeze_value(
                observed_value,
                field="observed_value",
                context=_CopyContext(),
                allow_none=True,
            ),
            subject_ids=_freeze_identifier_sequence(subject_ids, field="subject_ids"),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return validate_interpretation_evidence(evidence=result)


def create_interpretation_issue(
    *,
    code: object,
    message_key: object,
    path: object = (),
    category: object = "error",
    details: object = None,
) -> InterpretationIssue:
    """Create one immutable localization-ready technical issue."""

    valid_category = _require_choice(
        category, field="category", choices=("error", "warning")
    )
    result = cast(
        InterpretationIssue,
        _create_model(
            InterpretationIssue,
            code=_require_identifier(code, field="code"),
            message_key=_require_identifier(message_key, field="message_key"),
            path=_freeze_path(path, field="path", required=False),
            category=cast(InterpretationIssueCategory, valid_category),
            details=_freeze_value_mapping(
                {} if details is None else details, field="details"
            ),
        ),
    )
    return _validate_issue(result, field="issue")


def create_interpretation_finding(
    *,
    finding_id: object,
    rule_id: object,
    domain: object,
    topic: object,
    category: object,
    status: object = "complete",
    tendency: object,
    subject_ids: object = (),
    evidence_ids: object = (),
    errors: object = (),
    warnings: object = (),
    metadata: object = None,
) -> InterpretationFinding:
    """Create one immutable non-narrative finding."""

    valid_rule_id = _require_identifier(rule_id, field="rule_id")
    _parse_rule_id(valid_rule_id, field="rule_id")
    result = cast(
        InterpretationFinding,
        _create_model(
            InterpretationFinding,
            finding_id=_require_identifier(finding_id, field="finding_id"),
            rule_id=valid_rule_id,
            domain=cast(InterpretationDomain, _require_domain(domain)),
            topic=_require_identifier(topic, field="topic"),
            category=_require_identifier(category, field="category"),
            status=cast(InterpretationTechnicalStatus, _require_status(status)),
            tendency=cast(InterpretationTendency, _require_tendency(tendency)),
            subject_ids=_freeze_identifier_sequence(subject_ids, field="subject_ids"),
            evidence_ids=_freeze_identifier_sequence(
                evidence_ids, field="evidence_ids"
            ),
            errors=cast(
                tuple[InterpretationIssue, ...],
                _freeze_model_sequence(
                    errors, field="errors", model_type=InterpretationIssue
                ),
            ),
            warnings=cast(
                tuple[InterpretationIssue, ...],
                _freeze_model_sequence(
                    warnings, field="warnings", model_type=InterpretationIssue
                ),
            ),
            metadata=_metadata_or_default(metadata),
        ),
    )
    return validate_interpretation_finding(finding=result)


def create_interpretation_document(
    *,
    interpretation_type: object,
    interpretation_version: object,
    interpretation_id: object,
    status: object = "complete",
    subjects: object = (),
    sources: object = (),
    rules: object = (),
    evidence: object = (),
    findings: object = (),
    metadata: object = None,
    errors: object = (),
    warnings: object = (),
) -> InterpretationDocument:
    """Create one strictly validated immutable interpretation document."""

    result = cast(
        InterpretationDocument,
        _create_model(
            InterpretationDocument,
            schema_id=INTERPRETATION_SCHEMA_ID,
            schema_version=INTERPRETATION_SCHEMA_VERSION,
            interpretation_type=_require_identifier(
                interpretation_type, field="interpretation_type"
            ),
            interpretation_version=_require_version(
                interpretation_version, field="interpretation_version"
            ),
            interpretation_id=_require_identifier(
                interpretation_id, field="interpretation_id"
            ),
            status=cast(InterpretationTechnicalStatus, _require_status(status)),
            subjects=cast(
                tuple[InterpretationSubjectReference, ...],
                _freeze_model_sequence(
                    subjects,
                    field="subjects",
                    model_type=InterpretationSubjectReference,
                ),
            ),
            sources=cast(
                tuple[InterpretationSource, ...],
                _freeze_model_sequence(
                    sources, field="sources", model_type=InterpretationSource
                ),
            ),
            rules=cast(
                tuple[InterpretationRuleReference, ...],
                _freeze_model_sequence(
                    rules, field="rules", model_type=InterpretationRuleReference
                ),
            ),
            evidence=cast(
                tuple[InterpretationEvidence, ...],
                _freeze_model_sequence(
                    evidence, field="evidence", model_type=InterpretationEvidence
                ),
            ),
            findings=cast(
                tuple[InterpretationFinding, ...],
                _freeze_model_sequence(
                    findings, field="findings", model_type=InterpretationFinding
                ),
            ),
            metadata=_metadata_or_default(metadata),
            errors=cast(
                tuple[InterpretationIssue, ...],
                _freeze_model_sequence(
                    errors, field="errors", model_type=InterpretationIssue
                ),
            ),
            warnings=cast(
                tuple[InterpretationIssue, ...],
                _freeze_model_sequence(
                    warnings, field="warnings", model_type=InterpretationIssue
                ),
            ),
        ),
    )
    return validate_interpretation_document(document=result)


def _metadata_or_default(value: object) -> InterpretationMetadata:
    if value is None:
        return create_interpretation_metadata(
            schema_id=DEFAULT_METADATA_SCHEMA_ID,
            source_component=DEFAULT_METADATA_SOURCE_COMPONENT,
            source_version=DEFAULT_METADATA_SOURCE_VERSION,
        )
    return _validate_metadata(value, field="metadata")
