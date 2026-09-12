"""Strict validation and immutable value helpers for Reporting models."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import is_dataclass
from enum import Enum
from types import MappingProxyType

from backend.app.reporting.constants import (
    BLOCK_PAYLOAD_SCHEMAS,
    REPORT_BLOCK_KINDS,
    REPORT_SCHEMA_ID,
    REPORT_SCHEMA_VERSION,
    REPORT_TECHNICAL_STATUSES,
)
from backend.app.reporting.models import (
    ReportBlock,
    ReportDocument,
    ReportField,
    ReportIssue,
    ReportMetadata,
    ReportScalar,
    ReportSection,
    ReportSource,
    ReportSubject,
    ReportValue,
)

_IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
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


def _require_optional_identifier(value: object, *, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string identifier")
    if value == "":
        return value
    return _require_identifier(value, field=field)


def _require_version(value: object, *, field: str, allow_empty: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a version string")
    if allow_empty and value == "":
        return value
    if len(value) > _VERSION_MAX_LENGTH or not _VERSION_PATTERN.fullmatch(value):
        raise ValueError(f"{field} is not a valid version")
    return value


def _require_text(value: object, *, field: str, required: bool) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    if required and value == "":
        raise ValueError(f"{field} must not be empty")
    if value and value != value.strip():
        raise ValueError(f"{field} must not have surrounding whitespace")
    return value


def _require_opaque_string(value: object, *, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    return value


def _require_status(value: object, *, field: str = "status") -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    if value not in REPORT_TECHNICAL_STATUSES:
        raise ValueError(f"{field} is not a supported technical status")
    return value


def _require_sequence(
    value: object, *, field: str
) -> list[object] | tuple[object, ...]:
    if type(value) not in (list, tuple):
        raise TypeError(f"{field} must be a list or tuple")
    return value


def _require_mapping(value: object, *, field: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a mapping")
    return value


def _require_exact_keys(
    value: Mapping[object, object], expected: tuple[str, ...], *, field: str
) -> None:
    if tuple(value.keys()) != expected:
        raise ValueError(f"{field} must contain exactly {expected!r} in order")


def _copy_scalar(value: object, *, field: str, allow_none: bool) -> ReportScalar:
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


def _copy_number(value: object, *, field: str) -> int | float:
    if type(value) is int:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"{field} must not contain NaN or infinity")
        return 0.0 if value == 0.0 else value
    raise TypeError(f"{field} must be an integer or float, not boolean")


def _enter_container(value: object, context: _CopyContext, *, field: str) -> int:
    identity = id(value)
    if identity in context.active:
        raise ValueError(f"{field} contains a cyclic reference")
    if identity in context.seen_mutable:
        raise ValueError(f"{field} contains a shared mutable alias")
    context.active.add(identity)
    context.seen_mutable.add(identity)
    return identity


def _enter_sequence(
    value: list[object] | tuple[object, ...],
    context: _CopyContext,
    *,
    field: str,
) -> int:
    if type(value) is list:
        return _enter_container(value, context, field=field)
    identity = id(value)
    if identity in context.active:
        raise ValueError(f"{field} contains a cyclic reference")
    context.active.add(identity)
    return identity


def _freeze_report_value(
    value: object,
    *,
    field: str,
    context: _CopyContext,
    allow_none: bool = True,
) -> ReportValue:
    if value is None or type(value) in (str, bool, int, float):
        return _copy_scalar(value, field=field, allow_none=allow_none)
    if isinstance(value, Enum) or is_dataclass(value):
        raise TypeError(f"{field} contains an unsupported object")
    if type(value) is list:
        identity = _enter_container(value, context, field=field)
        try:
            return tuple(
                _freeze_report_value(
                    item,
                    field=f"{field}[{index}]",
                    context=context,
                    allow_none=True,
                )
                for index, item in enumerate(value)
            )
        finally:
            context.active.remove(identity)
    if type(value) is tuple:
        identity = id(value)
        if identity in context.active:
            raise ValueError(f"{field} contains a cyclic reference")
        context.active.add(identity)
        try:
            return tuple(
                _freeze_report_value(
                    item,
                    field=f"{field}[{index}]",
                    context=context,
                    allow_none=True,
                )
                for index, item in enumerate(value)
            )
        finally:
            context.active.remove(identity)
    if isinstance(value, Mapping):
        identity = _enter_container(value, context, field=field)
        try:
            copied: dict[str, ReportValue] = {}
            for key, item in value.items():
                copied_key = _require_identifier(key, field=f"{field}.key")
                copied[copied_key] = _freeze_report_value(
                    item,
                    field=f"{field}.{copied_key}",
                    context=context,
                    allow_none=True,
                )
            return MappingProxyType(copied)
        finally:
            context.active.remove(identity)
    raise TypeError(f"{field} contains an unsupported value type")


def _freeze_value_mapping(
    value: object, *, field: str, context: _CopyContext | None = None
) -> Mapping[str, ReportValue]:
    mapping = _require_mapping(value, field=field)
    copied = _freeze_report_value(
        mapping,
        field=field,
        context=context or _CopyContext(),
        allow_none=False,
    )
    if not isinstance(copied, Mapping):  # pragma: no cover - guarded above
        raise TypeError(f"{field} must be a mapping")
    return copied


def _freeze_metadata_attributes(value: object) -> Mapping[str, ReportScalar]:
    mapping = _require_mapping(value, field="attributes")
    context = _CopyContext()
    identity = _enter_container(mapping, context, field="attributes")
    try:
        copied: dict[str, ReportScalar] = {}
        for key, item in mapping.items():
            copied_key = _require_identifier(key, field="attributes.key")
            copied[copied_key] = _copy_scalar(
                item, field=f"attributes.{copied_key}", allow_none=False
            )
        return MappingProxyType(copied)
    finally:
        context.active.remove(identity)


def _freeze_path(value: object) -> tuple[str | int, ...]:
    sequence = _require_sequence(value, field="path")
    copied: list[str | int] = []
    for index, part in enumerate(sequence):
        if type(part) is str:
            copied.append(_require_identifier(part, field=f"path[{index}]"))
        elif type(part) is int:
            if part < 0:
                raise ValueError(f"path[{index}] must be non-negative")
            copied.append(part)
        else:
            raise TypeError(f"path[{index}] must be an identifier or integer")
    return tuple(copied)


def _freeze_model_sequence(
    value: object, *, field: str, model_type: type[object]
) -> tuple[object, ...]:
    sequence = _require_sequence(value, field=field)
    copied: list[object] = []
    for index, item in enumerate(sequence):
        if type(item) is not model_type:
            raise TypeError(f"{field}[{index}] must be an exact {model_type.__name__}")
        copied.append(item)
    return tuple(copied)


def _freeze_notes(value: object, *, field: str = "notes") -> tuple[str, ...]:
    sequence = _require_sequence(value, field=field)
    return tuple(
        _require_text(item, field=f"{field}[{index}]", required=True)
        for index, item in enumerate(sequence)
    )


def _freeze_block_payload(
    *, kind: str, payload_schema: str, payload: object
) -> Mapping[str, object]:
    expected_schema = BLOCK_PAYLOAD_SCHEMAS[kind]
    if payload_schema != expected_schema:
        raise ValueError("payload_schema does not match block kind")
    mapping = _require_mapping(payload, field="payload")
    context = _CopyContext()

    if kind == "key_value":
        _require_exact_keys(mapping, ("fields",), field="payload")
        fields_value = _freeze_model_sequence(
            mapping["fields"], field="payload.fields", model_type=ReportField
        )
        if not fields_value:
            raise ValueError("payload.fields must not be empty")
        _require_unique(
            (field.field_id for field in fields_value), field="payload.fields.field_id"
        )
        return MappingProxyType({"fields": fields_value})

    if kind == "score":
        _require_exact_keys(
            mapping, ("score", "maximum_score", "unit"), field="payload"
        )
        score = _copy_number(mapping["score"], field="payload.score")
        maximum = _copy_number(mapping["maximum_score"], field="payload.maximum_score")
        if maximum <= 0:
            raise ValueError("payload.maximum_score must be greater than zero")
        if score < 0 or score > maximum:
            raise ValueError("payload.score must be within its allowed range")
        unit = _require_identifier(mapping["unit"], field="payload.unit")
        return MappingProxyType(
            {"score": score, "maximum_score": maximum, "unit": unit}
        )

    if kind == "status":
        _require_exact_keys(mapping, ("status_id", "label"), field="payload")
        return MappingProxyType(
            {
                "status_id": _require_identifier(
                    mapping["status_id"], field="payload.status_id"
                ),
                "label": _require_text(
                    mapping["label"], field="payload.label", required=True
                ),
            }
        )

    if kind == "list":
        _require_exact_keys(mapping, ("items",), field="payload")
        items = _require_sequence(mapping["items"], field="payload.items")
        identity = _enter_sequence(items, context, field="payload.items")
        try:
            copied_items = tuple(
                _freeze_report_value(
                    item,
                    field=f"payload.items[{index}]",
                    context=context,
                    allow_none=True,
                )
                for index, item in enumerate(items)
            )
        finally:
            context.active.remove(identity)
        return MappingProxyType({"items": copied_items})

    if kind == "table":
        _require_exact_keys(mapping, ("columns", "rows"), field="payload")
        columns = _require_sequence(mapping["columns"], field="payload.columns")
        copied_columns: list[Mapping[str, object]] = []
        columns_identity = _enter_sequence(columns, context, field="payload.columns")
        try:
            for index, column in enumerate(columns):
                column_mapping = _require_mapping(
                    column, field=f"payload.columns[{index}]"
                )
                column_identity = _enter_container(
                    column_mapping, context, field=f"payload.columns[{index}]"
                )
                try:
                    _require_exact_keys(
                        column_mapping,
                        ("column_id", "label", "unit"),
                        field=f"payload.columns[{index}]",
                    )
                    copied_columns.append(
                        MappingProxyType(
                            {
                                "column_id": _require_identifier(
                                    column_mapping["column_id"],
                                    field=f"payload.columns[{index}].column_id",
                                ),
                                "label": _require_text(
                                    column_mapping["label"],
                                    field=f"payload.columns[{index}].label",
                                    required=True,
                                ),
                                "unit": _require_optional_identifier(
                                    column_mapping["unit"],
                                    field=f"payload.columns[{index}].unit",
                                ),
                            }
                        )
                    )
                finally:
                    context.active.remove(column_identity)
        finally:
            context.active.remove(columns_identity)
        _require_unique(
            (column["column_id"] for column in copied_columns),
            field="payload.columns.column_id",
        )

        rows = _require_sequence(mapping["rows"], field="payload.rows")
        copied_rows: list[tuple[ReportScalar, ...]] = []
        rows_identity = _enter_sequence(rows, context, field="payload.rows")
        try:
            for row_index, row in enumerate(rows):
                row_values = _require_sequence(row, field=f"payload.rows[{row_index}]")
                row_identity = _enter_sequence(
                    row_values, context, field=f"payload.rows[{row_index}]"
                )
                try:
                    if len(row_values) != len(copied_columns):
                        raise ValueError("each payload row must match the column count")
                    copied_rows.append(
                        tuple(
                            _copy_scalar(
                                cell,
                                field=f"payload.rows[{row_index}][{cell_index}]",
                                allow_none=True,
                            )
                            for cell_index, cell in enumerate(row_values)
                        )
                    )
                finally:
                    context.active.remove(row_identity)
        finally:
            context.active.remove(rows_identity)
        return MappingProxyType(
            {"columns": tuple(copied_columns), "rows": tuple(copied_rows)}
        )

    if kind == "note":
        _require_exact_keys(mapping, ("text",), field="payload")
        return MappingProxyType(
            {
                "text": _require_text(
                    mapping["text"], field="payload.text", required=True
                )
            }
        )

    if kind == "reference":
        _require_exact_keys(mapping, ("source_id",), field="payload")
        return MappingProxyType(
            {
                "source_id": _require_identifier(
                    mapping["source_id"], field="payload.source_id"
                )
            }
        )

    raise ValueError("kind is not a supported block kind")  # pragma: no cover


def _require_unique(values, *, field: str) -> None:  # type: ignore[no-untyped-def]
    seen: list[object] = []
    for value in values:
        if value in seen:
            raise ValueError(f"{field} contains a duplicate value")
        seen.append(value)


def _validate_metadata(value: object, *, field: str) -> ReportMetadata:
    if type(value) is not ReportMetadata:
        raise TypeError(f"{field} must be an exact ReportMetadata")
    _require_identifier(value.schema_id, field=f"{field}.schema_id")
    _require_identifier(value.source_component, field=f"{field}.source_component")
    _require_version(
        value.source_version, field=f"{field}.source_version", allow_empty=True
    )
    if type(value.deterministic) is not bool:
        raise TypeError(f"{field}.deterministic must be a boolean")
    if value.deterministic is not True:
        raise ValueError(f"{field}.deterministic must be true")
    _validate_frozen_scalar_mapping(
        value.attributes, field=f"{field}.attributes", allow_none=False
    )
    return value


def _validate_source(value: object, *, field: str) -> ReportSource:
    if type(value) is not ReportSource:
        raise TypeError(f"{field} must be an exact ReportSource")
    _require_identifier(value.source_id, field=f"{field}.source_id")
    _require_identifier(value.source_type, field=f"{field}.source_type")
    _require_opaque_string(value.reference, field=f"{field}.reference")
    _require_version(value.version, field=f"{field}.version", allow_empty=True)
    _require_text(value.note, field=f"{field}.note", required=False)
    return value


def _validate_issue(value: object, *, field: str) -> ReportIssue:
    if type(value) is not ReportIssue:
        raise TypeError(f"{field} must be an exact ReportIssue")
    _require_identifier(value.code, field=f"{field}.code")
    _require_identifier(value.message_key, field=f"{field}.message_key")
    if type(value.path) is not tuple:
        raise TypeError(f"{field}.path must be a tuple")
    _freeze_path(value.path)
    if type(value.category) is not str:
        raise TypeError(f"{field}.category must be a string")
    if value.category not in _ISSUE_CATEGORIES:
        raise ValueError(f"{field}.category is invalid")
    _validate_frozen_value_mapping(value.details, field=f"{field}.details")
    return value


def _validate_field(value: object, *, field: str) -> ReportField:
    if type(value) is not ReportField:
        raise TypeError(f"{field} must be an exact ReportField")
    _require_identifier(value.field_id, field=f"{field}.field_id")
    _require_text(value.label, field=f"{field}.label", required=True)
    _validate_frozen_value(value.value, field=f"{field}.value", allow_none=True)
    _require_optional_identifier(value.unit, field=f"{field}.unit")
    _validate_metadata(value.metadata, field=f"{field}.metadata")
    return value


def _validate_subject(value: object, *, field: str) -> ReportSubject:
    if type(value) is not ReportSubject:
        raise TypeError(f"{field} must be an exact ReportSubject")
    _require_identifier(value.subject_id, field=f"{field}.subject_id")
    _require_identifier(value.role, field=f"{field}.role")
    _require_text(value.label, field=f"{field}.label", required=False)
    _require_optional_identifier(value.input_schema, field=f"{field}.input_schema")
    _validate_frozen_value_mapping(value.input_summary, field=f"{field}.input_summary")
    if value.input_summary and not value.input_schema:
        raise ValueError(f"{field}.input_schema is required with input_summary")
    _validate_metadata(value.metadata, field=f"{field}.metadata")
    return value


def _validate_frozen_scalar_mapping(
    value: object, *, field: str, allow_none: bool
) -> None:
    if type(value) is not MappingProxyType:
        raise TypeError(f"{field} must be a mapping proxy")
    for key, item in value.items():
        _require_identifier(key, field=f"{field}.key")
        _validate_canonical_scalar(item, field=f"{field}.{key}", allow_none=allow_none)


def _validate_canonical_scalar(value: object, *, field: str, allow_none: bool) -> None:
    _copy_scalar(value, field=field, allow_none=allow_none)
    if type(value) is float and value == 0.0 and math.copysign(1.0, value) < 0:
        raise ValueError(f"{field} contains noncanonical negative zero")


def _validate_frozen_value_mapping(value: object, *, field: str) -> None:
    if type(value) is not MappingProxyType:
        raise TypeError(f"{field} must be a mapping proxy")
    _validate_frozen_value(value, field=field, allow_none=False)


def _validate_frozen_value(
    value: object,
    *,
    field: str,
    allow_none: bool,
    active: set[int] | None = None,
) -> None:
    if value is None or type(value) in (str, bool, int, float):
        _validate_canonical_scalar(value, field=field, allow_none=allow_none)
        return
    active = active if active is not None else set()
    if type(value) is tuple:
        identity = id(value)
        if identity in active:
            raise ValueError(f"{field} contains a cyclic reference")
        active.add(identity)
        try:
            for index, item in enumerate(value):
                _validate_frozen_value(
                    item,
                    field=f"{field}[{index}]",
                    allow_none=True,
                    active=active,
                )
        finally:
            active.remove(identity)
        return
    if type(value) is MappingProxyType:
        identity = id(value)
        if identity in active:
            raise ValueError(f"{field} contains a cyclic reference")
        active.add(identity)
        try:
            for key, item in value.items():
                key_value = _require_identifier(key, field=f"{field}.key")
                _validate_frozen_value(
                    item,
                    field=f"{field}.{key_value}",
                    allow_none=True,
                    active=active,
                )
        finally:
            active.remove(identity)
        return
    raise TypeError(f"{field} contains a non-immutable runtime value")


def _validate_issue_collection(
    value: object, *, field: str, category: str
) -> tuple[ReportIssue, ...]:
    if type(value) is not tuple:
        raise TypeError(f"{field} must be a tuple")
    for index, issue in enumerate(value):
        _validate_issue(issue, field=f"{field}[{index}]")
        if issue.category != category:
            raise ValueError(f"{field}[{index}] has the wrong issue category")
    _require_unique(value, field=field)
    return value


def _validate_notes(value: object, *, field: str) -> None:
    if type(value) is not tuple:
        raise TypeError(f"{field} must be a tuple")
    for index, note in enumerate(value):
        _require_text(note, field=f"{field}[{index}]", required=True)


def _validate_block_payload(block: ReportBlock) -> None:
    if type(block.payload) is not MappingProxyType:
        raise TypeError("block.payload must be a mapping proxy")
    kind = block.kind
    expected_schema = BLOCK_PAYLOAD_SCHEMAS[kind]
    if block.payload_schema != expected_schema:
        raise ValueError("block.payload_schema does not match block.kind")
    payload = block.payload

    if kind == "key_value":
        _require_exact_keys(payload, ("fields",), field="block.payload")
        fields_value = payload["fields"]
        if type(fields_value) is not tuple:
            raise TypeError("block.payload.fields must be a tuple")
        if not fields_value:
            raise ValueError("block.payload.fields must not be empty")
        for index, item in enumerate(fields_value):
            _validate_field(item, field=f"block.payload.fields[{index}]")
        _require_unique(
            (item.field_id for item in fields_value),
            field="block.payload.fields.field_id",
        )
        return
    if kind == "score":
        _require_exact_keys(
            payload,
            ("score", "maximum_score", "unit"),
            field="block.payload",
        )
        score = _copy_number(payload["score"], field="block.payload.score")
        maximum = _copy_number(
            payload["maximum_score"], field="block.payload.maximum_score"
        )
        if maximum <= 0 or score < 0 or score > maximum:
            raise ValueError("block score payload is out of range")
        _validate_canonical_scalar(
            payload["score"], field="block.payload.score", allow_none=False
        )
        _require_identifier(payload["unit"], field="block.payload.unit")
        return
    if kind == "status":
        _require_exact_keys(payload, ("status_id", "label"), field="block.payload")
        _require_identifier(payload["status_id"], field="block.payload.status_id")
        _require_text(payload["label"], field="block.payload.label", required=True)
        return
    if kind == "list":
        _require_exact_keys(payload, ("items",), field="block.payload")
        if type(payload["items"]) is not tuple:
            raise TypeError("block.payload.items must be a tuple")
        _validate_frozen_value(
            payload["items"], field="block.payload.items", allow_none=False
        )
        return
    if kind == "table":
        _require_exact_keys(payload, ("columns", "rows"), field="block.payload")
        columns = payload["columns"]
        rows = payload["rows"]
        if type(columns) is not tuple or type(rows) is not tuple:
            raise TypeError("table columns and rows must be tuples")
        column_ids: list[str] = []
        for index, column in enumerate(columns):
            if type(column) is not MappingProxyType:
                raise TypeError("table columns must be mapping proxies")
            _require_exact_keys(
                column,
                ("column_id", "label", "unit"),
                field=f"block.payload.columns[{index}]",
            )
            column_ids.append(
                _require_identifier(
                    column["column_id"],
                    field=f"block.payload.columns[{index}].column_id",
                )
            )
            _require_text(
                column["label"],
                field=f"block.payload.columns[{index}].label",
                required=True,
            )
            _require_optional_identifier(
                column["unit"], field=f"block.payload.columns[{index}].unit"
            )
        _require_unique(column_ids, field="block.payload.columns.column_id")
        for row_index, row in enumerate(rows):
            if type(row) is not tuple:
                raise TypeError("table rows must be tuples")
            if len(row) != len(columns):
                raise ValueError("each table row must match the column count")
            for cell_index, cell in enumerate(row):
                _validate_canonical_scalar(
                    cell,
                    field=f"block.payload.rows[{row_index}][{cell_index}]",
                    allow_none=True,
                )
        return
    if kind == "note":
        _require_exact_keys(payload, ("text",), field="block.payload")
        _require_text(payload["text"], field="block.payload.text", required=True)
        return
    if kind == "reference":
        _require_exact_keys(payload, ("source_id",), field="block.payload")
        _require_identifier(payload["source_id"], field="block.payload.source_id")
        return


def validate_report_block(*, block: object) -> ReportBlock:
    """Strictly validate one completed immutable ReportBlock."""

    if type(block) is not ReportBlock:
        raise TypeError("block must be an exact ReportBlock")
    _require_identifier(block.block_id, field="block.block_id")
    if type(block.kind) is not str:
        raise TypeError("block.kind must be a string")
    if block.kind not in REPORT_BLOCK_KINDS:
        raise ValueError("block.kind is not supported")
    _require_text(block.title, field="block.title", required=False)
    _require_identifier(block.payload_schema, field="block.payload_schema")
    _validate_block_payload(block)
    _validate_metadata(block.metadata, field="block.metadata")
    return block


def validate_report_section(*, section: object) -> ReportSection:
    """Strictly validate one completed immutable ReportSection."""

    if type(section) is not ReportSection:
        raise TypeError("section must be an exact ReportSection")
    _require_identifier(section.section_id, field="section.section_id")
    _require_text(section.title, field="section.title", required=True)
    _require_status(section.status, field="section.status")
    if type(section.blocks) is not tuple:
        raise TypeError("section.blocks must be a tuple")
    for index, block in enumerate(section.blocks):
        if type(block) is not ReportBlock:
            raise TypeError(f"section.blocks[{index}] must be an exact ReportBlock")
        validate_report_block(block=block)
    _require_unique(
        (block.block_id for block in section.blocks), field="section.blocks.block_id"
    )
    errors = _validate_issue_collection(
        section.errors, field="section.errors", category="error"
    )
    _validate_issue_collection(
        section.warnings, field="section.warnings", category="warning"
    )
    _validate_notes(section.notes, field="section.notes")
    _validate_metadata(section.metadata, field="section.metadata")
    if section.status == "complete" and errors:
        raise ValueError("a complete section must not contain errors")
    if section.status in ("incomplete", "invalid") and not errors:
        raise ValueError("an incomplete or invalid section requires an error")
    return section


def validate_report_document(*, report: object) -> ReportDocument:
    """Strictly validate one completed immutable ReportDocument."""

    if type(report) is not ReportDocument:
        raise TypeError("report must be an exact ReportDocument")
    if report.schema_id != REPORT_SCHEMA_ID:
        raise ValueError("report.schema_id does not match REPORT_SCHEMA_ID")
    if report.schema_version != REPORT_SCHEMA_VERSION:
        raise ValueError("report.schema_version does not match REPORT_SCHEMA_VERSION")
    _require_identifier(report.report_type, field="report.report_type")
    _require_version(report.report_version, field="report.report_version")
    _require_identifier(report.report_id, field="report.report_id")
    _require_text(report.title, field="report.title", required=True)
    _require_status(report.status, field="report.status")

    if type(report.subjects) is not tuple:
        raise TypeError("report.subjects must be a tuple")
    for index, subject in enumerate(report.subjects):
        _validate_subject(subject, field=f"report.subjects[{index}]")
    _require_unique(
        (subject.subject_id for subject in report.subjects),
        field="report.subjects.subject_id",
    )
    _require_unique(
        (subject.role for subject in report.subjects), field="report.subjects.role"
    )

    if type(report.sections) is not tuple:
        raise TypeError("report.sections must be a tuple")
    for section in report.sections:
        validate_report_section(section=section)
    _require_unique(
        (section.section_id for section in report.sections),
        field="report.sections.section_id",
    )

    if type(report.sources) is not tuple:
        raise TypeError("report.sources must be a tuple")
    for index, source in enumerate(report.sources):
        _validate_source(source, field=f"report.sources[{index}]")
    _require_unique(
        (source.source_id for source in report.sources),
        field="report.sources.source_id",
    )

    _validate_metadata(report.metadata, field="report.metadata")
    errors = _validate_issue_collection(
        report.errors, field="report.errors", category="error"
    )
    _validate_issue_collection(
        report.warnings, field="report.warnings", category="warning"
    )
    _validate_notes(report.notes, field="report.notes")

    section_statuses = tuple(section.status for section in report.sections)
    if report.status == "complete":
        if errors or any(status != "complete" for status in section_statuses):
            raise ValueError("a complete report must contain only complete sections")
    elif report.status == "incomplete":
        if not errors or "invalid" in section_statuses:
            raise ValueError("an incomplete report has inconsistent errors or sections")
        if "incomplete" not in section_statuses and not any(
            issue.path for issue in errors
        ):
            raise ValueError(
                "an incomplete report must identify omitted content explicitly"
            )
    else:
        if not errors:
            raise ValueError("an invalid report requires an error")
    if "invalid" in section_statuses and report.status != "invalid":
        raise ValueError("a report containing an invalid section must be invalid")
    if "incomplete" in section_statuses and report.status == "complete":
        raise ValueError("a report containing an incomplete section cannot be complete")

    source_ids = {source.source_id for source in report.sources}
    for section in report.sections:
        for block in section.blocks:
            if (
                block.kind == "reference"
                and block.payload["source_id"] not in source_ids
            ):
                raise ValueError("a reference block must resolve to a report source")
    return report
