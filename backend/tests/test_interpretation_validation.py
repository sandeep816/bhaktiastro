"""Strict validation coverage for the Interpretation foundation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

import pytest

from backend.app.interpretation import (
    INTERPRETATION_DOMAINS,
    INTERPRETATION_EVIDENCE_RELATIONS,
    INTERPRETATION_TENDENCIES,
    create_interpretation_document,
    create_interpretation_evidence,
    create_interpretation_finding,
    create_interpretation_issue,
    create_interpretation_rule_reference,
    create_interpretation_source,
    create_interpretation_subject_reference,
    validate_interpretation_document,
    validate_interpretation_evidence,
    validate_interpretation_finding,
)
from backend.tests.interpretation_test_helpers import create_complete_document


@pytest.mark.parametrize("domain", INTERPRETATION_DOMAINS)
def test_every_supported_domain_is_accepted(domain: str) -> None:
    source = create_interpretation_source(
        source_id="source", domain=domain, result_family="result"
    )
    assert source.domain == domain


@pytest.mark.parametrize("relation", INTERPRETATION_EVIDENCE_RELATIONS)
def test_every_supported_evidence_relation_is_accepted(relation: str) -> None:
    evidence = create_interpretation_evidence(
        evidence_id="evidence",
        source_id="source",
        source_path=("value",),
        relation=relation,
        observed_value=True,
    )
    assert evidence.relation == relation


@pytest.mark.parametrize("tendency", INTERPRETATION_TENDENCIES)
def test_every_supported_tendency_is_accepted(tendency: str) -> None:
    finding = create_interpretation_finding(
        finding_id="finding",
        rule_id="kundali.foundation.structural.v1",
        domain="kundali",
        topic="foundation",
        category="structural",
        tendency=tendency,
        evidence_ids=("evidence",),
    )
    assert finding.tendency == tendency


@pytest.mark.parametrize(
    ("factory", "keyword", "value"),
    [
        (create_interpretation_source, "domain", "unknown"),
        (create_interpretation_evidence, "relation", "favorable"),
        (create_interpretation_finding, "status", "partial"),
        (create_interpretation_finding, "tendency", "good"),
    ],
)
def test_unsupported_vocabularies_are_rejected(factory, keyword, value) -> None:
    if factory is create_interpretation_source:
        arguments = {
            "source_id": "source",
            "domain": "kundali",
            "result_family": "result",
        }
    elif factory is create_interpretation_evidence:
        arguments = {
            "evidence_id": "evidence",
            "source_id": "source",
            "source_path": ("value",),
            "relation": "contextual",
            "observed_value": 1,
        }
    else:
        arguments = {
            "finding_id": "finding",
            "rule_id": "kundali.foundation.structural.v1",
            "domain": "kundali",
            "topic": "foundation",
            "category": "structural",
            "tendency": "informational",
            "evidence_ids": ("evidence",),
        }
    arguments[keyword] = value

    with pytest.raises(ValueError):
        factory(**arguments)


@pytest.mark.parametrize(
    "value",
    ["", "Upper", " leading", "trailing ", "a..b", "1start", "a" * 129],
)
def test_invalid_identifiers_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        create_interpretation_subject_reference(subject_id=value, role="primary")


@pytest.mark.parametrize(
    ("rule_id", "owner", "version"),
    [
        ("career.001", "foundation", "1.0"),
        ("unknown.foundation.structural.v1", "foundation", "1.0"),
        ("kundali.wrong.structural.v1", "foundation", "1.0"),
        ("kundali.foundation.structural.v2", "foundation", "1.0"),
        ("kundali.foundation.structural.v0", "foundation", "1.0"),
    ],
)
def test_rule_identifier_owner_and_version_are_strict(
    rule_id: str, owner: str, version: str
) -> None:
    with pytest.raises(ValueError):
        create_interpretation_rule_reference(
            rule_id=rule_id, owner=owner, rule_version=version
        )


@pytest.mark.parametrize(
    "field", ["subject", "role", "source", "rule", "evidence", "finding"]
)
def test_duplicate_document_identifiers_are_rejected(field: str) -> None:
    document = create_complete_document()
    kwargs = {
        "interpretation_type": document.interpretation_type,
        "interpretation_version": document.interpretation_version,
        "interpretation_id": "duplicate_test",
        "subjects": document.subjects,
        "sources": document.sources,
        "rules": document.rules,
        "evidence": document.evidence,
        "findings": document.findings,
    }
    key = {
        "subject": "subjects",
        "role": "subjects",
        "source": "sources",
        "rule": "rules",
        "evidence": "evidence",
        "finding": "findings",
    }[field]
    if field == "role":
        duplicate_role = create_interpretation_subject_reference(
            subject_id="subject_b", role=document.subjects[0].role
        )
        kwargs[key] = (*document.subjects, duplicate_role)
    else:
        kwargs[key] = getattr(document, key) * 2

    with pytest.raises(ValueError, match="unique"):
        create_interpretation_document(**kwargs)


def test_duplicate_subject_and_evidence_references_are_rejected() -> None:
    with pytest.raises(ValueError, match="unique"):
        create_interpretation_evidence(
            evidence_id="evidence",
            source_id="source",
            source_path=("value",),
            relation="contextual",
            observed_value=1,
            subject_ids=("subject", "subject"),
        )


def test_empty_source_path_and_invalid_mapping_key_are_rejected() -> None:
    with pytest.raises(ValueError, match="empty"):
        create_interpretation_evidence(
            evidence_id="evidence",
            source_id="source",
            source_path=(),
            relation="contextual",
            observed_value=1,
        )
    with pytest.raises(ValueError, match="identifier"):
        create_interpretation_evidence(
            evidence_id="evidence",
            source_id="source",
            source_path=("value",),
            relation="contextual",
            observed_value={"Invalid Key": 1},
        )
    with pytest.raises(ValueError, match="unique"):
        create_interpretation_finding(
            finding_id="finding",
            rule_id="kundali.foundation.structural.v1",
            domain="kundali",
            topic="foundation",
            category="structural",
            tendency="informational",
            evidence_ids=("evidence", "evidence"),
        )


@pytest.mark.parametrize("broken", ["source", "subject", "rule", "evidence", "domain"])
def test_malformed_document_references_are_rejected(broken: str) -> None:
    document = create_complete_document()
    subject_ids = () if broken == "subject" else ("subject_a",)
    source_id = "missing" if broken == "source" else "source_a"
    rule_id = (
        "kundali.foundation.missing.v1"
        if broken == "rule"
        else "kundali.foundation.structural.v1"
    )
    evidence_id = "missing" if broken == "evidence" else "evidence_a"
    domain = "dasha" if broken == "domain" else "kundali"
    finding_subject_ids = ("missing",) if broken == "subject" else ("subject_a",)
    evidence = create_interpretation_evidence(
        evidence_id="evidence_a",
        source_id=source_id,
        source_path=("status",),
        relation="contextual",
        observed_value=True,
        subject_ids=subject_ids,
    )
    finding = create_interpretation_finding(
        finding_id="finding_a",
        rule_id=rule_id,
        domain=domain,
        topic="foundation",
        category="structural",
        tendency="informational",
        subject_ids=finding_subject_ids,
        evidence_ids=(evidence_id,),
    )

    with pytest.raises(ValueError):
        create_interpretation_document(
            interpretation_type="broken",
            interpretation_version="1.0",
            interpretation_id=f"broken_{broken}",
            subjects=document.subjects,
            sources=document.sources,
            rules=document.rules,
            evidence=(evidence,),
            findings=(finding,),
        )


def test_evidence_cannot_be_shared_between_findings() -> None:
    document = create_complete_document()
    second = create_interpretation_finding(
        finding_id="finding_b",
        rule_id=document.rules[0].rule_id,
        domain="kundali",
        topic="foundation",
        category="second",
        tendency="informational",
        evidence_ids=(document.evidence[0].evidence_id,),
    )
    with pytest.raises(ValueError, match="exactly one finding"):
        create_interpretation_document(
            interpretation_type="shared",
            interpretation_version="1.0",
            interpretation_id="shared_evidence",
            subjects=document.subjects,
            sources=document.sources,
            rules=document.rules,
            evidence=document.evidence,
            findings=(*document.findings, second),
        )


def test_complete_document_rejects_orphans_and_unreferenced_evidence() -> None:
    document = create_complete_document()
    extra_source = create_interpretation_source(
        source_id="source_b", domain="kundali", result_family="result"
    )
    with pytest.raises(ValueError, match="orphan"):
        create_interpretation_document(
            interpretation_type="orphan",
            interpretation_version="1.0",
            interpretation_id="orphan_source",
            subjects=document.subjects,
            sources=(*document.sources, extra_source),
            rules=document.rules,
            evidence=document.evidence,
            findings=document.findings,
        )
    extra_evidence = create_interpretation_evidence(
        evidence_id="evidence_b",
        source_id="source_a",
        source_path=("other",),
        relation="contextual",
        observed_value=False,
    )
    with pytest.raises(ValueError, match="exactly once"):
        create_interpretation_document(
            interpretation_type="orphan",
            interpretation_version="1.0",
            interpretation_id="orphan_evidence",
            subjects=document.subjects,
            sources=document.sources,
            rules=document.rules,
            evidence=(*document.evidence, extra_evidence),
            findings=document.findings,
        )


def test_complete_incomplete_and_invalid_status_consistency() -> None:
    error = create_interpretation_issue(
        code="missing_evidence",
        message_key="interpretation.missing_evidence",
        path=("findings", 0, "evidence_ids"),
    )
    incomplete_finding = create_interpretation_finding(
        finding_id="finding",
        rule_id="kundali.foundation.structural.v1",
        domain="kundali",
        topic="foundation",
        category="structural",
        status="incomplete",
        tendency="informational",
        errors=(error,),
    )
    invalid_finding = create_interpretation_finding(
        finding_id="finding",
        rule_id="kundali.foundation.structural.v1",
        domain="kundali",
        topic="foundation",
        category="structural",
        status="invalid",
        tendency="informational",
        errors=(error,),
    )
    rule = create_interpretation_rule_reference(
        rule_id="kundali.foundation.structural.v1",
        owner="foundation",
        rule_version="1.0",
    )

    incomplete = create_interpretation_document(
        interpretation_type="diagnostic",
        interpretation_version="1.0",
        interpretation_id="incomplete",
        status="incomplete",
        rules=(rule,),
        findings=(incomplete_finding,),
        errors=(error,),
    )
    invalid = create_interpretation_document(
        interpretation_type="diagnostic",
        interpretation_version="1.0",
        interpretation_id="invalid",
        status="invalid",
        rules=(rule,),
        findings=(invalid_finding,),
        errors=(error,),
    )

    assert incomplete.status == "incomplete"
    assert invalid.status == "invalid"
    with pytest.raises(ValueError):
        create_interpretation_finding(
            finding_id="bad",
            rule_id=rule.rule_id,
            domain="kundali",
            topic="foundation",
            category="structural",
            tendency="informational",
        )


class SampleEnum(Enum):
    VALUE = "value"


@dataclass
class SampleDataclass:
    value: int


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        complex(1, 2),
        Decimal("1.0"),
        SampleEnum.VALUE,
        SampleDataclass(1),
        {1, 2},
        frozenset({1}),
        b"bytes",
        bytearray(b"bytes"),
        datetime(2026, 1, 1),
        ValueError("error"),
        lambda: None,
        (item for item in (1, 2)),
        object(),
    ],
)
def test_nonfinite_and_unsupported_values_are_rejected(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        create_interpretation_evidence(
            evidence_id="evidence",
            source_id="source",
            source_path=("value",),
            relation="contextual",
            observed_value=value,
        )


def test_bool_is_rejected_as_a_numeric_path_index() -> None:
    with pytest.raises(TypeError):
        create_interpretation_evidence(
            evidence_id="evidence",
            source_id="source",
            source_path=(True,),
            relation="contextual",
            observed_value=1,
        )


def test_cycles_and_shared_mutable_paths_are_rejected() -> None:
    cyclic: list[object] = []
    cyclic.append(cyclic)
    shared = [1, 2]
    aliased = {"first": shared, "second": shared}

    for value in (cyclic, aliased):
        with pytest.raises(ValueError):
            create_interpretation_evidence(
                evidence_id="evidence",
                source_id="source",
                source_path=("value",),
                relation="contextual",
                observed_value=value,
            )


def test_strict_validators_accept_only_exact_models() -> None:
    document = create_complete_document()
    assert validate_interpretation_document(document=document) is document
    assert (
        validate_interpretation_evidence(evidence=document.evidence[0])
        is document.evidence[0]
    )
    assert (
        validate_interpretation_finding(finding=document.findings[0])
        is document.findings[0]
    )
    for validator, keyword in (
        (validate_interpretation_document, "document"),
        (validate_interpretation_evidence, "evidence"),
        (validate_interpretation_finding, "finding"),
    ):
        with pytest.raises(TypeError):
            validator(**{keyword: {}})
