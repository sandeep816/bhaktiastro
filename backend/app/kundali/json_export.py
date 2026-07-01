"""JSON export helpers for Kundali chart data."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from typing import Any

ENGINE_NAME = "kundali"
PACKAGE_NAME = "bhaktiastro"


def export_kundali_chart(
    chart_data: Mapping[str, Any],
    include_metadata: bool = True,
) -> dict[str, Any]:
    """Return a JSON-safe copy of Kundali chart data."""

    if not isinstance(chart_data, Mapping):
        raise TypeError("chart_data must be a mapping")

    exported = to_json_safe(chart_data)
    if not isinstance(exported, dict):
        raise TypeError("chart_data must export to a JSON object")

    if include_metadata:
        exported["metadata"] = _build_metadata(exported.get("metadata"))

    return exported


def dumps_kundali_chart(
    chart_data: Mapping[str, Any],
    include_metadata: bool = True,
    **json_kwargs: Any,
) -> str:
    """Serialize Kundali chart data to a JSON string."""

    return json.dumps(
        export_kundali_chart(chart_data, include_metadata=include_metadata),
        **json_kwargs,
    )


def to_json_safe(data: Any) -> Any:
    """Return data converted to JSON-serializable primitives."""

    if isinstance(data, Enum):
        return to_json_safe(data.value)

    if is_dataclass(data) and not isinstance(data, type):
        return to_json_safe(asdict(data))

    if isinstance(data, Mapping):
        return {str(key): to_json_safe(value) for key, value in data.items()}

    if isinstance(data, list):
        return [to_json_safe(value) for value in data]

    if isinstance(data, tuple):
        return [to_json_safe(value) for value in data]

    if data is None or isinstance(data, (str, bool, int)):
        return data

    if isinstance(data, float):
        if not math.isfinite(data):
            raise ValueError("float values must be finite for JSON export")
        return data

    raise TypeError(f"Unsupported JSON value type: {type(data).__name__}")


def _build_metadata(existing_metadata: Any) -> dict[str, Any]:
    """Build export metadata without requiring it in chart/API responses."""

    metadata: dict[str, Any] = {}
    if isinstance(existing_metadata, Mapping):
        metadata.update(to_json_safe(existing_metadata))

    metadata["engine"] = ENGINE_NAME

    package_version = _get_package_version()
    if package_version is not None:
        metadata["version"] = package_version

    return metadata


def _get_package_version() -> str | None:
    """Return installed package version when available."""

    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return None
