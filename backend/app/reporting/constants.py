"""Stable constants for the domain-neutral Reporting foundation."""

from __future__ import annotations

from typing import Literal, TypeAlias

REPORT_SCHEMA_ID = "bhaktiastro.reporting.document"
REPORT_SCHEMA_VERSION = "1.0"
REPORT_TECHNICAL_STATUSES = ("complete", "incomplete", "invalid")
REPORT_BLOCK_KINDS = (
    "key_value",
    "score",
    "status",
    "list",
    "table",
    "note",
    "reference",
)

ReportTechnicalStatus: TypeAlias = Literal["complete", "incomplete", "invalid"]
ReportBlockKind: TypeAlias = Literal[
    "key_value", "score", "status", "list", "table", "note", "reference"
]
ReportIssueCategory: TypeAlias = Literal["error", "warning"]

DEFAULT_METADATA_SCHEMA_ID = "bhaktiastro.reporting.metadata"
DEFAULT_METADATA_SOURCE_COMPONENT = "bhaktiastro.reporting"
DEFAULT_METADATA_SOURCE_VERSION = "1.0"

BLOCK_PAYLOAD_SCHEMAS = {
    "key_value": "report.block.key_value.v1",
    "score": "report.block.score.v1",
    "status": "report.block.status.v1",
    "list": "report.block.list.v1",
    "table": "report.block.table.v1",
    "note": "report.block.note.v1",
    "reference": "report.block.reference.v1",
}
