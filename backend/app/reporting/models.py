"""Immutable runtime models for structured Reporting data."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import TypeAlias

from backend.app.reporting.constants import (
    ReportBlockKind,
    ReportIssueCategory,
    ReportTechnicalStatus,
)

ReportScalar: TypeAlias = str | bool | int | float | None
ReportValue: TypeAlias = (
    ReportScalar | tuple["ReportValue", ...] | Mapping[str, "ReportValue"]
)
ReportJsonValue: TypeAlias = (
    ReportScalar | list["ReportJsonValue"] | dict[str, "ReportJsonValue"]
)

_MODEL_TOKEN = object()


class _ReportingModel:
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
class ReportMetadata(_ReportingModel):
    schema_id: str
    source_component: str
    source_version: str
    deterministic: bool
    attributes: Mapping[str, ReportScalar]


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportSource(_ReportingModel):
    source_id: str
    source_type: str
    reference: str
    version: str
    note: str


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportIssue(_ReportingModel):
    code: str
    message_key: str
    path: tuple[str | int, ...]
    category: ReportIssueCategory
    details: Mapping[str, ReportValue]


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportField(_ReportingModel):
    field_id: str
    label: str
    value: ReportValue
    unit: str
    metadata: ReportMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportSubject(_ReportingModel):
    subject_id: str
    role: str
    label: str
    input_schema: str
    input_summary: Mapping[str, ReportValue]
    metadata: ReportMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportBlock(_ReportingModel):
    block_id: str
    kind: ReportBlockKind
    title: str
    payload_schema: str
    payload: Mapping[str, object]
    metadata: ReportMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportSection(_ReportingModel):
    section_id: str
    title: str
    status: ReportTechnicalStatus
    blocks: tuple[ReportBlock, ...]
    errors: tuple[ReportIssue, ...]
    warnings: tuple[ReportIssue, ...]
    notes: tuple[str, ...]
    metadata: ReportMetadata


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ReportDocument(_ReportingModel):
    schema_id: str
    schema_version: str
    report_type: str
    report_version: str
    report_id: str
    title: str
    status: ReportTechnicalStatus
    subjects: tuple[ReportSubject, ...]
    sections: tuple[ReportSection, ...]
    sources: tuple[ReportSource, ...]
    metadata: ReportMetadata
    errors: tuple[ReportIssue, ...]
    warnings: tuple[ReportIssue, ...]
    notes: tuple[str, ...]


def _create_model(model_type: type[_ReportingModel], **values: object):
    instance = model_type.__new__(model_type, _token=_MODEL_TOKEN)
    for field in fields(model_type):
        object.__setattr__(instance, field.name, values[field.name])
    return instance
