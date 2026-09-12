"""Strict validation and immutable value helpers for Interpretation models."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import is_dataclass
from enum import Enum
from types import MappingProxyType

from backend.app.interpretation.constants import (
    INTERPRETATION_DOMAINS,
    INTERPRETATION_EVIDENCE_RELATIONS,
    INTERPRETATION_SCHEMA_ID,
    INTERPRETATION_SCHEMA_VERSION,
    INTERPRETATION_TECHNICAL_STATUSES,
    INTERPRETATION_TENDENCIES,
)
from backend.app.interpretation.models import (
    InterpretationDocument,
    InterpretationEvidence,
    InterpretationFinding,
    InterpretationIssue,
    InterpretationMetadata,
    InterpretationRuleReference,
    InterpretationScalar,
    InterpretationSource,
    InterpretationSubjectReference,
    InterpretationValue,
)

_IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
_RULE_ID_PATTERN = re.compile(
    r"^(kundali|matchmaking|panchang|dasha|prediction|yoga|dosha|transit)\."
    r"([a-z][a-z0-9_-]*)\.([a-z][a-z0-9_-]*)\.v([1-9][0-9]*)$"
)
_IDENTIFIER_MAX_LENGTH = 128
_VERSION_MAX_LENGTH = 32
_ISSUE_CATEGORIES = ("error", "warning")


class _CopyContext:
    def __init__(self) -> None:
        self.active: set[int] = set()
        self.seen_mutable: set[int] = set()


def _require_identifier(value: object, *, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string identifier")
    if len(value) > _IDENTIFIER_MAX_LENGTH or not _IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(f"{field} is not a valid identifier")
    return value


def _require_version(value: object, *, field: str, allow_empty: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a version string")
    if allow_empty and value == "":
        return value
    if len(value) > _VERSION_MAX_LENGTH or not _VERSION_PATTERN.fullmatch(value):
        raise ValueError(f"{field} is not a valid version")
    return value


def _require_text(value: object, *, field: str, required: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    if required and not value:
        raise ValueError(f"{field} must not be empty")
    if value and value != value.strip():
        raise ValueError(f"{field} must not have surrounding whitespace")
    return value


def _require_opaque_string(value: object, *, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    return value


def _require_choice(value: object, *, field: str, choices: tuple[str, ...]) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    if value not in choices:
        raise ValueError(f"{field} is not supported")
    return value


def _require_status(value: object, *, field: str = "status") -> str:
    return _require_choice(
        value, field=field, choices=INTERPRETATION_TECHNICAL_STATUSES
    )


def _require_domain(value: object, *, field: str = "domain") -> str:
    return _require_choice(value, field=field, choices=INTERPRETATION_DOMAINS)


def _require_tendency(value: object, *, field: str = "tendency") -> str:
    return _require_choice(value, field=field, choices=INTERPRETATION_TENDENCIES)


def _require_relation(value: object, *, field: str = "relation") -> str:
    return _require_choice(
        value, field=field, choices=INTERPRETATION_EVIDENCE_RELATIONS
    )


def _require_sequence(
    value: object, *, field: str
) -> list[object] | tuple[object, ...]:
    if type(value) not in (list, tuple):
        raise TypeError(f"{field} must be a list or tuple")
    return value


def _copy_scalar(
    value: object, *, field: str, allow_none: bool
) -> InterpretationScalar:
    if value is None:
        if allow_none:
            return None
        raise ValueError(f"{field} must not be null")
    if type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"{field} must not contain NaN or infinity")
        return 0.0 if value == 0.0 else value
    raise TypeError(f"{field} contains an unsupported scalar type")


def _enter_container(value: object, context: _CopyContext, *, field: str) -> None:
    identity = id(value)
    if identity in context.active:
        raise ValueError(f"{field} contains a cycle")
    if type(value) is list or isinstance(value, Mapping):
        if identity in context.seen_mutable:
            raise ValueError(f"{field} contains a shared mutable input path")
        context.seen_mutable.add(identity)
    context.active.add(identity)


def _leave_container(value: object, context: _CopyContext) -> None:
    context.active.remove(id(value))


def _freeze_value(
    value: object,
    *,
    field: str,
    context: _CopyContext,
    allow_none: bool,
) -> InterpretationValue:
    if value is None or type(value) in (str, bool, int, float):
        return _copy_scalar(value, field=field, allow_none=allow_none)
    if isinstance(value, Enum) or is_dataclass(value):
        raise TypeError(f"{field} contains an unsupported object type")
    if type(value) in (list, tuple):
        _enter_container(value, context, field=field)
        try:
            return tuple(
                _freeze_value(
                    item,
                    field=f"{field}[{index}]",
                    context=context,
                    allow_none=True,
                )
                for index, item in enumerate(value)
            )
        finally:
            _leave_container(value, context)
    if isinstance(value, Mapping):
        _enter_container(value, context, field=field)
        try:
            copied: dict[str, InterpretationValue] = {}
            for key, item in value.items():
                valid_key = _require_identifier(key, field=f"{field}.key")
                copied[valid_key] = _freeze_value(
                    item,
                    field=f"{field}.{valid_key}",
                    context=context,
                    allow_none=True,
                )
            return MappingProxyType(copied)
        finally:
            _leave_container(value, context)
    raise TypeError(f"{field} contains an unsupported object type")


def _freeze_value_mapping(
    value: object, *, field: str
) -> Mapping[str, InterpretationValue]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a mapping")
    frozen = _freeze_value(
        value,
        field=field,
        context=_CopyContext(),
        allow_none=False,
    )
    if not isinstance(frozen, Mapping):
        raise TypeError(f"{field} must be a mapping")
    return frozen


def _freeze_metadata_attributes(value: object) -> Mapping[str, InterpretationScalar]:
    if not isinstance(value, Mapping):
        raise TypeError("attributes must be a mapping")
    copied: dict[str, InterpretationScalar] = {}
    for key, item in value.items():
        valid_key = _require_identifier(key, field="attributes.key")
        copied[valid_key] = _copy_scalar(
            item, field=f"attributes.{valid_key}", allow_none=False
        )
    return MappingProxyType(copied)


def _freeze_path(value: object, *, field: str, required: bool) -> tuple[str | int, ...]:
    sequence = _require_sequence(value, field=field)
    if required and not sequence:
        raise ValueError(f"{field} must not be empty")
    result: list[str | int] = []
    for index, item in enumerate(sequence):
        if type(item) is str:
            result.append(_require_identifier(item, field=f"{field}[{index}]"))
        elif type(item) is int:
            if item < 0:
                raise ValueError(f"{field}[{index}] must be non-negative")
            result.append(item)
        else:
            raise TypeError(f"{field}[{index}] must be an identifier or integer")
    return tuple(result)


def _freeze_identifier_sequence(value: object, *, field: str) -> tuple[str, ...]:
    sequence = _require_sequence(value, field=field)
    result = tuple(
        _require_identifier(item, field=f"{field}[{index}]")
        for index, item in enumerate(sequence)
    )
    _require_unique(result, field=field)
    return result


def _freeze_model_sequence(
    value: object, *, field: str, model_type: type[object]
) -> tuple[object, ...]:
    sequence = _require_sequence(value, field=field)
    result: list[object] = []
    for index, item in enumerate(sequence):
        if type(item) is not model_type:
            raise TypeError(f"{field}[{index}] must be an exact {model_type.__name__}")
        result.append(item)
    return tuple(result)


def _require_unique(values: object, *, field: str) -> None:
    seen: set[object] = set()
    for value in values:  # type: ignore[union-attr]
        if value in seen:
            raise ValueError(f"{field} must contain unique values")
        seen.add(value)


def _parse_rule_id(value: object, *, field: str) -> tuple[str, str, int]:
    rule_id = _require_identifier(value, field=field)
    match = _RULE_ID_PATTERN.fullmatch(rule_id)
    if match is None:
        raise ValueError(f"{field} is not a valid interpretation rule identifier")
    return match.group(1), match.group(2), int(match.group(4))


def _validate_canonical_value(value: object, *, field: str, allow_none: bool) -> None:
    if value is None or type(value) in (str, bool, int, float):
        canonical = _copy_scalar(value, field=field, allow_none=allow_none)
        if type(value) is float and value != canonical:
            raise ValueError(f"{field} is not canonical")
        return
    if type(value) is tuple:
        for index, item in enumerate(value):
            _validate_canonical_value(item, field=f"{field}[{index}]", allow_none=True)
        return
    if type(value) is MappingProxyType:
        for key, item in value.items():
            valid_key = _require_identifier(key, field=f"{field}.key")
            _validate_canonical_value(
                item, field=f"{field}.{valid_key}", allow_none=True
            )
        return
    raise TypeError(f"{field} contains a noncanonical value type")


def _validate_metadata(value: object, *, field: str) -> InterpretationMetadata:
    if type(value) is not InterpretationMetadata:
        raise TypeError(f"{field} must be an exact InterpretationMetadata")
    _require_identifier(value.schema_id, field=f"{field}.schema_id")
    _require_identifier(value.source_component, field=f"{field}.source_component")
    _require_version(
        value.source_version, field=f"{field}.source_version", allow_empty=True
    )
    if type(value.deterministic) is not bool:
        raise TypeError(f"{field}.deterministic must be a boolean")
    if value.deterministic is not True:
        raise ValueError(f"{field}.deterministic must be true")
    if type(value.attributes) is not MappingProxyType:
        raise TypeError(f"{field}.attributes must be a mapping proxy")
    for key, item in value.attributes.items():
        valid_key = _require_identifier(key, field=f"{field}.attributes.key")
        _copy_scalar(item, field=f"{field}.attributes.{valid_key}", allow_none=False)
    return value


def _validate_subject(value: object, *, field: str) -> InterpretationSubjectReference:
    if type(value) is not InterpretationSubjectReference:
        raise TypeError(f"{field} must be an exact InterpretationSubjectReference")
    _require_identifier(value.subject_id, field=f"{field}.subject_id")
    _require_identifier(value.role, field=f"{field}.role")
    _require_text(value.label, field=f"{field}.label")
    _validate_metadata(value.metadata, field=f"{field}.metadata")
    return value


def _validate_source(value: object, *, field: str) -> InterpretationSource:
    if type(value) is not InterpretationSource:
        raise TypeError(f"{field} must be an exact InterpretationSource")
    _require_identifier(value.source_id, field=f"{field}.source_id")
    _require_domain(value.domain, field=f"{field}.domain")
    _require_identifier(value.result_family, field=f"{field}.result_family")
    _require_version(
        value.result_version, field=f"{field}.result_version", allow_empty=True
    )
    _require_opaque_string(value.reference, field=f"{field}.reference")
    _validate_metadata(value.metadata, field=f"{field}.metadata")
    return value


def _validate_rule(value: object, *, field: str) -> InterpretationRuleReference:
    if type(value) is not InterpretationRuleReference:
        raise TypeError(f"{field} must be an exact InterpretationRuleReference")
    _, owner, major = _parse_rule_id(value.rule_id, field=f"{field}.rule_id")
    if value.owner != owner:
        raise ValueError(f"{field}.owner must match the rule identifier")
    _require_identifier(value.owner, field=f"{field}.owner")
    version = _require_version(value.rule_version, field=f"{field}.rule_version")
    if int(version.split(".", 1)[0]) != major:
        raise ValueError(f"{field}.rule_version major must match the rule identifier")
    _require_opaque_string(value.source_reference, field=f"{field}.source_reference")
    _validate_metadata(value.metadata, field=f"{field}.metadata")
    return value


def _validate_issue(value: object, *, field: str) -> InterpretationIssue:
    if type(value) is not InterpretationIssue:
        raise TypeError(f"{field} must be an exact InterpretationIssue")
    _require_identifier(value.code, field=f"{field}.code")
    _require_identifier(value.message_key, field=f"{field}.message_key")
    if type(value.path) is not tuple:
        raise TypeError(f"{field}.path must be a tuple")
    _freeze_path(value.path, field=f"{field}.path", required=False)
    _require_choice(
        value.category, field=f"{field}.category", choices=_ISSUE_CATEGORIES
    )
    if type(value.details) is not MappingProxyType:
        raise TypeError(f"{field}.details must be a mapping proxy")
    _validate_canonical_value(value.details, field=f"{field}.details", allow_none=False)
    return value


def _validate_issue_collection(
    value: object, *, field: str, category: str
) -> tuple[InterpretationIssue, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{field} must be a tuple")
    result: list[InterpretationIssue] = []
    for index, item in enumerate(value):
        issue = _validate_issue(item, field=f"{field}[{index}]")
        if issue.category != category:
            raise ValueError(f"{field} contains an issue in the wrong category")
        if any(issue == prior for prior in result):
            raise ValueError(f"{field} contains a duplicate issue")
        result.append(issue)
    return tuple(result)


def validate_interpretation_evidence(*, evidence: object) -> InterpretationEvidence:
    """Strictly validate one completed immutable InterpretationEvidence."""

    if type(evidence) is not InterpretationEvidence:
        raise TypeError("evidence must be an exact InterpretationEvidence")
    _require_identifier(evidence.evidence_id, field="evidence.evidence_id")
    _require_identifier(evidence.source_id, field="evidence.source_id")
    if type(evidence.source_path) is not tuple:
        raise TypeError("evidence.source_path must be a tuple")
    _freeze_path(evidence.source_path, field="evidence.source_path", required=True)
    _require_relation(evidence.relation, field="evidence.relation")
    _validate_canonical_value(
        evidence.observed_value, field="evidence.observed_value", allow_none=True
    )
    if type(evidence.subject_ids) is not tuple:
        raise TypeError("evidence.subject_ids must be a tuple")
    for index, subject_id in enumerate(evidence.subject_ids):
        _require_identifier(subject_id, field=f"evidence.subject_ids[{index}]")
    _require_unique(evidence.subject_ids, field="evidence.subject_ids")
    _validate_metadata(evidence.metadata, field="evidence.metadata")
    return evidence


def validate_interpretation_finding(*, finding: object) -> InterpretationFinding:
    """Strictly validate one completed immutable InterpretationFinding."""

    if type(finding) is not InterpretationFinding:
        raise TypeError("finding must be an exact InterpretationFinding")
    _require_identifier(finding.finding_id, field="finding.finding_id")
    _parse_rule_id(finding.rule_id, field="finding.rule_id")
    _require_domain(finding.domain, field="finding.domain")
    _require_identifier(finding.topic, field="finding.topic")
    _require_identifier(finding.category, field="finding.category")
    _require_status(finding.status, field="finding.status")
    _require_tendency(finding.tendency, field="finding.tendency")
    for field_name, values in (
        ("subject_ids", finding.subject_ids),
        ("evidence_ids", finding.evidence_ids),
    ):
        if type(values) is not tuple:
            raise TypeError(f"finding.{field_name} must be a tuple")
        for index, value in enumerate(values):
            _require_identifier(value, field=f"finding.{field_name}[{index}]")
        _require_unique(values, field=f"finding.{field_name}")
    errors = _validate_issue_collection(
        finding.errors, field="finding.errors", category="error"
    )
    _validate_issue_collection(
        finding.warnings, field="finding.warnings", category="warning"
    )
    _validate_metadata(finding.metadata, field="finding.metadata")
    if finding.status == "complete":
        if errors or not finding.evidence_ids:
            raise ValueError("a complete finding requires evidence and no errors")
    elif not errors:
        raise ValueError("an incomplete or invalid finding requires an error")
    return finding


def validate_interpretation_document(*, document: object) -> InterpretationDocument:
    """Strictly validate one completed immutable InterpretationDocument."""

    if type(document) is not InterpretationDocument:
        raise TypeError("document must be an exact InterpretationDocument")
    if document.schema_id != INTERPRETATION_SCHEMA_ID:
        raise ValueError("document.schema_id does not match the schema constant")
    if document.schema_version != INTERPRETATION_SCHEMA_VERSION:
        raise ValueError("document.schema_version does not match the schema constant")
    _require_identifier(
        document.interpretation_type, field="document.interpretation_type"
    )
    _require_version(
        document.interpretation_version, field="document.interpretation_version"
    )
    _require_identifier(document.interpretation_id, field="document.interpretation_id")
    _require_status(document.status, field="document.status")

    collections: tuple[tuple[str, object, type[object]], ...] = (
        ("subjects", document.subjects, InterpretationSubjectReference),
        ("sources", document.sources, InterpretationSource),
        ("rules", document.rules, InterpretationRuleReference),
        ("evidence", document.evidence, InterpretationEvidence),
        ("findings", document.findings, InterpretationFinding),
    )
    for name, values, model_type in collections:
        if type(values) is not tuple:
            raise TypeError(f"document.{name} must be a tuple")
        for index, value in enumerate(values):
            if type(value) is not model_type:
                raise TypeError(
                    f"document.{name}[{index}] must be an exact {model_type.__name__}"
                )

    for index, subject in enumerate(document.subjects):
        _validate_subject(subject, field=f"document.subjects[{index}]")
    for index, source in enumerate(document.sources):
        _validate_source(source, field=f"document.sources[{index}]")
    for index, rule in enumerate(document.rules):
        _validate_rule(rule, field=f"document.rules[{index}]")
    for evidence in document.evidence:
        validate_interpretation_evidence(evidence=evidence)
    for finding in document.findings:
        validate_interpretation_finding(finding=finding)

    _require_unique(
        (item.subject_id for item in document.subjects),
        field="document.subjects.subject_id",
    )
    _require_unique(
        (item.role for item in document.subjects), field="document.subjects.role"
    )
    _require_unique(
        (item.source_id for item in document.sources),
        field="document.sources.source_id",
    )
    _require_unique(
        (item.rule_id for item in document.rules), field="document.rules.rule_id"
    )
    _require_unique(
        (item.evidence_id for item in document.evidence),
        field="document.evidence.evidence_id",
    )
    _require_unique(
        (item.finding_id for item in document.findings),
        field="document.findings.finding_id",
    )

    subject_ids = {item.subject_id for item in document.subjects}
    source_ids = {item.source_id for item in document.sources}
    rules = {item.rule_id: item for item in document.rules}
    evidence_ids = {item.evidence_id for item in document.evidence}
    evidence_usage = {item.evidence_id: 0 for item in document.evidence}

    for evidence in document.evidence:
        if evidence.source_id not in source_ids:
            raise ValueError("an evidence source_id must resolve in the document")
        if any(subject_id not in subject_ids for subject_id in evidence.subject_ids):
            raise ValueError("an evidence subject_id must resolve in the document")

    for finding in document.findings:
        rule = rules.get(finding.rule_id)
        if rule is None:
            raise ValueError("a finding rule_id must resolve in the document")
        rule_domain, _, _ = _parse_rule_id(rule.rule_id, field="rule.rule_id")
        if finding.domain != rule_domain:
            raise ValueError("a finding domain must match its rule identifier")
        if any(subject_id not in subject_ids for subject_id in finding.subject_ids):
            raise ValueError("a finding subject_id must resolve in the document")
        for evidence_id in finding.evidence_ids:
            if evidence_id not in evidence_ids:
                raise ValueError("a finding evidence_id must resolve in the document")
            evidence_usage[evidence_id] += 1
            if evidence_usage[evidence_id] > 1:
                raise ValueError(
                    "an evidence object must belong to exactly one finding"
                )

    _validate_metadata(document.metadata, field="document.metadata")
    errors = _validate_issue_collection(
        document.errors, field="document.errors", category="error"
    )
    _validate_issue_collection(
        document.warnings, field="document.warnings", category="warning"
    )

    finding_statuses = tuple(item.status for item in document.findings)
    if document.status == "complete":
        if errors or any(status != "complete" for status in finding_statuses):
            raise ValueError("a complete document must contain only complete findings")
        used_sources = {item.source_id for item in document.evidence}
        used_rules = {item.rule_id for item in document.findings}
        if used_sources != source_ids or used_rules != set(rules):
            raise ValueError(
                "a complete document must not contain orphan sources or rules"
            )
        if any(count != 1 for count in evidence_usage.values()):
            raise ValueError(
                "complete document evidence must be referenced exactly once"
            )
    elif document.status == "incomplete":
        if not errors or "invalid" in finding_statuses:
            raise ValueError("an incomplete document has inconsistent content")
        if "incomplete" not in finding_statuses and not any(
            issue.path for issue in errors
        ):
            raise ValueError("an incomplete document must identify omitted content")
    elif not errors:
        raise ValueError("an invalid document requires an error")

    if "invalid" in finding_statuses and document.status != "invalid":
        raise ValueError("a document containing an invalid finding must be invalid")
    if "incomplete" in finding_statuses and document.status == "complete":
        raise ValueError(
            "a document containing an incomplete finding cannot be complete"
        )
    return document
