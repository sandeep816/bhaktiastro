"""Public domain-neutral Reporting data-model foundation."""

from backend.app.reporting.constants import (
    REPORT_BLOCK_KINDS,
    REPORT_SCHEMA_ID,
    REPORT_SCHEMA_VERSION,
    REPORT_TECHNICAL_STATUSES,
)
from backend.app.reporting.factories import (
    create_report_block,
    create_report_document,
    create_report_field,
    create_report_issue,
    create_report_metadata,
    create_report_section,
    create_report_source,
    create_report_subject,
)
from backend.app.reporting.models import (
    ReportBlock,
    ReportDocument,
    ReportField,
    ReportIssue,
    ReportJsonValue,
    ReportMetadata,
    ReportScalar,
    ReportSection,
    ReportSource,
    ReportSubject,
    ReportValue,
)
from backend.app.reporting.serialization import serialize_report_document
from backend.app.reporting.validation import (
    validate_report_block,
    validate_report_document,
    validate_report_section,
)

__all__ = [
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
]
