"""Shared structural fixtures for Interpretation foundation tests."""

from __future__ import annotations

from backend.app.interpretation import (
    create_interpretation_document,
    create_interpretation_evidence,
    create_interpretation_finding,
    create_interpretation_rule_reference,
    create_interpretation_source,
    create_interpretation_subject_reference,
)


def create_complete_document(*, interpretation_id: str = "sample_document"):
    """Create a complete synthetic structural document without astrology rules."""

    subject = create_interpretation_subject_reference(
        subject_id="subject_a", role="primary", label="Subject A"
    )
    source = create_interpretation_source(
        source_id="source_a",
        domain="kundali",
        result_family="kundali_chart",
        result_version="1.0",
        reference="fixture-a",
    )
    rule = create_interpretation_rule_reference(
        rule_id="kundali.foundation.structural.v1",
        owner="foundation",
        rule_version="1.0",
        source_reference="structural-only",
    )
    evidence = create_interpretation_evidence(
        evidence_id="evidence_a",
        source_id="source_a",
        source_path=("status",),
        relation="contextual",
        observed_value={"available": True, "count": 1, "value": 1.25},
        subject_ids=("subject_a",),
    )
    finding = create_interpretation_finding(
        finding_id="finding_a",
        rule_id="kundali.foundation.structural.v1",
        domain="kundali",
        topic="foundation",
        category="structural",
        tendency="informational",
        subject_ids=("subject_a",),
        evidence_ids=("evidence_a",),
    )
    return create_interpretation_document(
        interpretation_type="structural_test",
        interpretation_version="1.0",
        interpretation_id=interpretation_id,
        subjects=(subject,),
        sources=(source,),
        rules=(rule,),
        evidence=(evidence,),
        findings=(finding,),
    )
