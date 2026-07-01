"""Reusable Kundali yoga detection framework foundations."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Callable, List, Mapping, Optional, TypedDict, Union


class YogaResult(TypedDict):
    """Generic result structure for future Kundali yoga detectors."""

    yoga_name: str
    is_present: bool
    involved_planets: list[str]
    involved_houses: list[int]
    reason: str
    strength: str


YogaDetector = Callable[
    [Mapping[str, Any]],
    Optional[Union[YogaResult, List[YogaResult]]],
]

_YOGA_DETECTORS: dict[str, YogaDetector] = {}
DEFAULT_STRENGTH_PLACEHOLDER = "not_evaluated"


def create_yoga_result(
    yoga_name: str,
    is_present: bool,
    involved_planets: list[str] | None = None,
    involved_houses: list[int] | None = None,
    reason: str = "",
    strength: str = DEFAULT_STRENGTH_PLACEHOLDER,
) -> YogaResult:
    """Create a generic yoga result without implementing yoga-specific logic."""

    return {
        "yoga_name": str(yoga_name),
        "is_present": bool(is_present),
        "involved_planets": list(involved_planets or []),
        "involved_houses": list(involved_houses or []),
        "reason": str(reason),
        "strength": str(strength),
    }


def detect_yogas(chart_data: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Run registered yoga detectors against chart data.

    With no registered detectors this returns an empty list. The framework
    deliberately does not include any actual yoga rules yet.
    """

    if not isinstance(chart_data, MappingABC):
        raise TypeError("chart_data must be a mapping")

    results: list[dict[str, Any]] = []
    for detector in _YOGA_DETECTORS.values():
        detector_result = detector(chart_data)
        if detector_result is None:
            continue

        if isinstance(detector_result, list):
            results.extend(dict(result) for result in detector_result)
            continue

        results.append(dict(detector_result))

    return results


def register_yoga_detector(name: str, function: YogaDetector) -> None:
    """Register a named Kundali yoga detector."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError("detector name must be a non-empty string")

    if not callable(function):
        raise TypeError("function must be callable")

    _YOGA_DETECTORS[name.strip()] = function


def get_registered_yoga_detectors() -> dict[str, YogaDetector]:
    """Return registered yoga detectors by name."""

    return dict(_YOGA_DETECTORS)
