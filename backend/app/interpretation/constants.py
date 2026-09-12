"""Stable constants for the Interpretation Data Boundary."""

from __future__ import annotations

from typing import Literal, TypeAlias

INTERPRETATION_SCHEMA_ID = "bhaktiastro.interpretation.document"
INTERPRETATION_SCHEMA_VERSION = "1.0"
INTERPRETATION_TECHNICAL_STATUSES = ("complete", "incomplete", "invalid")
INTERPRETATION_TENDENCIES = (
    "supportive",
    "challenging",
    "mixed",
    "neutral",
    "informational",
)
INTERPRETATION_EVIDENCE_RELATIONS = ("supporting", "opposing", "contextual")
INTERPRETATION_DOMAINS = (
    "kundali",
    "matchmaking",
    "panchang",
    "dasha",
    "prediction",
    "yoga",
    "dosha",
    "transit",
)

InterpretationTechnicalStatus: TypeAlias = Literal["complete", "incomplete", "invalid"]
InterpretationTendency: TypeAlias = Literal[
    "supportive", "challenging", "mixed", "neutral", "informational"
]
InterpretationEvidenceRelation: TypeAlias = Literal[
    "supporting", "opposing", "contextual"
]
InterpretationDomain: TypeAlias = Literal[
    "kundali",
    "matchmaking",
    "panchang",
    "dasha",
    "prediction",
    "yoga",
    "dosha",
    "transit",
]
InterpretationIssueCategory: TypeAlias = Literal["error", "warning"]

DEFAULT_METADATA_SCHEMA_ID = "bhaktiastro.interpretation.metadata"
DEFAULT_METADATA_SOURCE_COMPONENT = "bhaktiastro.interpretation"
DEFAULT_METADATA_SOURCE_VERSION = "1.0"
