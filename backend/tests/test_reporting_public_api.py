"""Public import and backward-compatibility smoke tests for Reporting."""

from __future__ import annotations

import inspect

import backend.app.matchmaking as matchmaking
import backend.app.reporting as reporting

EXPECTED_EXPORTS = (
    "REPORT_BLOCK_KINDS",
    "REPORT_SCHEMA_ID",
    "REPORT_SCHEMA_VERSION",
    "REPORT_TECHNICAL_STATUSES",
    "ReportBlock",
    "ReportDocument",
    "ReportField",
    "ReportIssue",
    "ReportJsonValue",
    "ReportMetadata",
    "ReportScalar",
    "ReportSection",
    "ReportSource",
    "ReportSubject",
    "ReportValue",
    "create_report_block",
    "create_report_document",
    "create_report_field",
    "create_report_issue",
    "create_report_metadata",
    "create_report_section",
    "create_report_source",
    "create_report_subject",
    "serialize_report_document",
    "validate_report_block",
    "validate_report_document",
    "validate_report_section",
)


def test_reporting_public_exports_are_exact() -> None:
    assert tuple(reporting.__all__) == EXPECTED_EXPORTS
    assert all(hasattr(reporting, name) for name in EXPECTED_EXPORTS)
    assert not hasattr(reporting, "serialize_report_model")
    assert not hasattr(reporting, "deserialize_report_document")


def test_public_factory_validator_and_serializer_signatures_are_keyword_only() -> None:
    callables = (
        reporting.create_report_metadata,
        reporting.create_report_source,
        reporting.create_report_issue,
        reporting.create_report_field,
        reporting.create_report_subject,
        reporting.create_report_block,
        reporting.create_report_section,
        reporting.create_report_document,
        reporting.validate_report_block,
        reporting.validate_report_section,
        reporting.validate_report_document,
        reporting.serialize_report_document,
    )
    for function in callables:
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(function).parameters.values()
        )


def test_reporting_does_not_change_matchmaking_public_contract() -> None:
    result = matchmaking.compose_compatibility_report(
        bride_moon_longitude=0.0,
        groom_moon_longitude=30.0,
        bride_lagna_longitude=1.0,
        groom_lagna_longitude=1.0,
        bride_mars_longitude=1.0,
        groom_mars_longitude=31.0,
    )
    serialized = matchmaking.serialize_compatibility_report(report=result)

    assert serialized == result
    assert serialized["schema_version"] == "1.0"
    assert serialized["report_type"] == "matchmaking_compatibility_report"
    assert "ReportDocument" not in matchmaking.__all__
