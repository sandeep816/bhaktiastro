"""Tests for Kundali yoga detection framework foundations."""

from __future__ import annotations

from typing import Any

import pytest

from backend.app.kundali import chart, yoga_framework


@pytest.fixture(autouse=True)
def clear_yoga_detectors() -> None:
    yoga_framework._YOGA_DETECTORS.clear()


def test_yoga_result_structure_is_created() -> None:
    result = yoga_framework.create_yoga_result(
        yoga_name="Example Yoga",
        is_present=False,
        involved_planets=["sun", "moon"],
        involved_houses=[1, 7],
        reason="framework placeholder",
    )

    assert result == {
        "yoga_name": "Example Yoga",
        "is_present": False,
        "involved_planets": ["sun", "moon"],
        "involved_houses": [1, 7],
        "reason": "framework placeholder",
        "strength": "not_evaluated",
    }


def test_detect_yogas_returns_a_list() -> None:
    assert isinstance(yoga_framework.detect_yogas({}), list)


def test_empty_detector_registry_returns_empty_results() -> None:
    assert yoga_framework.get_registered_yoga_detectors() == {}
    assert yoga_framework.detect_yogas({"planets": []}) == []


def test_registered_detector_is_called() -> None:
    calls: list[dict[str, Any]] = []

    def detector(chart_data: dict[str, Any]) -> yoga_framework.YogaResult:
        calls.append(dict(chart_data))
        return yoga_framework.create_yoga_result(
            yoga_name="Registered Placeholder",
            is_present=True,
            involved_planets=["mars"],
            involved_houses=[10],
            reason="detector was invoked",
        )

    yoga_framework.register_yoga_detector("registered_placeholder", detector)

    results = yoga_framework.detect_yogas({"planets": [{"planet": "mars"}]})

    assert list(yoga_framework.get_registered_yoga_detectors()) == [
        "registered_placeholder"
    ]
    assert calls == [{"planets": [{"planet": "mars"}]}]
    assert results == [
        {
            "yoga_name": "Registered Placeholder",
            "is_present": True,
            "involved_planets": ["mars"],
            "involved_houses": [10],
            "reason": "detector was invoked",
            "strength": "not_evaluated",
        }
    ]


def test_registered_detector_can_return_multiple_results() -> None:
    def detector(chart_data: dict[str, Any]) -> list[yoga_framework.YogaResult]:
        return [
            yoga_framework.create_yoga_result("First", False),
            yoga_framework.create_yoga_result("Second", False),
        ]

    yoga_framework.register_yoga_detector("multiple", detector)

    results = yoga_framework.detect_yogas({"planets": []})

    assert [result["yoga_name"] for result in results] == ["First", "Second"]


def test_invalid_detector_registration_is_handled_safely() -> None:
    with pytest.raises(ValueError, match="detector name"):
        yoga_framework.register_yoga_detector("", lambda chart_data: None)

    with pytest.raises(TypeError, match="function must be callable"):
        yoga_framework.register_yoga_detector("bad", None)  # type: ignore[arg-type]


def test_existing_kundali_chart_still_builds_without_yoga_metadata() -> None:
    result = chart.assemble_kundali_chart(
        1990,
        1,
        1,
        12,
        0,
        0,
        5.5,
        26.9124,
        75.7873,
    )

    assert set(result) == {"lagna", "planets", "houses"}
    assert yoga_framework.detect_yogas(result) == []
