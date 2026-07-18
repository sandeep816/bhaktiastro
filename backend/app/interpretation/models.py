"""Immutable runtime models for structured Interpretation data."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import TypeAlias

from backend.app.interpretation.constants import (
    InterpretationDomain,
    InterpretationEvidenceRelation,
    InterpretationIssueCategory,
    InterpretationTechnicalStatus,
    InterpretationTendency,
)

InterpretationScalar: TypeAlias = str | bool | int | float | None
InterpretationValue: TypeAlias = (
    InterpretationScalar
    | tuple["InterpretationValue", ...]
    | Mapping[str, "InterpretationValue"]
)
InterpretationJsonValue: TypeAlias = (
    InterpretationScalar
    | list["InterpretationJsonValue"]
    | dict[str, "InterpretationJsonValue"]
)

_MODEL_TOKEN = object()


class _InterpretationModel:
    """Shared private-construction and ordered-equality behavior."""

    __slots__ = ()
    __hash__ = None

    def __new__(cls, *, _token: object = None):  # type: ignore[no-untyped-def]
        if _token is not _MODEL_TOKEN:
            raise TypeError(f"{cls.__name__} instances must be created by a factory")
        return super().__new__(cls)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        return all(
            _ordered_equal(getattr(self, field.name), getattr(other, field.name))
            for field in fields(self)
        )


def _ordered_equal(left: object, right: object) -> bool:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        left_items = tuple(left.items())
        right_items = tuple(right.items())
        return len(left_items) == len(right_items) and all(
            _ordered_equal(left_key, right_key)
            and _ordered_equal(left_value, right_value)
            for (left_key, left_value), (right_key, right_value) in zip(
                left_items, right_items, strict=True
            )
        )
    if isinstance(left, tuple) and isinstance(right, tuple):
        return len(left) == len(right) and all(
            _ordered_equal(left_item, right_item)
            for left_item, right_item in zip(left, right, strict=True)
        )
    return left == right


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationMetadata(_InterpretationModel):
    schema_id: str
    source_component: str
    source_version: str
    deterministic: bool
    attributes: Mapping[str, InterpretationScalar]


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationSubjectReference(_InterpretationModel):
    subject_id: str
    role: str
    label: str
    metadata: InterpretationMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationSource(_InterpretationModel):
    source_id: str
    domain: InterpretationDomain
    result_family: str
    result_version: str
    reference: str
    metadata: InterpretationMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationRuleReference(_InterpretationModel):
    rule_id: str
    owner: str
    rule_version: str
    source_reference: str
    metadata: InterpretationMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationEvidence(_InterpretationModel):
    evidence_id: str
    source_id: str
    source_path: tuple[str | int, ...]
    relation: InterpretationEvidenceRelation
    observed_value: InterpretationValue
    subject_ids: tuple[str, ...]
    metadata: InterpretationMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationIssue(_InterpretationModel):
    code: str
    message_key: str
    path: tuple[str | int, ...]
    category: InterpretationIssueCategory
    details: Mapping[str, InterpretationValue]


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationFinding(_InterpretationModel):
    finding_id: str
    rule_id: str
    domain: InterpretationDomain
    topic: str
    category: str
    status: InterpretationTechnicalStatus
    tendency: InterpretationTendency
    subject_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    errors: tuple[InterpretationIssue, ...]
    warnings: tuple[InterpretationIssue, ...]
    metadata: InterpretationMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class InterpretationDocument(_InterpretationModel):
    schema_id: str
    schema_version: str
    interpretation_type: str
    interpretation_version: str
    interpretation_id: str
    status: InterpretationTechnicalStatus
    subjects: tuple[InterpretationSubjectReference, ...]
    sources: tuple[InterpretationSource, ...]
    rules: tuple[InterpretationRuleReference, ...]
    evidence: tuple[InterpretationEvidence, ...]
    findings: tuple[InterpretationFinding, ...]
    metadata: InterpretationMetadata
    errors: tuple[InterpretationIssue, ...]
    warnings: tuple[InterpretationIssue, ...]


def _create_model(model_type: type[_InterpretationModel], **values: object):
    instance = model_type.__new__(model_type, _token=_MODEL_TOKEN)
    for field in fields(model_type):
        object.__setattr__(instance, field.name, values[field.name])
    return instance
