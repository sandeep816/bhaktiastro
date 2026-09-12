"""Model and construction coverage for the Interpretation foundation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from types import MappingProxyType

import pytest

from backend.app.interpretation import (
    INTERPRETATION_SCHEMA_ID,
    INTERPRETATION_SCHEMA_VERSION,
    InterpretationDocument,
    InterpretationEvidence,
    InterpretationFinding,
    InterpretationIssue,
    InterpretationMetadata,
    InterpretationRuleReference,
    InterpretationSource,
    InterpretationSubjectReference,
    create_interpretation_document,
    create_interpretation_evidence,
    create_interpretation_finding,
    create_interpretation_issue,
    create_interpretation_metadata,
    create_interpretation_rule_reference,
    create_interpretation_source,
    create_interpretation_subject_reference,
)
from backend.tests.interpretation_test_helpers import create_complete_document


def test_all_eight_models_are_exact_frozen_slotted_models() -> None:
    document = create_complete_document()
    values = (
        document,
        document.subjects[0],
        document.findings[0],
        document.evidence[0],
        create_interpretation_issue(
            code="sample_error", message_key="interpretation.sample_error"
        ),
        document.sources[0],
        document.metadata,
        document.rules[0],
    )
    expected_types = (
        InterpretationDocument,
        InterpretationSubjectReference,
        InterpretationFinding,
        InterpretationEvidence,
        InterpretationIssue,
        InterpretationSource,
        InterpretationMetadata,
        InterpretationRuleReference,
    )

    assert tuple(type(value) for value in values) == expected_types
    for value in values:
        assert not hasattr(value, "__dict__")
        with pytest.raises(FrozenInstanceError):
            setattr(value, fields(type(value))[0].name, None)
        with pytest.raises(TypeError):
            hash(value)


def test_model_field_order_is_contractual() -> None:
    expected = {
        InterpretationMetadata: (
            "schema_id",
            "source_component",
            "source_version",
            "deterministic",
            "attributes",
        ),
        InterpretationSubjectReference: (
            "subject_id",
            "role",
            "label",
            "metadata",
        ),
        InterpretationSource: (
            "source_id",
            "domain",
            "result_family",
            "result_version",
            "reference",
            "metadata",
        ),
        InterpretationRuleReference: (
            "rule_id",
            "owner",
            "rule_version",
            "source_reference",
            "metadata",
        ),
        InterpretationEvidence: (
            "evidence_id",
            "source_id",
            "source_path",
            "relation",
            "observed_value",
            "subject_ids",
            "metadata",
        ),
        InterpretationIssue: (
            "code",
            "message_key",
            "path",
            "category",
            "details",
        ),
        InterpretationFinding: (
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
        ),
        InterpretationDocument: (
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
        ),
    }
    for model_type, field_names in expected.items():
        assert tuple(field.name for field in fields(model_type)) == field_names


def test_private_model_constructors_are_enforced() -> None:
    for model_type in (
        InterpretationDocument,
        InterpretationSubjectReference,
        InterpretationFinding,
        InterpretationEvidence,
        InterpretationIssue,
        InterpretationSource,
        InterpretationMetadata,
        InterpretationRuleReference,
    ):
        with pytest.raises(TypeError, match="factory"):
            model_type()  # type: ignore[call-arg]


def test_factory_defaults_are_independent_and_immutable() -> None:
    first = create_interpretation_document(
        interpretation_type="empty",
        interpretation_version="1.0",
        interpretation_id="first",
    )
    second = create_interpretation_document(
        interpretation_type="empty",
        interpretation_version="1.0",
        interpretation_id="second",
    )

    assert first.schema_id == INTERPRETATION_SCHEMA_ID
    assert first.schema_version == INTERPRETATION_SCHEMA_VERSION
    assert first.subjects == first.sources == first.rules == ()
    assert first.evidence == first.findings == ()
    assert first.metadata is not second.metadata
    assert type(first.metadata.attributes) is MappingProxyType
    with pytest.raises(TypeError):
        first.metadata.attributes["new"] = True  # type: ignore[index]


def test_structural_equality_preserves_mapping_and_sequence_order() -> None:
    first = create_complete_document()
    second = create_complete_document()
    reordered = create_interpretation_evidence(
        evidence_id="evidence_a",
        source_id="source_a",
        source_path=("status",),
        relation="contextual",
        observed_value={"count": 1, "available": True, "value": 1.25},
        subject_ids=("subject_a",),
    )

    assert first == second
    assert first.evidence[0] != reordered


def test_zero_single_directional_two_and_multi_subjects_preserve_order() -> None:
    empty = create_interpretation_document(
        interpretation_type="subjects",
        interpretation_version="1.0",
        interpretation_id="zero",
    )
    subjects = tuple(
        create_interpretation_subject_reference(
            subject_id=f"subject_{index}", role=f"role_{index}"
        )
        for index in range(1, 5)
    )

    assert empty.subjects == ()
    for count in (1, 2, 4):
        issue = create_interpretation_issue(
            code="omitted_findings",
            message_key="interpretation.omitted_findings",
            path=("findings",),
        )
        document = create_interpretation_document(
            interpretation_type="subjects",
            interpretation_version="1.0",
            interpretation_id=f"count_{count}",
            status="incomplete",
            subjects=subjects[:count],
            errors=(issue,),
        )
        assert document.subjects == subjects[:count]


def test_individual_factories_create_exact_documented_fields() -> None:
    metadata = create_interpretation_metadata(
        schema_id="custom.metadata",
        source_component="custom.component",
        source_version="2.1",
        attributes={"mode": "test"},
    )
    subject = create_interpretation_subject_reference(
        subject_id="subject", role="primary", metadata=metadata
    )
    source = create_interpretation_source(
        source_id="source",
        domain="prediction",
        result_family="prediction_result",
    )
    rule = create_interpretation_rule_reference(
        rule_id="prediction.foundation.structural.v2",
        owner="foundation",
        rule_version="2.1.0",
    )
    evidence = create_interpretation_evidence(
        evidence_id="evidence",
        source_id="source",
        source_path=("items", 0, "status"),
        relation="supporting",
        observed_value=None,
    )
    warning = create_interpretation_issue(
        code="sample_warning",
        message_key="interpretation.sample_warning",
        category="warning",
    )
    finding = create_interpretation_finding(
        finding_id="finding",
        rule_id=rule.rule_id,
        domain="prediction",
        topic="foundation",
        category="structural",
        tendency="neutral",
        evidence_ids=(evidence.evidence_id,),
        warnings=(warning,),
    )

    assert subject.metadata is metadata
    assert source.result_version == ""
    assert rule.rule_version == "2.1.0"
    assert evidence.source_path == ("items", 0, "status")
    assert finding.warnings == (warning,)
