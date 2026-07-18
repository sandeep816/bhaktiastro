"""Public API contract coverage for the Interpretation foundation."""

from __future__ import annotations

import inspect
import json

import backend.app.interpretation as interpretation

EXPECTED_EXPORTS = {
    "INTERPRETATION_DOMAINS",
    "INTERPRETATION_EVIDENCE_RELATIONS",
    "INTERPRETATION_SCHEMA_ID",
    "INTERPRETATION_SCHEMA_VERSION",
    "INTERPRETATION_TECHNICAL_STATUSES",
    "INTERPRETATION_TENDENCIES",
    "InterpretationDocument",
    "InterpretationEvidence",
    "InterpretationFinding",
    "InterpretationIssue",
    "InterpretationJsonValue",
    "InterpretationMetadata",
    "InterpretationRuleReference",
    "InterpretationScalar",
    "InterpretationSource",
    "InterpretationSubjectReference",
    "InterpretationValue",
    "create_interpretation_document",
    "create_interpretation_evidence",
    "create_interpretation_finding",
    "create_interpretation_issue",
    "create_interpretation_metadata",
    "create_interpretation_rule_reference",
    "create_interpretation_source",
    "create_interpretation_subject_reference",
    "serialize_interpretation_document",
    "validate_interpretation_document",
    "validate_interpretation_evidence",
    "validate_interpretation_finding",
}


def test_public_exports_are_exact() -> None:
    assert set(interpretation.__all__) == EXPECTED_EXPORTS
    assert len(interpretation.__all__) == len(EXPECTED_EXPORTS)
    for name in interpretation.__all__:
        assert hasattr(interpretation, name)


def test_all_public_functions_are_keyword_only() -> None:
    function_names = {
        name
        for name in EXPECTED_EXPORTS
        if name.startswith(("create_", "validate_", "serialize_"))
    }
    for name in function_names:
        signature = inspect.signature(getattr(interpretation, name))
        assert signature.parameters
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in signature.parameters.values()
        )


def test_constants_match_the_approved_schema() -> None:
    assert interpretation.INTERPRETATION_SCHEMA_ID == (
        "bhaktiastro.interpretation.document"
    )
    assert interpretation.INTERPRETATION_SCHEMA_VERSION == "1.0"
    assert interpretation.INTERPRETATION_TECHNICAL_STATUSES == (
        "complete",
        "incomplete",
        "invalid",
    )
    assert interpretation.INTERPRETATION_EVIDENCE_RELATIONS == (
        "supporting",
        "opposing",
        "contextual",
    )
    assert len(interpretation.INTERPRETATION_DOMAINS) == 8


def test_public_import_and_json_smoke() -> None:
    document = interpretation.create_interpretation_document(
        interpretation_type="smoke",
        interpretation_version="1.0",
        interpretation_id="smoke",
    )
    payload = interpretation.serialize_interpretation_document(document=document)

    assert json.loads(json.dumps(payload, allow_nan=False)) == payload
    assert not hasattr(interpretation, "generate_interpretation")
    assert not hasattr(interpretation, "render_interpretation")
    assert not hasattr(interpretation, "create_report_adapter")
